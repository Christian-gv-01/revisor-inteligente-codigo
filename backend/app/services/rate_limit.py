"""Límite de peticiones costosas, local al proceso y seguro para hilos.

Las entradas de usuarios son datos no confiables. No se confía en X-Forwarded-For.
Para varias réplicas se necesita un almacén compartido (p. ej., Redis).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import ceil
from threading import Lock
from time import monotonic
from typing import Callable


# La unidad representa el coste relativo, NO el número real de tokens de Gemini.
ENDPOINT_WEIGHTS: dict[str, int] = {
    "/api/v1/analizar": 1,
    "/api/v1/estatico/analizar": 1,
    "/api/v1/archivos": 1,
    "/api/v1/archivos/zip": 5,
    "/api/v1/repositorios/github": 5,
    "/api/v1/agente/previsualizar": 1,
    "/api/v1/agente/analizar": 3,
}


@dataclass(frozen=True)
class LimiteResultado:
    permitido: bool
    retry_after: int = 0


class LimitadorPonderado:
    """Ventana deslizante con límite global y por cliente.

    Protege la cuota global incluso si varias personas utilizan el mismo proxy.
    El bloqueo impide que dos solicitudes concurrentes reserven el mismo cupo.
    """

    def __init__(
        self,
        *,
        ventana: int = 60,
        limite_global: int = 30,
        limite_cliente: int = 10,
        reloj: Callable[[], float] = monotonic,
    ) -> None:
        if ventana < 1 or limite_global < 1 or limite_cliente < 1:
            raise ValueError("Los limites y la ventana deben ser positivos.")
        self.ventana = ventana
        self.limite_global = limite_global
        self.limite_cliente = limite_cliente
        self._reloj = reloj
        self._lock = Lock()
        self._global: deque[tuple[float, int]] = deque()
        self._clientes: dict[str, deque[tuple[float, int]]] = {}

    def comprobar(self, cliente: str, peso: int) -> LimiteResultado:
        if peso < 1:
            raise ValueError("El peso debe ser positivo.")
        identidad = cliente or "desconocido"
        with self._lock:
            ahora = self._reloj()
            corte = ahora - self.ventana
            while self._global and self._global[0][0] <= corte:
                self._global.popleft()

            # Se descartan clientes inactivos en cada consulta para limitar memoria.
            for clave, eventos in list(self._clientes.items()):
                while eventos and eventos[0][0] <= corte:
                    eventos.popleft()
                if not eventos:
                    del self._clientes[clave]

            eventos_cliente = self._clientes.get(identidad)
            suma_global = sum(unidades for _, unidades in self._global)
            suma_cliente = sum(unidades for _, unidades in (eventos_cliente or ()))
            sobre_global = suma_global + peso > self.limite_global
            sobre_cliente = suma_cliente + peso > self.limite_cliente
            if sobre_global or sobre_cliente:
                tiempos = []
                if sobre_global:
                    tiempos.append(self._segundos_hasta_liberar(
                        self._global, suma_global + peso - self.limite_global, ahora
                    ))
                if sobre_cliente and eventos_cliente:
                    tiempos.append(self._segundos_hasta_liberar(
                        eventos_cliente, suma_cliente + peso - self.limite_cliente, ahora
                    ))
                return LimiteResultado(False, max(tiempos, default=self.ventana))

            self._global.append((ahora, peso))
            if eventos_cliente is None:
                eventos_cliente = deque()
                self._clientes[identidad] = eventos_cliente
            eventos_cliente.append((ahora, peso))
            return LimiteResultado(True)

    def _segundos_hasta_liberar(
        self, eventos: deque[tuple[float, int]], faltan: int, ahora: float
    ) -> int:
        acumulado = 0
        for instante, peso in eventos:
            acumulado += peso
            if acumulado >= faltan:
                return max(1, ceil(instante + self.ventana - ahora))
        return self.ventana
