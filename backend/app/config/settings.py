"""Configuración centralizada de CODEGUARD.

Todas las lecturas de variables de entorno de la aplicación se concentran
 aquí para mantener valores predeterminados y validaciones consistentes.
"""

import math
import os
from pathlib import Path


MODELO_GEMINI_DEFAULT = "gemini-3.5-flash-lite"
TIMEOUT_LLM_DEFAULT = 60
MAX_TOKENS_LLM_DEFAULT = 2048
TIMEOUT_AGENTE_DEFAULT = 45000
MAX_TOKENS_AGENTE_DEFAULT = 256
DISTANCIA_RAG_DEFAULT = 0.75
ROOT = Path(__file__).resolve().parents[3]
MAX_CODIGO = 12000
MAX_SALIDA_HERRAMIENTAS = 1_000_000
TIMEOUT_HERRAMIENTAS = 12
RAG_LIMITE = 3
AGENTE_RAG_POR_CATEGORIA = 2
AGENTE_RAG_MAX_FUENTES = 6
MAX_PASOS_AGENTE = 3
VENTANA_PETICIONES = 60
PRESUPUESTO_GLOBAL = 30
PRESUPUESTO_CLIENTE = 10
MAX_CONCURRENCIA = 2
TTL_CORRECCION = 300
RETENCION_CORRECCION = 86400
MAX_PROPUESTAS = 200
MAX_PROPUESTAS_SESION = 10
COOKIE_CORRECCIONES = "codeguard_correcciones"
RETRY_INITIAL_DELAY = 0.6
RETRY_MAX_DELAY = 2.0


def limites_solicitud(ruta: str) -> tuple[int, int]:
    """Plazo cooperativo y máximo de intentos reales, sin cambiar contratos HTTP."""
    if ruta in {"/api/v1/archivos/zip", "/api/v1/repositorios/github"}:
        return min(_obtener_entero_positivo("PROJECT_TOTAL_SECONDS", 150), 150), 15
    if ruta == "/api/v1/agente/analizar":
        return min(_obtener_entero_positivo("AGENT_TOTAL_SECONDS", 150), 150), 9
    return min(_obtener_entero_positivo("ANALYSIS_TOTAL_SECONDS", 45), 45), 3


def obtener_intentos_llm() -> int:
    return min(_obtener_entero_positivo("LLM_RETRY_ATTEMPTS", 2), 3)


def bandera(nombre: str, predeterminado: bool = False) -> bool:
    return os.getenv(nombre, "1" if predeterminado else "0").strip().casefold() in {"1", "true", "yes", "on"}


def obtener_ruta_chroma() -> Path:
    valor = os.getenv("CHROMA_PATH", "").strip()
    return Path(valor).expanduser() if valor else ROOT / "data" / "chroma"


def obtener_ruta_correcciones() -> Path:
    valor = os.getenv("CORRECTIONS_DB_PATH", "").strip()
    return Path(valor).expanduser() if valor else obtener_ruta_chroma().parent / "correcciones.sqlite3"


def cookie_segura() -> bool:
    # Docker sirve el frontend en HTTPS mediante el proxy de Railway.
    return bandera("CORRECTIONS_COOKIE_SECURE", bandera("SERVE_FRONTEND"))


def obtener_clave_gemini() -> str:
    """Obtiene la clave API exclusivamente del entorno."""
    return os.getenv("GEMINI_API_KEY", "").strip()


def obtener_modelo_gemini() -> str:
    """Obtiene el modelo Gemini configurado o su valor predeterminado."""
    valor = os.getenv("GEMINI_MODEL") or MODELO_GEMINI_DEFAULT
    return valor.strip() or MODELO_GEMINI_DEFAULT


def _obtener_entero_positivo(variable: str, valor_default: int) -> int:
    """Obtiene un entero positivo o devuelve el valor predeterminado."""
    try:
        valor = int(os.getenv(variable, str(valor_default)).strip())
    except (AttributeError, TypeError, ValueError):
        return valor_default
    return valor if valor > 0 else valor_default


def obtener_timeout_llm() -> int:
    """Devuelve el timeout del servicio LLM en segundos."""
    return _obtener_entero_positivo("LLM_TIMEOUT_SECONDS", TIMEOUT_LLM_DEFAULT)


def obtener_max_tokens_llm() -> int:
    """Devuelve el máximo de tokens de salida del servicio LLM."""
    return _obtener_entero_positivo(
        "LLM_MAX_OUTPUT_TOKENS",
        MAX_TOKENS_LLM_DEFAULT,
    )


def obtener_timeout_agente() -> int:
    """Devuelve el timeout HTTP del agente en milisegundos."""
    return _obtener_entero_positivo("AGENT_TIMEOUT_MS", TIMEOUT_AGENTE_DEFAULT)


def obtener_max_tokens_agente() -> int:
    """Devuelve el máximo de tokens de salida del planificador."""
    return _obtener_entero_positivo(
        "AGENT_MAX_OUTPUT_TOKENS",
        MAX_TOKENS_AGENTE_DEFAULT,
    )


def obtener_distancia_rag() -> float:
    """Obtiene y limita la distancia máxima RAG al intervalo [0, 2]."""
    try:
        distancia = float(
            os.getenv("RAG_MAX_DISTANCE", str(DISTANCIA_RAG_DEFAULT)).strip()
        )
    except (AttributeError, TypeError, ValueError):
        return DISTANCIA_RAG_DEFAULT

    if not math.isfinite(distancia):
        return DISTANCIA_RAG_DEFAULT

    return max(0.0, min(distancia, 2.0))


def analisis_estatico_habilitado() -> bool:
    """Indica si el análisis estático está habilitado por configuración."""
    return bandera("STATIC_ANALYSIS_ENABLED")

