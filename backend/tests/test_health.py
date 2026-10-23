
# Importamos TestClient para probar la API sin iniciar un servidor aparte.
from fastapi.testclient import TestClient

# Importamos la aplicación FastAPI que vamos a comprobar.
from app.main import app

# Creamos un cliente de pruebas asociado a nuestra aplicación.
client = TestClient(app)


# Definimos una prueba para verificar que el endpoint de salud funciona.
def test_health_endpoint_returns_success():

    # Enviamos una petición GET al endpoint /health y guardamos la respuesta.
    response = client.get("/health")

    # Comprobamos que la API responda con el código HTTP 200 (correcto).
    assert response.status_code == 200

    # Comprobamos que la respuesta JSON tenga exactamente los datos esperados.
    assert response.json() == {
        # Verificamos que el estado del servicio sea correcto.
        "status": "ok",

        # Verificamos que la respuesta identifique nuestro proyecto.
        "service": "revisor-inteligente-codigo",

        # Verificamos que la versión de la API sea la esperada.
        "version": "0.1.0",
    }
