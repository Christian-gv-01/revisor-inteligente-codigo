"""Previsualización de consumo y decisión vinculada a una instantánea inmutable."""
import hashlib
import re
import secrets

from fastapi import APIRouter, File, HTTPException, Request, Response, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator
from typing import Literal

from app.config import settings
from app.models.analisis import SolicitudGitHub
from app.services.github_repos import obtener_archivos_python_github
from app.services.zip_files import leer_zip_seguro, MAX_ZIP_BYTES
from app.services import proyectos as servicio
from app.services.presupuesto import presupuesto_solicitud, tiempo_disponible, comprobar_plazo, PlazoAgotado

router = APIRouter(prefix="/api/v1/proyectos", tags=["Presupuesto de proyectos"])


class DecisionPresupuesto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["aprobar", "rechazar"]
    confirmar: StrictBool
    sha256_manifiesto: str = Field(pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def consentimiento(self):
        if self.confirmar != (self.decision == "aprobar"):
            raise ValueError("La aprobación requiere confirmar=true; el rechazo, confirmar=false.")
        return self


def habilitado():
    if not settings.bandera("PROJECT_BUDGET_ENABLED"):
        raise HTTPException(404, "El flujo de presupuesto no está habilitado.")


def sesion(request):
    valor = request.cookies.get(servicio.COOKIE, "")
    return valor if re.fullmatch(r"[A-Za-z0-9_-]{43}", valor) else None


def preparar_sesion(request, response):
    valor = sesion(request) or secrets.token_urlsafe(32)
    response.set_cookie(servicio.COOKIE, valor, httponly=True, secure=settings.cookie_segura(),
                        samesite="strict", path="/api/v1/proyectos", max_age=600)
    response.headers["Cache-Control"] = "no-store"
    return servicio.huella(valor)


@router.post("/previsualizar/zip")
async def previsualizar_zip(request: Request, response: Response, archivo: UploadFile = File(...)):
    try:
        habilitado()
        if not archivo.filename or len(archivo.filename) > 255 or "\0" in archivo.filename:
            raise HTTPException(400, "Nombre ZIP inválido.")
        archivos = await leer_zip_seguro(archivo)
        await archivo.seek(0)
        entrada = await archivo.read(MAX_ZIP_BYTES + 1)
        return await run_in_threadpool(servicio.crear, "zip", archivo.filename,
            hashlib.sha256(entrada).hexdigest(), archivos, preparar_sesion(request, response))
    except servicio.ProyectoError as error:
        raise HTTPException(error.codigo, str(error)) from error
    finally:
        await archivo.close()


@router.post("/previsualizar/github")
async def previsualizar_github(solicitud: SolicitudGitHub, request: Request, response: Response):
    habilitado()
    origen = solicitud.url.strip()
    archivos = await run_in_threadpool(obtener_archivos_python_github, origen)
    try:
        return await run_in_threadpool(servicio.crear, "github", origen, servicio.huella(origen),
                                       archivos, preparar_sesion(request, response))
    except servicio.ProyectoError as error:
        raise HTTPException(error.codigo, str(error)) from error


@router.post("/{presupuesto_id}/decision")
async def decision(presupuesto_id: str, solicitud: DecisionPresupuesto, request: Request, response: Response):
    habilitado()
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", presupuesto_id) or not sesion(request):
        raise HTTPException(404, "El presupuesto no existe.")
    propietario = servicio.huella(sesion(request))
    response.headers["Cache-Control"] = "no-store"
    consumido = False
    try:
        datos = await run_in_threadpool(servicio.decidir, presupuesto_id, propietario,
                                        solicitud.sha256_manifiesto, solicitud.decision)
        if "snapshot" not in datos:
            return datos
        consumido = True
        from app.main import analizar_con_respaldo
        manifiesto = datos["manifiesto"]
        presupuesto = manifiesto["presupuesto"]
        informes = []
        sin_proveedor = False
        with presupuesto_solicitud(tiempo_disponible(presupuesto["plazo_cooperativo_segundos"]), presupuesto["max_intentos_proveedor"]):
            for nombre, codigo in datos["snapshot"]:
                comprobar_plazo()
                informe = await analizar_con_respaldo(codigo, nombre, omitir_ia=sin_proveedor)
                informes.append(informe.model_dump(mode="json"))
                if informe.estado == "parcial" and not informe.fuentes:
                    sin_proveedor = True
            comprobar_plazo()
        clave = "archivo_zip" if manifiesto["tipo"] == "zip" else "repositorio"
        resultado = {"version": "1", "presupuesto_id": presupuesto_id,
            "sha256_manifiesto": solicitud.sha256_manifiesto, "estado": "finalizado",
            "resultado": {clave: manifiesto["origen"], "total_archivos": len(informes),
                "estado": "parcial" if any(i["estado"] == "parcial" for i in informes) else "analizado", "informes": informes}}
        await run_in_threadpool(servicio.finalizar, presupuesto_id, propietario, resultado)
        consumido = False
        return resultado
    except servicio.ProyectoError as error:
        raise HTTPException(error.codigo, str(error)) from error
    except PlazoAgotado as error:
        raise HTTPException(504, "Se agotó el plazo aprobado del proyecto.") from error
    except Exception as error:
        from app.services.llm import LLMError
        if isinstance(error, LLMError):
            raise HTTPException(error.codigo, str(error)) from error
        raise
    finally:
        if consumido:
            await run_in_threadpool(servicio.fallar, presupuesto_id, propietario)
