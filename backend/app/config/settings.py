"""Configuración centralizada de CODEGUARD.

Todas las lecturas de variables de entorno de la aplicación se concentran
 aquí para mantener valores predeterminados y validaciones consistentes.
"""

import math
import os


MODELO_GEMINI_DEFAULT = "gemini-3.5-flash-lite"
TIMEOUT_LLM_DEFAULT = 60
MAX_TOKENS_LLM_DEFAULT = 2048
TIMEOUT_AGENTE_DEFAULT = 45000
MAX_TOKENS_AGENTE_DEFAULT = 256
DISTANCIA_RAG_DEFAULT = 0.75


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
    valor = os.getenv("STATIC_ANALYSIS_ENABLED", "1")
    return valor.strip().casefold() in {"1", "true", "yes", "on"}
