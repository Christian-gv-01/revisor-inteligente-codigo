"""Regresiones: Gemini puede fallar sin borrar hallazgos estáticos reales."""
from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient

from app.main import app
from app.services.llm import LLMError
from app.models.analisis import InformeModelo
from app.services.static_analysis import (
    ResultadoEstatico, HallazgoEstatico, EstadoHerramienta,
)


def estatico(codigo, archivo):
    return ResultadoEstatico(
        archivo=archivo,
        estado="completo",
        hallazgos=[
            HallazgoEstatico(
                herramienta="bandit", regla="B307", tipo="seguridad",
                linea=1, severidad="alta", titulo="Uso de eval",
                descripcion="Patrón potencialmente inseguro", confianza="alta",
            )
        ],
        herramientas=[
            EstadoHerramienta(herramienta="ruff", estado="ok", hallazgos=0),
            EstadoHerramienta(herramienta="bandit", estado="ok", hallazgos=1),
        ],
    )


def preparar(monkeypatch, estatico_activado=True):
    import app.main as principal
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "0")
    monkeypatch.setenv("STATIC_ANALYSIS_ENABLED", "1" if estatico_activado else "0")
    monkeypatch.setattr(principal, "analizar_estatico", estatico)


def test_gemini_503_devuelve_analisis_estatico_parcial(monkeypatch):
    import app.main as principal
    preparar(monkeypatch)
    monkeypatch.setattr(principal, "analizar_codigo", lambda _: (_ for _ in ()).throw(
        LLMError("Proveedor no disponible", 503)
    ))
    with TestClient(app) as client:
        respuesta = client.post("/api/v1/analizar", json={
            "archivo": "usuarios.py", "codigo": "eval(input())"
        })
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["estado"] == "parcial"
    assert datos["hallazgos"] == []
    assert datos["fuentes"] == []
    assert datos["analisis_estatico"]["hallazgos"][0]["regla"] == "B307"
    assert "Gemini" in datos["mensaje"]


def test_sin_herramientas_estaticas_gemini_503_se_conserva(monkeypatch):
    import app.main as principal
    preparar(monkeypatch, estatico_activado=False)
    monkeypatch.setattr(principal, "analizar_codigo", lambda _: (_ for _ in ()).throw(
        LLMError("Sin disponibilidad", 503)
    ))
    with TestClient(app) as client:
        r = client.post("/api/v1/analizar", json={"archivo": "x.py", "codigo": "print(1)"})
    assert r.status_code == 503


def test_estatico_no_disponible_no_se_finge_analisis(monkeypatch):
    import app.main as principal
    preparar(monkeypatch)
    def sin_herramientas(codigo, archivo):
        return ResultadoEstatico(
            archivo=archivo, estado="no_disponible", hallazgos=[],
            herramientas=[
                EstadoHerramienta(herramienta="ruff", estado="timeout"),
                EstadoHerramienta(herramienta="bandit", estado="timeout"),
            ],
        )
    monkeypatch.setattr(principal, "analizar_estatico", sin_herramientas)
    monkeypatch.setattr(principal, "analizar_codigo", lambda _: (_ for _ in ()).throw(
        LLMError("Proveedor no disponible", 504)
    ))
    with TestClient(app) as client:
        r = client.post("/api/v1/analizar", json={"archivo": "x.py", "codigo": "print(1)"})
    assert r.status_code == 504


def test_gemini_correcto_sigue_devolviendo_informe_ordinario(monkeypatch):
    import app.main as principal
    preparar(monkeypatch)
    monkeypatch.setattr(principal, "analizar_codigo", lambda _: InformeModelo(hallazgos=[]))
    with TestClient(app) as client:
        r = client.post("/api/v1/analizar", json={"archivo": "x.py", "codigo": "print(1)"})
    assert r.status_code == 200
    assert r.json()["estado"] == "analizado"
    assert r.json()["analisis_estatico"]["hallazgos"][0]["regla"] == "B307"


def test_zip_corta_nuevas_llamadas_gemini_despues_de_503(monkeypatch):
    import app.main as principal
    preparar(monkeypatch)
    llamadas = []
    def error_ia(codigo):
        llamadas.append(codigo)
        raise LLMError("Gemini no disponible", 503)
    monkeypatch.setattr(principal, "analizar_codigo", error_ia)
    buffer = BytesIO()
    with ZipFile(buffer, "w") as z:
        z.writestr("a.py", "eval(input())\n")
        z.writestr("b.py", "eval(input())\n")
    with TestClient(app) as client:
        r = client.post("/api/v1/archivos/zip", files={
            "archivo": ("ejemplo.zip", buffer.getvalue(), "application/zip")
        })
    assert r.status_code == 200
    body = r.json()
    assert body["estado"] == "parcial"
    assert body["total_archivos"] == 2
    assert [x["estado"] for x in body["informes"]] == ["parcial", "parcial"]
    assert len(llamadas) == 1


def test_github_parcial_sin_simular_citas(monkeypatch):
    import app.main as principal
    preparar(monkeypatch)
    monkeypatch.setattr(principal, "obtener_archivos_python_github", lambda _: [
        ("a.py", "eval(input())"),
        ("b.py", "eval(input())"),
    ])
    llamadas = []
    def fallar(codigo):
        llamadas.append(codigo)
        raise LLMError("Gemini no disponible", 503)
    monkeypatch.setattr(principal, "analizar_codigo", fallar)
    with TestClient(app) as client:
        r = client.post("/api/v1/repositorios/github", json={
            "url": "https://github.com/demo/proyecto"
        })
    assert r.status_code == 200
    assert r.json()["estado"] == "parcial"
    assert len(llamadas) == 1
    assert all(not x["fuentes"] for x in r.json()["informes"])
