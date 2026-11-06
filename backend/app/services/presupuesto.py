"""Plazo monotónico e intentos compartidos; nunca reintenta el limitador HTTP."""
from contextlib import contextmanager
from contextvars import ContextVar
from email.utils import parsedate_to_datetime
from math import isfinite
from threading import Lock
from time import monotonic, sleep, time

import httpx
from google.genai import errors, types

from app.config import settings


class PlazoAgotado(httpx.TimeoutException):
    """El presupuesto temporal no permite publicar ni iniciar más trabajo de IA."""


class ConsumoAgotado(Exception):
    """No se permiten más intentos reales en esta solicitud."""


class Presupuesto:
    def __init__(self, segundos: float, llamadas: int):
        self.limite = monotonic() + segundos
        self.max_llamadas = llamadas
        self.llamadas = 0
        self._lock = Lock()

    def restante(self) -> float:
        restante = self.limite - monotonic()
        if restante <= 0:
            raise PlazoAgotado("Se agotó el plazo total de la solicitud.")
        return restante

    def reservar_intento(self) -> float:
        with self._lock:
            restante = self.restante()
            if self.llamadas >= self.max_llamadas:
                raise ConsumoAgotado("Se agotó el presupuesto de llamadas de la solicitud.")
            self.llamadas += 1
            return restante


_actual: ContextVar[Presupuesto | None] = ContextVar("presupuesto_codeguard", default=None)


@contextmanager
def presupuesto_solicitud(segundos: float, llamadas: int):
    token = _actual.set(Presupuesto(segundos, llamadas))
    try:
        yield _actual.get()
    finally:
        _actual.reset(token)


def tiempo_disponible(maximo: float) -> float:
    actual = _actual.get()
    return min(maximo, actual.restante()) if actual is not None else maximo


def comprobar_plazo() -> None:
    actual = _actual.get()
    if actual is not None:
        actual.restante()


def _espera_proveedor(error: errors.APIError) -> float | None:
    response = getattr(error, "response", None)
    valor = getattr(response, "headers", {}).get("Retry-After")
    if not isinstance(valor, str) or len(valor) > 128:
        return None
    try:
        segundos = float(valor)
    except ValueError:
        try:
            segundos = parsedate_to_datetime(valor).timestamp() - time()
        except (ValueError, TypeError, OverflowError):
            return None
    return segundos if isfinite(segundos) and segundos >= 0 else None


def generar_con_presupuesto(cliente, *, model, contents, config, timeout_ms: int):
    """Un solo nivel de reintentos, cada transporte ajustado al tiempo restante.

    HttpOptions aplica timeout de E/S; los chequeos antes/después evitan aceptar
    respuestas tardías. No abandona hilos ni libera concurrencia con trabajo vivo.
    """
    actual = _actual.get()
    if actual is None:
        segundos, llamadas = settings.limites_solicitud("/api/v1/analizar")
        with presupuesto_solicitud(segundos, llamadas):
            return generar_con_presupuesto(cliente, model=model, contents=contents,
                config=config, timeout_ms=timeout_ms)
    for intento in range(settings.obtener_intentos_llm()):
        restante = actual.reservar_intento()
        opciones = types.HttpOptions(timeout=max(1, int(min(timeout_ms, restante * 1000))),
            retry_options=types.HttpRetryOptions(attempts=1))
        configuracion = config.model_copy(update={"http_options": opciones})
        try:
            resultado = cliente.models.generate_content(model=model, contents=contents, config=configuracion)
            actual.restante()
            return resultado
        except errors.APIError as error:
            actual.restante()
            if error.code not in (429, 502, 503, 504) or intento + 1 >= settings.obtener_intentos_llm():
                raise
            espera = min(settings.RETRY_INITIAL_DELAY * 2 ** intento, settings.RETRY_MAX_DELAY)
            indicada = _espera_proveedor(error)
            if indicada is not None:
                espera = max(espera, indicada)
            if espera >= actual.restante():
                raise PlazoAgotado("La espera del proveedor supera el plazo restante.") from error
            sleep(espera)
            actual.restante()
