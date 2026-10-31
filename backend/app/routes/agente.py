"""Endpoints aislados del agente y su sala de control visual."""
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse

from app.models.analisis import RespuestaAnalisis
from app.services.agente import (
    RespuestaAgente,
    SolicitudAgente,
    ejecutar_agente,
    inspeccion_local,
)
from app.services.llm import LLMError

router = APIRouter(tags=["CODEGUARD Agent Lab"])

@router.get("/agente/demo", response_class=HTMLResponse, include_in_schema=False)
def agente_demo():
    ruta = Path(__file__).resolve().parents[1] / "static" / "agent_lab.html"
    return HTMLResponse(ruta.read_text(encoding="utf-8"))

@router.post("/api/v1/agente/previsualizar", response_model=RespuestaAgente)
async def previsualizar_agente(solicitud: SolicitudAgente):
    """Solo herramientas AST: verificable sin clave ni consumo de Gemini."""
    if not solicitud.codigo.strip() or "\x00" in solicitud.codigo:
        raise HTTPException(status_code=422, detail="Código Python inválido.")
    pasos = await run_in_threadpool(inspeccion_local, solicitud)
    return RespuestaAgente(
        archivo=solicitud.archivo,
        modo="inspeccion_local",
        pasos=pasos,
        max_pasos=solicitud.max_pasos,
        informe=RespuestaAnalisis(
            archivo=solicitud.archivo,
            estado="abstenido",
            hallazgos=[], fuentes=[],
            mensaje="Inspección AST completada. No se consultó Gemini; los indicadores no son un dictamen de seguridad.",
        ),
    )

@router.post("/api/v1/agente/analizar", response_model=RespuestaAgente)
async def analizar_con_agente(solicitud: SolicitudAgente):
    """Gemini planifica las herramientas; RAG + Gemini generan el informe."""
    if not solicitud.codigo.strip() or "\x00" in solicitud.codigo:
        raise HTTPException(status_code=422, detail="Código Python inválido.")
    try:
        pasos, informe = await run_in_threadpool(ejecutar_agente, solicitud)
        return RespuestaAgente(
            archivo=solicitud.archivo,
            modo="gemini_real", pasos=pasos,
            max_pasos=solicitud.max_pasos,
            informe=RespuestaAnalisis(
                archivo=solicitud.archivo,
                estado="abstenido" if informe.motivo_abstencion else "analizado",
                hallazgos=informe.hallazgos,
                fuentes=informe.fuentes,
                mensaje=informe.motivo_abstencion,
            ),
        )
    except LLMError as error:
        raise HTTPException(status_code=error.codigo, detail=str(error)) from error
