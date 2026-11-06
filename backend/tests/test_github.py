"""Pruebas offline para el servicio de GitHub de CODEGUARD.

Guardar como backend/tests/test_github.py. No consume GitHub ni Gemini.
"""

import base64
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.analisis import Hallazgo, InformeModelo
from app.services import github_repos
import app.main as main_module


SHA_TREE = "a" * 40
REPO_URL = "https://github.com/demo/mini"
BASE = "/repos/demo/mini"


def api_simulada(monkeypatch, archivos=None, *, privado=False, truncado=False, fallos=None):
    """Sustituye la red por httpx.MockTransport conservando la lectura real de JSON."""
    archivos = archivos if archivos is not None else {"src/ejemplo.py": "resultado = eval(input())\n"}
    fallos = fallos or {}
    rutas = {
        BASE: {"private": privado, "default_branch": "main"},
        f"{BASE}/commits/main": {"commit": {"tree": {"sha": SHA_TREE}}},
    }
    entradas = []
    for indice, (ruta, codigo) in enumerate(archivos.items(), start=1):
        sha = format(indice, "040x")
        datos = codigo if isinstance(codigo, bytes) else codigo.encode("utf-8")
        entradas.append({"type": "blob", "path": ruta, "size": len(datos), "sha": sha})
        rutas[f"{BASE}/git/blobs/{sha}"] = {
            "encoding": "base64",
            "content": base64.b64encode(datos).decode("ascii"),
        }
    rutas[f"{BASE}/git/trees/{SHA_TREE}"] = {"truncated": truncado, "tree": entradas}
    solicitudes = []

    def handler(request):
        solicitudes.append(str(request.url))
        # La única sede remota que debe tocar el servicio es la API de GitHub.
        assert request.url.host == "api.github.com"
        assert request.url.scheme == "https"
        ruta = request.url.path
        if ruta in fallos:
            valor = fallos[ruta]
            if isinstance(valor, Exception):
                raise valor
            return httpx.Response(valor, json={"message": "simulado"})
        if ruta not in rutas:
            return httpx.Response(404, json={"message": "Not Found"})
        return httpx.Response(200, json=rutas[ruta])

    def fabrica_cliente(**kwargs):
        return httpx.Client(transport=httpx.MockTransport(handler), **kwargs)

    # Evita sustituir el módulo httpx global que utiliza FastAPI/TestClient.
    monkeypatch.setattr(
        github_repos,
        "httpx",
        SimpleNamespace(
            Client=fabrica_cliente,
            Timeout=httpx.Timeout,
            TimeoutException=httpx.TimeoutException,
            RequestError=httpx.RequestError,
        ),
    )
    return solicitudes


def error_http(codigo, funcion, *args):
    with pytest.raises(HTTPException) as fallo:
        funcion(*args)
    assert fallo.value.status_code == codigo


@pytest.mark.parametrize("url", [
    "http://github.com/demo/mini",
    "https://github.com.evil.test/demo/mini",
    "https://user:pass@github.com/demo/mini",
    "https://github.com:443/demo/mini",
    "https://github.com/demo/mini/tree/main",
    "https://github.com/demo/mini?token=123",
    "https://github.com/demo/mini#readme",
    "https://github.com/demo/../mini",
    "https://github.com/demo/%2e%2e",
    "https://127.0.0.1/demo/mini",
])
def test_rechaza_direcciones_no_permitidas(url):
    error_http(400, github_repos.validar_url_github, url)


def test_acepta_url_publica_extrayendo_owner_y_repo():
    assert github_repos.validar_url_github(REPO_URL) == ("demo", "mini")


def test_descarga_python_sin_ejecutarlo(monkeypatch):
    peticiones = api_simulada(monkeypatch)
    resultado = github_repos.obtener_archivos_python_github(REPO_URL)
    assert resultado == [("src/ejemplo.py", "resultado = eval(input())\n")]
    assert len(peticiones) == 4
    assert all(p.startswith("https://api.github.com/") for p in peticiones)


def test_acepta_cinco_python(monkeypatch):
    api_simulada(monkeypatch, {f"modulo_{i}.py": "x = 1\n" for i in range(5)})
    assert len(github_repos.obtener_archivos_python_github(REPO_URL)) == 5


def test_rechaza_seis_python(monkeypatch):
    api_simulada(monkeypatch, {f"modulo_{i}.py": "x = 1\n" for i in range(6)})
    error_http(413, github_repos.obtener_archivos_python_github, REPO_URL)


def test_rechaza_ruta_de_traversal(monkeypatch):
    api_simulada(monkeypatch, {"../secreto.py": "print('nunca')\n"})
    error_http(400, github_repos.obtener_archivos_python_github, REPO_URL)


def test_rechaza_archivo_excesivo(monkeypatch):
    api_simulada(monkeypatch, {"grande.py": "x" * 48_001})
    error_http(413, github_repos.obtener_archivos_python_github, REPO_URL)


def test_rechaza_total_superior_a_12000_caracteres(monkeypatch):
    api_simulada(monkeypatch, {"a.py": "a" * 7_000, "b.py": "b" * 5_001})
    error_http(413, github_repos.obtener_archivos_python_github, REPO_URL)


def test_rechaza_repositorio_privado(monkeypatch):
    api_simulada(monkeypatch, privado=True)
    error_http(403, github_repos.obtener_archivos_python_github, REPO_URL)


def test_rechaza_arbol_truncado(monkeypatch):
    api_simulada(monkeypatch, truncado=True)
    error_http(413, github_repos.obtener_archivos_python_github, REPO_URL)


def test_rechaza_codigo_no_utf8(monkeypatch):
    api_simulada(monkeypatch, {"no_utf8.py": b"\xff\xfe"})
    error_http(400, github_repos.obtener_archivos_python_github, REPO_URL)


def test_rechaza_archivo_binario(monkeypatch):
    api_simulada(monkeypatch, {"binario.py": b"a = 1\x00\n"})
    error_http(413, github_repos.obtener_archivos_python_github, REPO_URL)


def test_rechaza_repositorio_inexistente(monkeypatch):
    api_simulada(monkeypatch, fallos={BASE: 404})
    error_http(404, github_repos.obtener_archivos_python_github, REPO_URL)


def test_controla_limite_de_api_github(monkeypatch):
    api_simulada(monkeypatch, fallos={BASE: 403})
    error_http(503, github_repos.obtener_archivos_python_github, REPO_URL)


def test_controla_timeout_github(monkeypatch):
    api_simulada(monkeypatch, fallos={BASE: httpx.ConnectTimeout("sin respuesta")})
    error_http(504, github_repos.obtener_archivos_python_github, REPO_URL)


def test_endpoint_devuelve_informes_con_nombre_y_fuentes(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "obtener_archivos_python_github",
        lambda url: [("src/ejemplo.py", "x = eval(input())\n")],
    )
    def analizador_falso(_codigo):
        informe = InformeModelo(hallazgos=[Hallazgo(
            linea=1,
            severidad="critica",
            categoria="Ejecución arbitraria",
            titulo="eval inseguro",
            explicacion="El dato no confiable llega a eval.",
            correccion_sugerida="No utilizar eval con entradas externas.",
            referencias=["seguridad_python-001"],
        )])
        informe._fuentes = [{
            "id": "seguridad_python-001",
            "documento": "seguridad_python.md",
            "seccion": "Regla 1",
            "fuente": "MITRE CWE-94",
            "url": "https://cwe.mitre.org/data/definitions/94.html",
            "distancia": 0.1,
        }]
        return informe
    monkeypatch.setattr(main_module, "analizar_codigo", analizador_falso)
    respuesta = TestClient(app).post(
        "/api/v1/repositorios/github", json={"url": REPO_URL}
    )
    assert respuesta.status_code == 200, respuesta.text
    data = respuesta.json()
    assert data["total_archivos"] == 1
    assert data["informes"][0]["archivo"] == "src/ejemplo.py"
    assert data["informes"][0]["hallazgos"][0]["linea"] == 1
    assert data["informes"][0]["fuentes"][0]["id"] == "seguridad_python-001"


def test_endpoint_rechaza_url_invalida_sin_red():
    respuesta = TestClient(app).post(
        "/api/v1/repositorios/github",
        json={"url": "https://example.com/otro/repositorio"},
    )
    assert respuesta.status_code == 400
