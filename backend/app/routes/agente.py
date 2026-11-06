"""Endpoints aislados del agente y su sala de control visual."""
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse

from app.models.analisis import RespuestaAnalisis
from app.services.agente import (
    RespuestaAgente,
    ErrorAgenteConTraza,
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
        ejecucion = await run_in_threadpool(ejecutar_agente, solicitud)
        # Compatibilidad con los mocks previos que retornan una tupla.
        pasos, informe = ejecucion
        decisiones = getattr(ejecucion, "decisiones", [])
        estatico = getattr(ejecucion, "estatico", None)
        return RespuestaAgente(
            archivo=solicitud.archivo,
            modo="gemini_real", pasos=pasos,
            version_herramientas="2" if solicitud.version_herramientas == "2" else None,
            terminacion=getattr(ejecucion, "terminacion", None),
            max_pasos=solicitud.max_pasos,
            decisiones=decisiones,
            analisis_estatico=estatico,
            informe=RespuestaAnalisis(
                archivo=solicitud.archivo,
                estado=informe.estado_validado,
                hallazgos=informe.hallazgos,
                fuentes=informe.fuentes,
                mensaje=informe.mensaje_validado,
            ),
        )
    except LLMError as error:
        # Fallback explícito: no se atribuyen hallazgos AST a Gemini ni a RAG.
        # No ocultar una falla distinta de disponibilidad/formato del proveedor.
        if error.codigo not in (502, 503, 504):
            raise HTTPException(status_code=error.codigo, detail=str(error)) from error

        # Si el planificador llegó a seleccionar herramientas, conservar
        # sus pasos y decisiones reales. Completar únicamente los AST restantes
        # con respaldo local y no atribuirlos al modelo.
        fase = error.fase if isinstance(error, ErrorAgenteConTraza) else None
        decisiones = error.decisiones if isinstance(error, ErrorAgenteConTraza) else []
        estatico = error.estatico if isinstance(error, ErrorAgenteConTraza) else None
        pasos = list(error.pasos) if isinstance(error, ErrorAgenteConTraza) else []
        ya_ejecutadas = {paso.herramienta for paso in pasos}
        for local in await run_in_threadpool(inspeccion_local, solicitud):
            if len(pasos) >= solicitud.max_pasos:
                break
            if local.herramienta in ya_ejecutadas:
                continue
            pasos.append(local.model_copy(update={"numero": len(pasos) + 1}))
            ya_ejecutadas.add(local.herramienta)

        if fase == "informe":
            detalle = (
                "La planificación pudo ejecutarse, pero Gemini no completó el "
                "informe contextual. Se conservaron las decisiones registradas."
            )
        elif fase == "planificacion":
            detalle = (
                "Gemini no completó la planificación. Se conservaron los pasos "
                "realmente ejecutados y se completó la inspección AST local."
            )
        elif fase == "herramienta":
            detalle = (
                "Una herramienta contextual no pudo completarse. Se conservaron "
                "los pasos anteriores y el estado de error de la decisión."
            )
        else:
            detalle = "Gemini no completó la solicitud; se realizó inspección AST local."

        return RespuestaAgente(
            archivo=solicitud.archivo,
            modo="degradado",
            version_herramientas="2" if solicitud.version_herramientas == "2" else None,
            terminacion=getattr(error, "terminacion", None),
            pasos=pasos,
            max_pasos=solicitud.max_pasos,
            decisiones=decisiones,
            fase_error=fase,
            analisis_estatico=estatico,
            informe=RespuestaAnalisis(
                archivo=solicitud.archivo,
                estado="parcial",
                hallazgos=[],
                fuentes=[],
                mensaje=(
                    detalle + " No hay dictamen de IA ni referencias RAG. "
                    "Los indicadores AST no garantizan que el código sea seguro."
                ),
            ),
        )

