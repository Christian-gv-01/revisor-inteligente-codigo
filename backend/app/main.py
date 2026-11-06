
from fastapi import FastAPI, HTTPException, File, Request, UploadFile
import os
from app.config import settings

from app.services.rate_limit import ENDPOINT_WEIGHTS, LimitadorPonderado
from app.services.http_security import ControlConcurrencia, identidad_cliente
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import asyncio
import logging
from contextlib import asynccontextmanager, suppress


@asynccontextmanager
async def ciclo_vida(_app):
    async def purgar():
        from app.services.correcciones import limpiar_caducadas
        while True:
            try:
                await run_in_threadpool(limpiar_caducadas)
            except Exception as exc:
                logging.getLogger(__name__).warning("correction_cleanup_failed tipo=%s", type(exc).__name__)
            await asyncio.sleep(60)
    tarea = asyncio.create_task(purgar())
    try:
        yield
    finally:
        tarea.cancel()
        with suppress(asyncio.CancelledError):
            await tarea



from app.models.analisis import (
    InformeModelo,
    RespuestaAnalisis,
    RespuestaAnalisisZIP,
    RespuestaAnalisisRepositorio,
    SolicitudAnalisis,
    SolicitudGitHub,
)

from app.services.github_repos import obtener_archivos_python_github
from app.services.files import leer_python_seguro
from app.services.llm import analizar_codigo, LLMError
from app.services.zip_files import leer_zip_seguro
from app.services.static_analysis import (
    analizar_estatico,
    EntradaEstaticaInvalida,
    ResultadoEstatico,
)


app = FastAPI(
    lifespan=ciclo_vida,
    title="Revisor Inteligente de Código Seguro",
    description="API para el análisis inteligente de código Python",
    version="0.1.0",
)


def errores_validacion_publicos(error: RequestValidationError) -> list[dict]:
    """Conserva la utilidad del 422 sin reflejar código o secretos recibidos."""

    return [
        {
            "type": detalle.get("type", "validation_error"),
            "loc": list(detalle.get("loc", ())),
            "msg": detalle.get("msg", "Entrada inválida."),
        }
        for detalle in error.errors()
    ]


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    _request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    """Evita que FastAPI devuelva el valor completo de entradas sensibles."""

    return JSONResponse(
        status_code=422,
        content={"detail": errores_validacion_publicos(error)},
    )


# Dos barreras complementarias: presupuesto por minuto y concurrencia.
# Ambas son por proceso; en varias réplicas se necesita un almacén compartido.
limitador_peticiones = LimitadorPonderado(
    ventana=settings.VENTANA_PETICIONES,
    limite_global=settings.PRESUPUESTO_GLOBAL,
    limite_cliente=settings.PRESUPUESTO_CLIENTE,
)
control_concurrencia = ControlConcurrencia(max_activas=settings.MAX_CONCURRENCIA)


@app.middleware("http")
async def proteger_analisis(request: Request, call_next):
    es_costosa = (
        request.method == "POST"
        and (request.url.path in ENDPOINT_WEIGHTS or
             (request.url.path.startswith("/api/v1/correcciones/") and request.url.path.endswith("/decision")))
    )
    if not es_costosa:
        return await call_next(request)

    if settings.bandera("RATE_LIMIT_ENABLED"):
        # No habilitar sin garantizar que no existen rutas privadas/directas
        # hacia este servicio que puedan falsificar X-Real-IP.
        confiar_proxy_publico = (
            settings.bandera("TRUST_RAILWAY_REAL_IP")
        )
        identidad = identidad_cliente(
            request, confiar_railway_publico=confiar_proxy_publico
        )
        resultado = limitador_peticiones.comprobar(
            identidad, ENDPOINT_WEIGHTS.get(request.url.path, 1)
        )
        if not resultado.permitido:
            return JSONResponse(
                status_code=429,
                content={"detail": "Demasiadas solicitudes. Reintenta más tarde."},
                headers={
                    "Retry-After": str(resultado.retry_after),
                    "Cache-Control": "no-store",
                },
            )

    if not settings.bandera("CONCURRENCY_LIMIT_ENABLED"):
        return await call_next(request)

    if not control_concurrencia.adquirir():
        return JSONResponse(
            status_code=503,
            content={"detail": "Servicio ocupado. Reintenta más tarde."},
            headers={"Retry-After": "3", "Cache-Control": "no-store"},
        )

    try:
        return await call_next(request)
    finally:
        control_concurrencia.liberar()


async def _analisis_estatico_si_habilitado(
    codigo: str, archivo: str
) -> ResultadoEstatico | None:
    if not settings.analisis_estatico_habilitado():
        return None
    try:
        return await run_in_threadpool(analizar_estatico, codigo, archivo)
    except EntradaEstaticaInvalida:
        # Los contratos de entrada del backend siguen siendo obligatorios.
        return None


@app.post("/api/v1/estatico/analizar", response_model=ResultadoEstatico)
async def analizar_solo_estatico(solicitud: SolicitudAnalisis):
    """Análisis autónomo sin consumo de Gemini ni recuperación RAG."""
    try:
        return await run_in_threadpool(
            analizar_estatico, solicitud.codigo, solicitud.archivo
        )
    except EntradaEstaticaInvalida as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


def construir_respuesta(
    archivo: str,
    informe: InformeModelo,
    analisis_estatico: ResultadoEstatico | None = None,
) -> RespuestaAnalisis:
    """
    Convierte el informe interno en una respuesta de la API.

    Conserva el estado de abstención, el motivo y las fuentes.
    """

    motivo = informe.motivo_abstencion

    return RespuestaAnalisis(
        archivo=archivo,
        estado="abstenido" if motivo else "analizado",
        hallazgos=informe.hallazgos,
        fuentes=informe.fuentes,
        analisis_estatico=analisis_estatico,
        mensaje=motivo,
    )


async def analizar_con_respaldo(
    codigo: str, archivo: str, *, omitir_ia: bool = False
) -> RespuestaAnalisis:
    """Analiza primero de forma estática; la IA es opcional si no responde.

    Cuando el proveedor falla no se inventan hallazgos RAG ni citas.
    Si tampoco queda un analizador estático útil, se conserva el error HTTP.
    """
    estatico = await _analisis_estatico_si_habilitado(codigo, archivo)
    if omitir_ia:
        if estatico is None or estatico.estado == "no_disponible":
            raise LLMError("El análisis no está disponible temporalmente.", 503)
        return RespuestaAnalisis(
            archivo=archivo,
            estado="parcial",
            hallazgos=[],
            fuentes=[],
            analisis_estatico=estatico,
            mensaje="Gemini no disponible temporalmente; se muestran únicamente resultados estáticos.",
        )

    try:
        informe = await run_in_threadpool(analizar_codigo, codigo)
    except LLMError as error:
        if error.codigo not in (502, 503, 504):
            raise
        if estatico is None or estatico.estado == "no_disponible":
            raise
        return RespuestaAnalisis(
            archivo=archivo,
            estado="parcial",
            hallazgos=[],
            fuentes=[],
            analisis_estatico=estatico,
            mensaje="Gemini no completó el análisis; solo hay observaciones estáticas. No se realizó una revisión contextual con citas.",
        )
    return construir_respuesta(archivo, informe, estatico)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "revisor-inteligente-codigo",
        "version": "0.1.0",
    }


@app.post(
    "/api/v1/analizar",
    response_model=RespuestaAnalisis,
)
async def analizar(solicitud: SolicitudAnalisis):
    """
    Analiza un fragmento Python sin ejecutar su contenido.
    """

    try:
        return await analizar_con_respaldo(solicitud.codigo, solicitud.archivo)

    except LLMError as error:
        raise HTTPException(
            status_code=error.codigo,
            detail=str(error),
        ) from error


@app.post(
    "/api/v1/archivos",
    response_model=RespuestaAnalisis,
)
async def analizar_archivo(
    archivo: UploadFile = File(...),
):
    """
    Valida y analiza un archivo Python sin ejecutarlo.
    """

    try:
        nombre, codigo = await leer_python_seguro(archivo)

        return await analizar_con_respaldo(codigo, nombre)

    except LLMError as error:
        raise HTTPException(
            status_code=error.codigo,
            detail=str(error),
        ) from error

    finally:
        await archivo.close()


@app.post(
    "/api/v1/archivos/zip",
    response_model=RespuestaAnalisisZIP,
)
async def analizar_zip(
    archivo: UploadFile = File(...),
):
    """
    Analiza archivos Python contenidos en un ZIP.
    Nunca ejecuta ni importa el código recibido.
    """

    try:
        archivos = await leer_zip_seguro(archivo)

        # Limitar el consumo del proveedor de IA.
        if len(archivos) > 5:
            raise HTTPException(
                status_code=413,
                detail="Máximo 5 archivos Python por análisis ZIP.",
            )

        informes = []
        proveedor_no_disponible = False

        for nombre, codigo in archivos:
            resultado = await analizar_con_respaldo(
                codigo, nombre, omitir_ia=proveedor_no_disponible
            )
            informes.append(resultado)
            # Evitar repetir la misma espera de Gemini por cada archivo ZIP
            # después de comprobar que el proveedor falla en esta petición.
            if resultado.estado == "parcial":
                proveedor_no_disponible = True

        return RespuestaAnalisisZIP(
            archivo_zip=archivo.filename or "proyecto.zip",
            estado="parcial" if proveedor_no_disponible else "analizado",
            total_archivos=len(informes),
            informes=informes,
        )

    except LLMError as error:
        raise HTTPException(
            status_code=error.codigo,
            detail=str(error),
        ) from error

    finally:
        await archivo.close()

# =========================================================
# ANALISIS DE REPOSITORIOS PUBLICOS DE GITHUB
# =========================================================

@app.post(
    "/api/v1/repositorios/github",
    response_model=RespuestaAnalisisRepositorio,
)
async def analizar_repositorio_github(
    solicitud: SolicitudGitHub,
):
    """
    Analiza archivos Python de un repositorio público de GitHub.

    La descarga y validación se delegan al servicio GitHub.
    El código recuperado nunca se ejecuta ni se importa.
    """

    try:
        archivos = await run_in_threadpool(
            obtener_archivos_python_github,
            solicitud.url,
        )

        informes = []
        proveedor_no_disponible = False

        for nombre, codigo in archivos:
            resultado = await analizar_con_respaldo(
                codigo, nombre, omitir_ia=proveedor_no_disponible
            )
            informes.append(resultado)
            if resultado.estado == "parcial":
                proveedor_no_disponible = True

        return RespuestaAnalisisRepositorio(
            repositorio=solicitud.url,
            estado="parcial" if proveedor_no_disponible else "analizado",
            total_archivos=len(informes),
            informes=informes,
        )

    except LLMError as error:
        raise HTTPException(
            status_code=error.codigo,
            detail=str(error),
        ) from error


# CODEGUARD AGENT LAB: rutas independientes
from app.routes.agente import router as agente_router
app.include_router(agente_router)
from app.routes.correcciones import router as correcciones_router
app.include_router(correcciones_router)


# En producción, servir el frontend compilado desde el mismo origen.
# Se registra al final para no interceptar /api, /health ni /agente/demo.
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

if settings.bandera("SERVE_FRONTEND"):
    dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if not (dist / "index.html").is_file():
        raise RuntimeError("SERVE_FRONTEND=1 requiere frontend/dist/index.html")
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
