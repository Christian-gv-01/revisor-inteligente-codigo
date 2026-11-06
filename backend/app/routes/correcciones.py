"""Endpoints del flujo de corrección con confirmación humana."""

from fastapi import APIRouter, HTTPException, Path
from fastapi.concurrency import run_in_threadpool

from app.models.correcciones import (
    RespuestaPrevisualizacion,
    SolicitudDecision,
    SolicitudPrevisualizacion,
)
from app.services.correcciones import (
    CorreccionError,
    crear_previsualizacion,
    decidir_propuesta,
)


router = APIRouter(
    prefix="/api/v1/correcciones",
    tags=["Correcciones con confirmación humana"],
)


@router.post(
    "/previsualizar",
    response_model=RespuestaPrevisualizacion,
    status_code=200,
)
async def previsualizar_correccion(
    solicitud: SolicitudPrevisualizacion,
) -> RespuestaPrevisualizacion:
    """Genera una propuesta temporal; no escribe ni ejecuta archivos."""
    try:
        resultado = await run_in_threadpool(crear_previsualizacion, solicitud)
        return RespuestaPrevisualizacion.model_validate(resultado)
    except CorreccionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.mensaje,
        ) from exc


@router.post("/{propuesta_id}/decision", status_code=200)
async def decidir_correccion(
    solicitud: SolicitudDecision,
    propuesta_id: str = Path(
        min_length=6,
        max_length=128,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
) -> dict:
    """Registra aprobación o rechazo de una propuesta inmutable."""
    try:
        return await run_in_threadpool(
            decidir_propuesta,
            propuesta_id,
            solicitud,
        )
    except CorreccionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.mensaje,
        ) from exc
