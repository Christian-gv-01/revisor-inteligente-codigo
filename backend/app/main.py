
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.config import analisis_estatico_habilitado

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
from app.routes.agente import router as agente_router
from app.routes.correcciones import router as correcciones_router


app = FastAPI(
    title="Revisor Inteligente de Código Seguro",
    description="API para el análisis inteligente de código Python",
    version="0.1.0",
)


async def ejecutar_analisis_estatico(
    codigo: str,
    archivo: str,
) -> ResultadoEstatico | None:
    """Ejecuta Ruff y Bandit sin ejecutar el código recibido."""

    if not analisis_estatico_habilitado():
        return None

    try:
        return await run_in_threadpool(
            analizar_estatico,
            codigo,
            archivo,
        )

    except EntradaEstaticaInvalida as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error



def resultado_estatico_utilizable(
    resultado: ResultadoEstatico | None,
) -> bool:
    """
    Determina si existe evidencia estática suficiente
    para construir una respuesta parcial cuando Gemini falla.

    Solo se considera utilizable si:
    - El análisis estático terminó completa o parcialmente.
    - Existe al menos un hallazgo real.
    """

    return (
        resultado is not None
        and resultado.estado in {"completo", "parcial"}
        and bool(resultado.hallazgos)
    )


# =========================================================
# CONSTRUCCION DE RESPUESTAS
# =========================================================

def construir_respuesta(
    archivo: str,
    informe: InformeModelo,
    analisis_estatico: ResultadoEstatico | None = None,
) -> RespuestaAnalisis:
    """
    Convierte el informe interno en una respuesta de la API.

    Conserva hallazgos, fuentes, abstenciones y evidencia estática.
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


def construir_respuesta_parcial(
    archivo: str,
    resultado_estatico: ResultadoEstatico | None,
    mensaje: str,
) -> RespuestaAnalisis:
    """
    Conserva la evidencia estática cuando Gemini no está disponible.
    """

    return RespuestaAnalisis(
        archivo=archivo,
        estado="parcial",
        hallazgos=[],
        fuentes=[],
        analisis_estatico=resultado_estatico,
        mensaje=mensaje,
    )


def mensaje_error_gemini(error: LLMError) -> str:
    """Construye un mensaje para los informes parciales."""

    return (
        "Gemini no estuvo disponible para completar el análisis "
        f"contextual (HTTP {error.codigo}). "
        "Se conserva la evidencia estática disponible."
    )


# =========================================================
# PROCESAMIENTO COMUN DE ARCHIVOS
# =========================================================

async def procesar_archivo(
    archivo: str,
    codigo: str,
    intentar_gemini: bool = True,
    mensaje_sin_gemini: str | None = None,
) -> tuple[RespuestaAnalisis, LLMError | None]:
    """
    Ejecuta análisis estático y contextual.

    Si Gemini falla y existe evidencia estática utilizable,
    devuelve un informe parcial en lugar de perder los hallazgos.
    """

    resultado_estatico = await ejecutar_analisis_estatico(
        codigo,
        archivo,
    )

    # En lotes ZIP/GitHub se pueden detener nuevas llamadas a Gemini.
    if not intentar_gemini:
        return (
            construir_respuesta_parcial(
                archivo,
                resultado_estatico,
                mensaje_sin_gemini
                or "Se omitió el análisis contextual con Gemini.",
            ),
            None,
        )

    try:
        informe = await run_in_threadpool(
            analizar_codigo,
            codigo,
        )

    except LLMError as error:

        # Sin evidencia estática utilizable no se debe simular
        # un análisis exitoso.
        if not resultado_estatico_utilizable(resultado_estatico):
            raise

        respuesta = construir_respuesta_parcial(
            archivo,
            resultado_estatico,
            mensaje_error_gemini(error),
        )

        return respuesta, error

    return (
        construir_respuesta(
            archivo,
            informe,
            resultado_estatico,
        ),
        None,
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "revisor-inteligente-codigo",
        "version": "0.1.0",
    }


# =========================================================
# ENDPOINT INDEPENDIENTE DE RUFF Y BANDIT
# =========================================================

@app.post(
    "/api/v1/estatico/analizar",
    response_model=ResultadoEstatico,
)
async def analizar_estatico_endpoint(
    solicitud: SolicitudAnalisis,
):
    """
    Ejecuta Ruff y Bandit independientemente de Gemini.
    """

    if not analisis_estatico_habilitado():
        raise HTTPException(
            status_code=503,
            detail="El análisis estático está deshabilitado.",
        )

    resultado = await ejecutar_analisis_estatico(
        solicitud.codigo,
        solicitud.archivo,
    )

    if resultado is None:
        raise HTTPException(
            status_code=503,
            detail="El análisis estático no está disponible.",
        )

    return resultado


# =========================================================
# ANALISIS DE CODIGO DIRECTO
# =========================================================

@app.post(
    "/api/v1/analizar",
    response_model=RespuestaAnalisis,
)
async def analizar(solicitud: SolicitudAnalisis):
    """Analiza un fragmento Python sin ejecutar su contenido."""

    try:
        respuesta, _ = await procesar_archivo(
            solicitud.archivo,
            solicitud.codigo,
        )

        return respuesta

    except LLMError as error:
        raise HTTPException(
            status_code=error.codigo,
            detail=str(error),
        ) from error


# =========================================================
# ANALISIS DE ARCHIVOS PYTHON
# =========================================================

@app.post(
    "/api/v1/archivos",
    response_model=RespuestaAnalisis,
)
async def analizar_archivo(
    archivo: UploadFile = File(...),
):
    """Valida y analiza un archivo Python sin ejecutarlo."""

    try:
        nombre, codigo = await leer_python_seguro(archivo)

        respuesta, _ = await procesar_archivo(
            nombre,
            codigo,
        )

        return respuesta

    except LLMError as error:
        raise HTTPException(
            status_code=error.codigo,
            detail=str(error),
        ) from error

    finally:
        await archivo.close()


# =========================================================
# ANALISIS DE ARCHIVOS ZIP
# =========================================================

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
    Conserva evidencia estática si Gemini falla.
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
        gemini_disponible = True
        motivo_parada = None

        for nombre, codigo in archivos:

            respuesta, error = await procesar_archivo(
                nombre,
                codigo,
                intentar_gemini=gemini_disponible,
                mensaje_sin_gemini=motivo_parada,
            )

            informes.append(respuesta)

            # Si Gemini falla, no seguimos consumiendo llamadas.
            if error is not None:
                gemini_disponible = False
                motivo_parada = mensaje_error_gemini(error)

        estado = (
            "parcial"
            if any(
                informe.estado == "parcial"
                for informe in informes
            )
            else "analizado"
        )

        return RespuestaAnalisisZIP(
            archivo_zip=archivo.filename or "proyecto.zip",
            estado=estado,
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
        gemini_disponible = True
        motivo_parada = None

        for nombre, codigo in archivos:

            respuesta, error = await procesar_archivo(
                nombre,
                codigo,
                intentar_gemini=gemini_disponible,
                mensaje_sin_gemini=motivo_parada,
            )

            informes.append(respuesta)

            if error is not None:
                gemini_disponible = False
                motivo_parada = mensaje_error_gemini(error)

        estado = (
            "parcial"
            if any(
                informe.estado == "parcial"
                for informe in informes
            )
            else "analizado"
        )

        return RespuestaAnalisisRepositorio(
            repositorio=solicitud.url,
            estado=estado,
            total_archivos=len(informes),
            informes=informes,
        )

    except LLMError as error:
        raise HTTPException(
            status_code=error.codigo,
            detail=str(error),
        ) from error


# =========================================================
# CODEGUARD AGENT LAB: RUTAS INDEPENDIENTES
# =========================================================

app.include_router(agente_router)
app.include_router(correcciones_router)
