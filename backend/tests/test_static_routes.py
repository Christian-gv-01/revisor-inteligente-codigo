"""Contratos HTTP de Ruff/Bandit; Gemini y GitHub simulados."""
from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient

from app.main import app
from app.models.analisis import InformeModelo
from app.services.static_analysis import (
    HallazgoEstatico,
    ResultadoEstatico,
    EstadoHerramienta,
)


def respuesta_estatica(codigo: str, archivo: str) -> ResultadoEstatico:
    return ResultadoEstatico(
        archivo=archivo,
        estado="completo",
        hallazgos=[HallazgoEstatico(
            herramienta="bandit",
            regla="B307",
            tipo="seguridad",
            linea=1,
            severidad="alta",
            titulo="Bandit B307: blacklist",
            descripcion="Uso potencialmente inseguro de eval.",
            confianza="alta",
        )],
        herramientas=[
            EstadoHerramienta(herramienta="ruff", estado="ok", hallazgos=0),
            EstadoHerramienta(herramienta="bandit", estado="ok", hallazgos=1),
        ],
    )


def preparar(monkeypatch):
    import app.main as principal

    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "0")
    monkeypatch.setenv("STATIC_ANALYSIS_ENABLED", "1")
    monkeypatch.setattr(principal, "analizar_estatico", respuesta_estatica)
    monkeypatch.setattr(
        principal, "analizar_codigo",
        lambda codigo: InformeModelo(hallazgos=[]),
    )


def test_endpoint_estatico_independiente_de_gemini(monkeypatch):
    preparar(monkeypatch)
    with TestClient(app) as client:
        r = client.post("/api/v1/estatico/analizar", json={
            "archivo": "usuarios.py", "codigo": "eval(input())"
        })
    assert r.status_code == 200
    assert r.json()["estado"] == "completo"
    assert r.json()["hallazgos"][0]["regla"] == "B307"


def test_endpoint_estatico_entrada_estructurada(monkeypatch):
    preparar(monkeypatch)
    with TestClient(app) as client:
        r = client.post("/api/v1/estatico/analizar", json={
            "archivo": "codigo.py", "codigo": ""
        })
    assert r.status_code == 422


def test_codigo_directo_incluye_estatico_separado_del_rag(monkeypatch):
    preparar(monkeypatch)
    with TestClient(app) as client:
        r = client.post("/api/v1/analizar", json={
            "archivo": "usuarios.py", "codigo": "eval(input())"
        })
    assert r.status_code == 200
    assert r.json()["hallazgos"] == []
    assert r.json()["analisis_estatico"]["hallazgos"][0]["regla"] == "B307"
    assert r.json()["fuentes"] == []


def test_archivo_python_incluye_estatico(monkeypatch):
    preparar(monkeypatch)
    with TestClient(app) as client:
        r = client.post("/api/v1/archivos", files={
            "archivo": ("usuarios.py", b"eval(input())", "text/x-python")
        })
    assert r.status_code == 200
    assert r.json()["analisis_estatico"]["archivo"] == "usuarios.py"


def test_zip_incluye_informe_individual_estatico(monkeypatch):
    preparar(monkeypatch)
    buffer = BytesIO()
    with ZipFile(buffer, "w") as z:
        z.writestr("src/usuarios.py", "eval(input())")
    buffer.seek(0)
    with TestClient(app) as client:
        r = client.post("/api/v1/archivos/zip", files={
            "archivo": ("ejemplo.zip", buffer.getvalue(), "application/zip")
        })
    assert r.status_code == 200
    assert len(r.json()["informes"]) == 1
    assert r.json()["informes"][0]["analisis_estatico"]["hallazgos"][0]["regla"] == "B307"


def test_github_usa_codigo_no_confiable_como_dato(monkeypatch):
    preparar(monkeypatch)
    import app.main as principal

    monkeypatch.setattr(
        principal, "obtener_archivos_python_github",
        lambda url: [("src/usuarios.py", "eval(input())")],
    )
    with TestClient(app) as client:
        r = client.post("/api/v1/repositorios/github", json={
            "url": "https://github.com/demo/proyecto"
        })
    assert r.status_code == 200
    report = r.json()["informes"][0]
    assert report["archivo"] == "src/usuarios.py"
    assert report["analisis_estatico"]["archivo"] == "src/usuarios.py"


def test_bandera_desactivada_mantiene_contrato_anterior(monkeypatch):
    preparar(monkeypatch)
    monkeypatch.setenv("STATIC_ANALYSIS_ENABLED", "0")
    with TestClient(app) as client:
        r = client.post("/api/v1/analizar", json={
            "archivo": "usuarios.py", "codigo": "print('ok')"
        })
    assert r.status_code == 200
    assert "analisis_estatico" not in r.json()
