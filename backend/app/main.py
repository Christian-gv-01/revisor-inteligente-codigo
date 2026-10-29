
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.models.analisis import (
    InformeModelo,
    RespuestaAnalisis,
    RespuestaAnalisisZIP,
    SolicitudAnalisis,
)
from app.services.files import leer_python_seguro
from app.services.llm import analizar_codigo, LLMError
from app.services.zip_files import leer_zip_seguro


app = FastAPI(
    title="Revisor Inteligente de Código Seguro",
    description="API para el análisis inteligente de código Python",
    version="0.1.0",
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
