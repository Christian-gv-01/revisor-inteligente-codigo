from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.concurrency import run_in_threadpool
from app.services.files import leer_python_seguro
from app.models.analisis import RespuestaAnalisisZIP
from app.services.zip_files import leer_zip_seguro

from app.models.analisis import (
    SolicitudAnalisis,
    RespuestaAnalisis,
)
from app.services.llm import analizar_codigo, LLMError


app = FastAPI(
    title="Revisor Inteligente de Código Seguro",
    description="API para el análisis inteligente de código Python",
    version="0.1.0",
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
    Recibe un fragmento Python y devuelve
    hallazgos generados por inteligencia artificial.

    El código recibido nunca se ejecuta.
    """

    try:
        informe = await run_in_threadpool(
            analizar_codigo,
            solicitud.codigo,
        )

        return RespuestaAnalisis(
            archivo=solicitud.archivo,
            estado="analizado",
            hallazgos=informe.hallazgos,
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
    Recibe un archivo Python, valida su contenido
    y lo analiza sin ejecutar el código recibido.
    """

    try:
        nombre, codigo = await leer_python_seguro(archivo)

        informe = await run_in_threadpool(
            analizar_codigo,
            codigo,
        )

        return RespuestaAnalisis(
            archivo=nombre,
            estado="analizado",
            hallazgos=informe.hallazgos,
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
    No ejecuta ni importa código del usuario.
    """

    try:
        archivos = await leer_zip_seguro(archivo)

        # Presupuesto inicial: máximo cinco llamadas
        # al modelo por solicitud ZIP.
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
                RespuestaAnalisis(
                    archivo=nombre,
                    estado="analizado",
                    hallazgos=informe.hallazgos,
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

