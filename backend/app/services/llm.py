
import logging
import os
import time
from pathlib import Path
import httpx

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.models.analisis import InformeModelo

# Configuración
ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

logger = logging.getLogger(__name__)

PROMPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "prompts"
    / "system_v1.md"
)


class LLMError(Exception):
    """Error controlado del servicio de inteligencia artificial."""

    def __init__(self, mensaje: str, codigo: int = 502):
        super().__init__(mensaje)
        self.codigo = codigo


def analizar_codigo(codigo: str) -> InformeModelo:
    """Analiza un fragmento sin ejecutar el código recibido."""

    api_key = os.getenv("GEMINI_API_KEY")
    modelo = os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
    timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
    max_tokens = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "2048"))

    if not api_key:
        raise LLMError("Proveedor de IA no configurado.", 503)

    instrucciones = PROMPT_PATH.read_text(encoding="utf-8")

    inicio = time.perf_counter()

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=timeout * 1000
        ),
    )

    try:
        respuesta = client.models.generate_content(
            model=modelo,
            contents=codigo,
            config=types.GenerateContentConfig(
                system_instruction=instrucciones,
                temperature=0.2,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
                response_schema=InformeModelo,
            ),
        )

        if not respuesta.text:
            raise LLMError(
                "El modelo devolvió una respuesta vacía."
            )

        informe = InformeModelo.model_validate_json(
            respuesta.text
        )

        # Comprobar que las líneas realmente existen.
        total_lineas = len(codigo.splitlines())

        for hallazgo in informe.hallazgos:
            if hallazgo.linea > total_lineas:
                raise LLMError(
                    "El modelo indicó una línea inexistente."
                )

        uso = respuesta.usage_metadata

        logger.info(
            "llm_success model=%s duration_ms=%d "
            "input_tokens=%s output_tokens=%s",
            modelo,
            round((time.perf_counter() - inicio) * 1000),
            getattr(uso, "prompt_token_count", None),
            getattr(uso, "candidates_token_count", None),
        )

        return informe

    
    except httpx.TimeoutException as error:
        logger.warning(
            "llm_timeout model=%s duration_ms=%d",
            modelo,
            round((time.perf_counter() - inicio) * 1000),
        )

        raise LLMError(
            "El proveedor excedió el tiempo de respuesta.",
            504,
        ) from error

    except errors.APIError as error:
        logger.warning(
            "llm_provider_error model=%s status=%s",
            modelo,
            error.code,
        )

        if error.code == 429:
            raise LLMError(
                "El proveedor ha alcanzado su límite de solicitudes.",
                503,
            ) from error

        if error.code in (408, 504):
            raise LLMError(
                "El proveedor excedió el tiempo de respuesta.",
                504,
            ) from error

        raise LLMError(
            "No fue posible completar el análisis.",
            502,
        ) from error

    except (ValidationError, ValueError) as error:
        raise LLMError(
            "La respuesta del modelo no cumple el esquema esperado.",
            502,
        ) from error

    finally:
        client.close()
