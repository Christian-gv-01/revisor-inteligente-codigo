
from app.config import (
    obtener_clave_gemini,
    obtener_modelo_gemini,
    obtener_timeout_llm,
    obtener_max_tokens_llm,
    obtener_timeout_agente,
    obtener_max_tokens_agente,
    obtener_distancia_rag,
    analisis_estatico_habilitado,
)


def test_valores_predeterminados(monkeypatch):
    variables = [
        "GEMINI_MODEL",
        "LLM_TIMEOUT_SECONDS",
        "LLM_MAX_OUTPUT_TOKENS",
        "AGENT_TIMEOUT_MS",
        "AGENT_MAX_OUTPUT_TOKENS",
        "RAG_MAX_DISTANCE",
        "STATIC_ANALYSIS_ENABLED",
    ]

    for variable in variables:
        monkeypatch.delenv(variable, raising=False)

    assert obtener_modelo_gemini() == "gemini-3.5-flash-lite"
    assert obtener_timeout_llm() == 60
    assert obtener_max_tokens_llm() == 2048
    assert obtener_timeout_agente() == 45000
    assert obtener_max_tokens_agente() == 256
    assert obtener_distancia_rag() == 0.75
    assert analisis_estatico_habilitado() is True


def test_variables_entorno_sobrescriben_valores(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "modelo-prueba")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "90")
    monkeypatch.setenv("LLM_MAX_OUTPUT_TOKENS", "3000")
    monkeypatch.setenv("AGENT_TIMEOUT_MS", "50000")
    monkeypatch.setenv("AGENT_MAX_OUTPUT_TOKENS", "512")

    assert obtener_modelo_gemini() == "modelo-prueba"
    assert obtener_timeout_llm() == 90
    assert obtener_max_tokens_llm() == 3000
    assert obtener_timeout_agente() == 50000
    assert obtener_max_tokens_agente() == 512


def test_clave_gemini_solo_desde_entorno(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "clave-prueba")

    assert obtener_clave_gemini() == "clave-prueba"


def test_clave_gemini_ausente(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    assert obtener_clave_gemini() == ""


def test_distancia_rag_configurable(monkeypatch):
    monkeypatch.setenv("RAG_MAX_DISTANCE", "0.45")

    assert obtener_distancia_rag() == 0.45


def test_distancia_rag_respeta_limites(monkeypatch):
    monkeypatch.setenv("RAG_MAX_DISTANCE", "5")

    assert obtener_distancia_rag() == 2.0

    monkeypatch.setenv("RAG_MAX_DISTANCE", "-1")

    assert obtener_distancia_rag() == 0.0


def test_distancia_rag_invalida(monkeypatch):
    monkeypatch.setenv("RAG_MAX_DISTANCE", "invalido")

    assert obtener_distancia_rag() == 0.75


def test_analisis_estatico_desactivado(monkeypatch):
    monkeypatch.setenv("STATIC_ANALYSIS_ENABLED", "0")

    assert analisis_estatico_habilitado() is False


def test_analisis_estatico_activado(monkeypatch):
    monkeypatch.setenv("STATIC_ANALYSIS_ENABLED", "yes")

    assert analisis_estatico_habilitado() is True


def test_timeout_invalido_usa_defecto(monkeypatch):
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "invalido")

    assert obtener_timeout_llm() == 60


def test_timeout_no_positivo_usa_defecto(monkeypatch):
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "-10")

    assert obtener_timeout_llm() == 60
