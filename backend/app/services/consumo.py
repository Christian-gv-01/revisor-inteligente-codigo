"""Contadores por solicitud: uso reportado por el SDK, nunca una estimación."""
from threading import Lock

CABECERA_CONSUMO = "X-Codeguard-Consumo-IA"
_CAMPOS = {
    "tokens_entrada": "prompt_token_count",
    "tokens_salida": "candidates_token_count",
    "tokens_totales": "total_token_count",
}


class ConsumoIA:
    def __init__(self):
        self._lock = Lock()
        self.intentos = 0
        self.respuestas = 0
        self._sumas = {campo: 0 for campo in _CAMPOS}
        self._conocidos = {campo: True for campo in _CAMPOS}

    def iniciar_intento(self):
        with self._lock:
            self.intentos += 1

    def registrar_respuesta(self, respuesta):
        # Solo atributos numéricos del SDK. No guardar prompts, textos, claves,
        # mensajes del proveedor ni completar contadores por diferencia.
        uso = getattr(respuesta, "usage_metadata", None)
        with self._lock:
            self.respuestas += 1
            for campo, atributo in _CAMPOS.items():
                valor = uso.get(atributo) if isinstance(uso, dict) else getattr(uso, atributo, None)
                if type(valor) is int and 0 <= valor <= 1_000_000_000:
                    self._sumas[campo] += valor
                else:
                    self._conocidos[campo] = False

    def publico(self):
        with self._lock:
            sin_respuesta = self.intentos - self.respuestas
            valores = {campo: total if self._conocidos[campo] and not sin_respuesta else None
                       for campo, total in self._sumas.items()}
            return {"version": 1, "intentos": self.intentos, "respuestas": self.respuestas,
                    **valores, "uso_completo": all(v is not None for v in valores.values())}
