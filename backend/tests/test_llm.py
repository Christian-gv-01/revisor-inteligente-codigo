
"""
Archivo: test_llm.py

Proyecto: Revisor Inteligente de Código Seguro.
Área responsable: QA y seguridad.

Objetivo:
Comprobar el comportamiento del servicio de inteligencia artificial
sin realizar llamadas reales a Gemini.

Pruebas:
1. Respuesta JSON válida.
2. Respuesta vacía.
3. Error HTTP 429 del proveedor.
4. Error HTTP 504 del proveedor.
5. Respuesta JSON inválida.
6. Timeout real simulado mediante una excepción HTTPX.

Todos los escenarios utilizan un cliente simulado.
"""

# pytest permite ejecutar las pruebas y verificar excepciones.
import pytest

# Mock permite simular objetos y funciones sin utilizar
# el servicio real de inteligencia artificial.
from unittest.mock import Mock

# HTTPX proporciona la excepción TimeoutException,
# que utilizaremos para simular un tiempo de espera agotado.
import httpx

# Importamos los errores del SDK de Google Gemini.
# Se utilizan para simular errores HTTP del proveedor.
from google.genai import errors

# Importamos el módulo que contiene la función analizar_codigo.
import app.services.llm as llm_module

# Importamos el modelo que debe cumplir el informe generado.
from app.models.analisis import InformeModelo


# =========================================================
# FUNCIÓN AUXILIAR: PREPARAR UN CLIENTE SIMULADO
# =========================================================

def crear_cliente_simulado(
    monkeypatch,
    texto_respuesta='{"hallazgos": []}',
):
    # Configuramos una clave ficticia.
    # No es una credencial real y no permite acceder a Gemini.
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "clave-ficticia-solo-para-pruebas",
    )

    # Creamos un cliente simulado para evitar conexiones externas.
    cliente = Mock()

    # Creamos una respuesta ficticia del modelo.
    respuesta = Mock()

    # Definimos el contenido de la respuesta.
    # Este valor se cambiará en las pruebas de respuesta vacía
    # y JSON inválido.
    respuesta.text = texto_respuesta

    # Simulamos los metadatos que consulta el servicio
    # cuando registra una respuesta correcta.
    respuesta.usage_metadata = Mock(
        prompt_token_count=10,
        candidates_token_count=5,
    )

    # Configuramos la llamada al modelo para devolver
    # la respuesta ficticia preparada anteriormente.
    cliente.models.generate_content.return_value = respuesta

    # Sustituimos el constructor del cliente real de Gemini.
    # Cuando el servicio intente crear un cliente, recibirá
    # nuestro objeto simulado en lugar de conectarse a Internet.
    monkeypatch.setattr(
        llm_module.genai,
        "Client",
        Mock(return_value=cliente),
    )

    # Devolvemos el cliente para poder configurar errores
    # y comprobar que se cierre después de cada prueba.
    return cliente


# =========================================================
# PRUEBA 1: PROCESAR UNA RESPUESTA JSON VÁLIDA
# =========================================================

def test_servicio_acepta_respuesta_json_valida(monkeypatch):
    # Preparamos una respuesta válida con cero hallazgos.
    cliente = crear_cliente_simulado(
        monkeypatch,
        '{"hallazgos": []}',
    )

    # Ejecutamos el servicio con código de ejemplo.
    # El cliente simulado evita una llamada real a Gemini.
    informe = llm_module.analizar_codigo("print('hola')")

    # Comprobamos que el resultado utiliza el modelo esperado.
    assert isinstance(informe, InformeModelo)

    # Verificamos que el informe contiene una lista vacía.
    assert informe.hallazgos == []

    # Comprobamos que el cliente se cierra al finalizar.
    cliente.close.assert_called_once()


# =========================================================
# PRUEBA 2: CONTROLAR UNA RESPUESTA VACÍA
# =========================================================

def test_servicio_controla_respuesta_vacia(monkeypatch):
    # Simulamos que Gemini no devuelve ningún texto.
    cliente = crear_cliente_simulado(
        monkeypatch,
        "",
    )

    # Esperamos que el servicio genere un LLMError controlado.
    with pytest.raises(
        llm_module.LLMError,
        match="respuesta vacía",
    ) as error:

        # Ejecutamos el servicio para provocar el escenario.
        llm_module.analizar_codigo("print('hola')")

    # Comprobamos que el error se clasifica como HTTP 502.
    assert error.value.codigo == 502

    # Incluso si ocurre un error, el cliente debe cerrarse.
    cliente.close.assert_called_once()


# =========================================================
# PRUEBA 3: CONTROLAR EL ERROR HTTP 429
# =========================================================

def test_servicio_controla_error_429(monkeypatch):
    # Creamos el cliente simulado.
    cliente = crear_cliente_simulado(monkeypatch)

    # Hacemos que la llamada al proveedor genere un APIError 429.
    # Este código suele indicar un límite de solicitudes o cuota.
    cliente.models.generate_content.side_effect = errors.APIError(
        429,
        {"message": "Cuota de solicitudes excedida"},
    )

    # Verificamos que el servicio convierte el error externo
    # en la excepción controlada LLMError.
    with pytest.raises(
        llm_module.LLMError,
        match="límite de solicitudes",
    ) as error:

        # Ejecutamos el análisis con el error simulado.
        llm_module.analizar_codigo("print('hola')")

    # Según la implementación actual, el error 429 se transforma
    # en el código HTTP 503 de nuestra aplicación.
    assert error.value.codigo == 503

    # Comprobamos que el cliente se cierra correctamente.
    cliente.close.assert_called_once()


# =========================================================
# PRUEBA 4: CONTROLAR EL ERROR HTTP 504 DEL PROVEEDOR
# =========================================================

def test_servicio_controla_timeout_504(monkeypatch):
    # Creamos el cliente simulado.
    cliente = crear_cliente_simulado(monkeypatch)

    # Simulamos un error HTTP 504 del proveedor.
    cliente.models.generate_content.side_effect = errors.APIError(
        504,
        {"message": "Tiempo de respuesta excedido"},
    )

    # Comprobamos que el servicio convierte el error
    # en una excepción controlada LLMError.
    with pytest.raises(
        llm_module.LLMError,
        match="tiempo de respuesta",
    ) as error:

        # Ejecutamos el análisis con el error simulado.
        llm_module.analizar_codigo("print('hola')")

    # El servicio debe clasificar este error como HTTP 504.
    assert error.value.codigo == 504

    # Comprobamos que el cliente se cierra tras el error.
    cliente.close.assert_called_once()


# =========================================================
# PRUEBA 5: CONTROLAR UNA RESPUESTA JSON INVÁLIDA
# =========================================================

def test_servicio_controla_json_invalido(monkeypatch):
    # Simulamos que el modelo devuelve texto que no es JSON.
    cliente = crear_cliente_simulado(
        monkeypatch,
        "esto no es JSON",
    )

    # Esperamos que el servicio transforme el error de validación
    # en una excepción controlada LLMError.
    with pytest.raises(
        llm_module.LLMError,
        match="no cumple el esquema esperado",
    ) as error:

        # Ejecutamos el servicio con la respuesta inválida.
        llm_module.analizar_codigo("print('hola')")

    # Comprobamos que el error se clasifica como HTTP 502.
    assert error.value.codigo == 502

    # Verificamos que el cliente se cierra incluso si falla
    # la validación del JSON.
    cliente.close.assert_called_once()


# =========================================================
# PRUEBA 6: CONTROLAR UN TIMEOUT REAL SIMULADO
# =========================================================

def test_servicio_controla_timeout_real(monkeypatch):
    # Preparamos un cliente que no realiza conexiones externas.
    cliente = crear_cliente_simulado(monkeypatch)

    # Simulamos una excepción de timeout de HTTPX.
    # Esto representa una petición cuyo tiempo de espera se agota.
    cliente.models.generate_content.side_effect = (
        httpx.TimeoutException("Tiempo de espera agotado")
    )

    # Esperamos que el servicio transforme el timeout
    # en un error controlado LLMError con código 504.
    with pytest.raises(
        llm_module.LLMError,
        match="tiempo de respuesta",
    ) as error:

        # Ejecutamos el servicio para provocar el timeout simulado.
        llm_module.analizar_codigo("print('hola')")

    # Verificamos el código HTTP que esperamos de la aplicación.
    assert error.value.codigo == 504

    # El bloque finally del servicio debe cerrar el cliente
    # incluso cuando se produce una excepción.
    cliente.close.assert_called_once()

# =========================================================
# PRUEBA 7: NO EXPONER CLAVES EN LOS ERRORES HTTP
# =========================================================

def test_endpoint_no_expone_clave_en_error_proveedor(monkeypatch):
    """
    Objetivo:
    Verificar que un error del proveedor de IA no revele
    credenciales en la respuesta HTTP de nuestra API.
    """

    # Importamos la aplicación FastAPI y el cliente de pruebas.
    # TestClient permite probar el endpoint sin iniciar un servidor.
    import app.main as main_module
    from fastapi.testclient import TestClient

    # Creamos una clave ficticia que usaremos para detectar
    # si el sistema revela accidentalmente información sensible.
    # Esta clave es inventada y no permite acceder a ningún servicio.
    clave_ficticia = "GEMINI_SECRET_FICTICIO_QA_12345"

    # Creamos un cliente simulado de Gemini.
    # La función auxiliar evita una conexión real a Internet.
    cliente_gemini = crear_cliente_simulado(monkeypatch)

    # Configuramos la variable de entorno con nuestra clave ficticia.
    monkeypatch.setenv("GEMINI_API_KEY", clave_ficticia)

    # Simulamos un error HTTP 500 del proveedor.
    # El mensaje del error contiene deliberadamente la clave ficticia
    # para comprobar que la API no la devuelve al usuario.
    cliente_gemini.models.generate_content.side_effect = (
        errors.APIError(
            500,
            {"message": f"Error simulado. Clave: {clave_ficticia}"},
        )
    )

    # Garantizamos que el endpoint utiliza la función de análisis
    # real, cuyo cliente de Gemini está sustituido por nuestro mock.
    monkeypatch.setattr(
        main_module,
        "analizar_codigo",
        llm_module.analizar_codigo,
    )

    # Creamos el cliente HTTP de pruebas para la aplicación.
    cliente_api = TestClient(main_module.app)

    # Enviamos una solicitud válida para activar el error simulado.
    respuesta = cliente_api.post(
        "/api/v1/analizar",
        json={
            "archivo": "ejemplo.py",
            "codigo": "print('hola')",
        },
    )

    # Verificamos que el error del proveedor se transforma
    # en una respuesta HTTP 502 controlada por nuestra API.
    assert respuesta.status_code == 502

    # Comprobamos que la clave ficticia no aparece en la respuesta.
    assert clave_ficticia not in respuesta.text

    # Comprobamos que la API devuelve un mensaje genérico
    # en lugar del mensaje original del proveedor.
    assert "No fue posible completar el análisis." in respuesta.text

    # Verificamos que el cliente simulado se cierra al finalizar.
    cliente_gemini.close.assert_called_once()
