"""Endpoints del flujo de corrección con confirmación humana."""

import hashlib
import re
import secrets
from fastapi import APIRouter, HTTPException, Path, Request, Response
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
from app.config import settings


def sesion(request: Request) -> str | None:
    valor = request.cookies.get(settings.COOKIE_CORRECCIONES, "")
    return valor if re.fullmatch(r"[A-Za-z0-9_-]{43}", valor) else None


def hash_sesion(valor: str) -> str:
    return hashlib.sha256(valor.encode("ascii")).hexdigest()


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
    request: Request,
    response: Response,
) -> RespuestaPrevisualizacion:
    """Genera una propuesta temporal; no escribe ni ejecuta archivos."""
    try:
        identidad = sesion(request) or secrets.token_urlsafe(32)
        resultado = await run_in_threadpool(crear_previsualizacion, solicitud, hash_sesion(identidad))
        response.set_cookie(settings.COOKIE_CORRECCIONES, identidad, httponly=True,
                            secure=settings.cookie_segura(), samesite="strict",
                            path="/api/v1/correcciones", max_age=settings.RETENCION_CORRECCION)
        response.headers["Cache-Control"] = "no-store"
        return RespuestaPrevisualizacion.model_validate(resultado)
    except CorreccionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.mensaje,
        ) from exc


@router.post("/{propuesta_id}/decision", status_code=200)
async def decidir_correccion(
    solicitud: SolicitudDecision,
    request: Request,
    response: Response,
    propuesta_id: str = Path(
        min_length=6,
        max_length=128,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
) -> dict:
    """Registra aprobación o rechazo de una propuesta inmutable."""
    try:
        identidad = sesion(request)
        if not identidad:
            raise HTTPException(status_code=404, detail="La propuesta no existe.")
        response.headers["Cache-Control"] = "no-store"
        return await run_in_threadpool(
            decidir_propuesta,
            propuesta_id,
            solicitud,
            hash_sesion(identidad),
        )
    except CorreccionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.mensaje,
        ) from exc

