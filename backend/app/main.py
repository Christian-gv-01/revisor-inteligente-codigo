
from fastapi import FastAPI, HTTPException, File, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse



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


app = FastAPI(
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


def construir_respuesta(
    archivo: str,
    informe: InformeModelo,
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
        mensaje=motivo,
    )


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
        informe = await run_in_threadpool(
            analizar_codigo,
            solicitud.codigo,
        )

        return construir_respuesta(
            solicitud.archivo,
            informe,
        )

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

        informe = await run_in_threadpool(
            analizar_codigo,
            codigo,
        )

        return construir_respuesta(
            nombre,
            informe,
        )

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

        for nombre, codigo in archivos:
            informe = await run_in_threadpool(
                analizar_codigo,
                codigo,
            )

            informes.append(
                construir_respuesta(
                    nombre,
                    informe,
                )
            )

        return RespuestaAnalisisZIP(
            archivo_zip=archivo.filename or "proyecto.zip",
            estado="analizado",
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

        for nombre, codigo in archivos:
            informe = await run_in_threadpool(
                analizar_codigo,
                codigo,
            )

            informes.append(
                construir_respuesta(nombre, informe)
            )

        return RespuestaAnalisisRepositorio(
            repositorio=solicitud.url,
            estado="analizado",
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


# En producción, servir el frontend compilado desde el mismo origen.
# Se registra al final para no interceptar /api, /health ni /agente/demo.
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

if os.getenv("SERVE_FRONTEND", "0") == "1":
    dist = Path(__file__).resolve().parents[3] / "frontend" / "dist"
    if not (dist / "index.html").is_file():
        raise RuntimeError("SERVE_FRONTEND=1 requiere frontend/dist/index.html")
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
