
"""
Archivo: test_analysis.py

Propósito:
Probar el endpoint POST /api/v1/analizar del proyecto
Revisor Inteligente de Código Seguro.

Las pruebas verifican:
1. Que una solicitud válida devuelve un JSON correcto.
2. Que las entradas inválidas son rechazadas.
3. Que los errores del servicio de IA se controlan correctamente.

IMPORTANTE:
Se utilizan mocks para simular el servicio de IA.
Por tanto, estas pruebas no necesitan llamar realmente a Gemini.
"""

# Importamos pytest para ejecutar las pruebas automatizadas
# y para probar diferentes entradas mediante parametrización.
import pytest

# Importamos Mock para simular funciones y definir
# qué resultado o error deben producir durante las pruebas.
from unittest.mock import Mock

# Importamos TestClient para enviar solicitudes HTTP de prueba
# a FastAPI sin iniciar un servidor independiente.
from fastapi.testclient import TestClient

# Importamos el módulo principal de la API.
# Lo necesitamos para sustituir temporalmente la función
# analizar_codigo que utiliza el endpoint.
import app.main as main_module

# Importamos la aplicación FastAPI que vamos a probar.
from app.main import app

# Importamos los modelos que representan los hallazgos
# y el informe generado por el servicio de inteligencia artificial.
from app.models.analisis import Hallazgo, InformeModelo


# Creamos un cliente de pruebas asociado a nuestra API.
# Lo utilizaremos para enviar solicitudes al endpoint.
client = TestClient(app)


# ---------------------------------------------------------
# FUNCIÓN AUXILIAR: CREAR UN INFORME FICTICIO
# ---------------------------------------------------------

def crear_informe_prueba():
    # Construimos un informe que cumple el modelo InformeModelo.
    # Este informe es ficticio y solo se utiliza para las pruebas.
    return InformeModelo(
        # Un informe contiene una lista de hallazgos.
        hallazgos=[
            # Creamos un hallazgo de ejemplo con todos los campos
            # obligatorios definidos en el modelo Hallazgo.
            Hallazgo(
                # El hallazgo corresponde a la primera línea.
                linea=1,

                # Establecemos la severidad del hallazgo.
                severidad="alta",

                # Indicamos la categoría del posible problema.
                categoria="Credenciales",

                # Escribimos el título descriptivo.
                titulo="Posible secreto en el código",

                # Explicamos el posible riesgo detectado.
                explicacion=(
                    "El código podría contener información sensible."
                ),

                # Proponemos una medida de corrección.
                correccion_sugerida=(
                    "Utilizar una variable de entorno."
                ),
            )
        ]
    )


# ---------------------------------------------------------
# PRUEBA 1: SOLICITUD VÁLIDA Y RESPUESTA JSON
# ---------------------------------------------------------

def test_analizar_devuelve_json_valido(monkeypatch):
    # Preparamos un fragmento de código que enviaremos a la API.
    # Es una cadena de texto: esta prueba no ejecuta ese código.
    codigo = "password = '12345'\nprint(password)"

    # Creamos un mock que devolverá nuestro informe ficticio
    # en lugar de realizar una llamada real a Gemini.
    mock_analisis = Mock(
        return_value=crear_informe_prueba()
    )

    # Sustituimos temporalmente la función analizar_codigo
    # utilizada por el módulo principal de la aplicación.
    # Así controlamos la respuesta del servicio de IA.
    monkeypatch.setattr(
        main_module,
        "analizar_codigo",
        mock_analisis,
    )

    # Enviamos una solicitud POST al endpoint de análisis.
    # El cuerpo JSON contiene el nombre del archivo y el código.
    respuesta = client.post(
        "/api/v1/analizar",
        json={
            "archivo": "ejemplo.py",
            "codigo": codigo,
        },
    )

    # Comprobamos que la API devuelve HTTP 200,
    # indicando que la solicitud se procesó correctamente.
    assert respuesta.status_code == 200

    # Convertimos la respuesta JSON en un diccionario de Python
    # para poder comprobar sus campos.
    resultado = respuesta.json()

    # Verificamos que el nombre del archivo se conserva.
    assert resultado["archivo"] == "ejemplo.py"

    # Verificamos que el estado del análisis es el esperado.
    assert resultado["estado"] == "analizado"

    # Comprobamos que los hallazgos se devuelven como una lista.
    assert isinstance(resultado["hallazgos"], list)

    # Verificamos la severidad del primer hallazgo.
    assert resultado["hallazgos"][0]["severidad"] == "alta"

    # Verificamos la línea asociada al primer hallazgo.
    assert resultado["hallazgos"][0]["linea"] == 1

    # Comprobamos que el mock fue llamado exactamente una vez
    # y que recibió el mismo código enviado al endpoint.
    mock_analisis.assert_called_once_with(codigo)


# ---------------------------------------------------------
# PRUEBA 2: RECHAZO DE ENTRADAS INVÁLIDAS
# ---------------------------------------------------------

# Parametrize permite ejecutar la misma prueba con distintos datos.
# Cada elemento de la lista representa un caso independiente.
@pytest.mark.parametrize(
    "datos",
    [
        # Caso 1: el código está vacío.
        {"archivo": "ejemplo.py", "codigo": ""},

        # Caso 2: falta el campo obligatorio codigo.
        {"archivo": "ejemplo.py"},

        # Caso 3: el nombre del archivo está vacío.
        {"archivo": "", "codigo": "print('hola')"},

        # Caso 4: falta el campo obligatorio archivo.
        {"codigo": "print('hola')"},

        # Caso 5: el nombre del archivo supera 255 caracteres.
        {"archivo": "a" * 256, "codigo": "print('hola')"},

        # Caso 6: el código supera 12000 caracteres.
        {"archivo": "ejemplo.py", "codigo": "x" * 12001},
    ],
)
def test_analizar_rechaza_entradas_invalidas(monkeypatch, datos):
    # Creamos un mock para detectar si el servicio de IA
    # llega a ser llamado durante una solicitud inválida.
    mock_analisis = Mock(
        return_value=crear_informe_prueba()
    )

    # Sustituimos temporalmente la función de análisis.
    monkeypatch.setattr(
        main_module,
        "analizar_codigo",
        mock_analisis,
    )

    # Enviamos al endpoint el caso de entrada correspondiente.
    respuesta = client.post(
        "/api/v1/analizar",
        json=datos,
    )

    # FastAPI debe rechazar estas entradas con HTTP 422,
    # porque no cumplen las restricciones del modelo de entrada.
    assert respuesta.status_code == 422

    # Verificamos que el servicio de IA no se haya llamado.
    # Una entrada inválida debe rechazarse antes del análisis.
    mock_analisis.assert_not_called()


# ---------------------------------------------------------
# PRUEBA 3: CONTROL DE UN ERROR DEL SERVICIO DE IA
# ---------------------------------------------------------

def test_analizar_controla_error_del_servicio(monkeypatch):
    # Creamos un mock que, al ser llamado, genera una excepción
    # LLMError con un mensaje controlado y código HTTP 503.
    mock_analisis = Mock(
        side_effect=main_module.LLMError(
            "Proveedor temporalmente no disponible.",
            503,
        )
    )

    # Sustituimos la función de análisis por el mock.
    # Así simulamos un fallo sin contactar con Gemini.
    monkeypatch.setattr(
        main_module,
        "analizar_codigo",
        mock_analisis,
    )

    # Enviamos una solicitud válida para que la petición llegue
    # a la función simulada y se produzca el error.
    respuesta = client.post(
        "/api/v1/analizar",
        json={
            "archivo": "ejemplo.py",
            "codigo": "print('hola')",
        },
    )

    # Comprobamos que la API devuelve el código HTTP 503.
    assert respuesta.status_code == 503

    # Comprobamos que la respuesta contiene el mensaje controlado
    # definido en la excepción.
    assert respuesta.json()["detail"] == (
        "Proveedor temporalmente no disponible."
    )

    # Comprobación básica: la respuesta no debe incluir
    # el nombre de la variable de entorno de la clave.
    # Esto no demuestra por sí solo que todos los secretos
    # estén protegidos; necesitaremos pruebas adicionales.
    assert "GEMINI_API_KEY" not in respuesta.text
