
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool

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
