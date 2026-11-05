"""Controles HTTP de CODEGUARD; ningún dato de usuario se ejecuta.

La IP reenviada por un proxy es confiable solamente si el despliegue garantiza
que no hay un camino alternativo hacia el backend que permita falsificarla.
"""
from __future__ import annotations

import ipaddress
from threading import Lock

from starlette.requests import Request


def _ip_valida(valor: str | None) -> str | None:
    if not isinstance(valor, str):
        return None
    # Rechazar listas de proxies, puertos, espacios y encabezados inyectados.
    valor = valor.strip()
    if not valor or len(valor) > 64 or any(c in valor for c in ", \t\r\n"):
        return None
    try:
        return str(ipaddress.ip_address(valor))
    except ValueError:
        return None


def identidad_cliente(request: Request, *, confiar_railway_publico: bool = False) -> str:
    """Obtiene la IP sin confiar por defecto en cabeceras suministradas por clientes.

    El modo Railway debe habilitarse SOLO con ingreso exclusivamente por el proxy
    público de Railway, donde X-Real-IP es escrito por la plataforma. Si el
    backend también acepta solicitudes directas o privadas, mantenerlo apagado.
    """
    peer = _ip_valida(request.client.host if request.client else None)
    if confiar_railway_publico:
        forwarded = _ip_valida(request.headers.get("x-real-ip"))
        if forwarded:
            return forwarded
    return peer or "desconocido"


class ControlConcurrencia:
    """Límite de operaciones simultáneas dentro de un solo proceso."""

    def __init__(self, max_activas: int = 2):
        if max_activas < 1:
            raise ValueError("El máximo de concurrencia debe ser positivo.")
        self.max_activas = max_activas
        self._activas = 0
        self._lock = Lock()

    def adquirir(self) -> bool:
        with self._lock:
            if self._activas >= self.max_activas:
                return False
            self._activas += 1
            return True

    def liberar(self) -> None:
        with self._lock:
            if self._activas < 1:
                raise RuntimeError("No existe una operación activa que liberar.")
            self._activas -= 1

    @property
    def activas(self) -> int:
        with self._lock:
            return self._activas
