"""Aceptación QA de la base a394d65; RAG/GitHub simulados, herramientas explícitas."""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import json
import sys

import pytest
from fastapi.testclient import TestClient
import app.main as api
from app.models.analisis import InformeModelo
from app.services import static_analysis as motor


def enviar(client, modo):
    if modo == "codigo":
        return client.post("/api/v1/analizar", json={"archivo": "x.py", "codigo": "eval(input())"})
    if modo == "python":
        return client.post("/api/v1/archivos", files={"archivo": ("x.py", b"eval(input())")})
    if modo == "zip":
        buf = BytesIO()
        with ZipFile(buf, "w") as z:
            z.writestr("src/x.py", "eval(input())")
        return client.post("/api/v1/archivos/zip", files={"archivo": ("x.zip", buf.getvalue())})
    return client.post("/api/v1/repositorios/github", json={"url": "https://github.com/demo/repo"})


@pytest.mark.parametrize("modo", ["codigo", "python", "zip", "github"])
@pytest.mark.parametrize("estado", ["completo", "parcial", "no_disponible", "desactivado"])
def test_cuatro_modalidades_preservan_abstencion_y_procedencia(monkeypatch, modo, estado):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "0")
    monkeypatch.setenv("STATIC_ANALYSIS_ENABLED", "0" if estado == "desactivado" else "1")
    informe = InformeModelo(hallazgos=[])
    informe._motivo_abstencion = "Sin evidencia RAG suficiente"
    monkeypatch.setattr(api, "analizar_codigo", lambda _: informe)
    monkeypatch.setattr(api, "obtener_archivos_python_github", lambda _: [("src/x.py", "eval(input())")])

    def estatico(codigo, archivo):
        assert estado != "desactivado", "No debe invocar analizadores con bandera apagada"
        return motor.ResultadoEstatico(
            archivo=archivo, estado=estado,
            herramientas=[
                motor.EstadoHerramienta(herramienta="ruff", estado="error" if estado == "no_disponible" else "ok"),
                motor.EstadoHerramienta(herramienta="bandit", estado="ok" if estado == "completo" else "timeout"),
            ], hallazgos=[],
        )
    monkeypatch.setattr(api, "analizar_estatico", estatico)
    with TestClient(api.app) as cliente:
        respuesta = enviar(cliente, modo)
    assert respuesta.status_code == 200
    datos = respuesta.json()
    reporte = datos["informes"][0] if "informes" in datos else datos
    assert reporte["estado"] == "abstenido"
    assert reporte["hallazgos"] == reporte["fuentes"] == []
    if estado == "desactivado":
        assert "analisis_estatico" not in reporte
    else:
        assert reporte["analisis_estatico"]["estado"] == estado
        assert reporte["analisis_estatico"]["archivo"] == reporte["archivo"]
        assert "fuentes" not in reporte["analisis_estatico"]


def test_subproceso_no_hereda_secretos_y_no_publica_stderr(monkeypatch, tmp_path):
    marcador = "SECRETO_SINTETICO_QA"
    monkeypatch.setenv("GEMINI_API_KEY", marcador)
    # Proceso controlado del test: comprueba entorno y emite un error privado.
    script = "import os,sys; assert 'GEMINI_API_KEY' not in os.environ; sys.stderr.write('SECRETO_SINTETICO_QA'); sys.exit(2)"
    estado, salida = motor._ejecutar([sys.executable, "-I", "-c", script], cwd=str(tmp_path))
    assert estado == "error" and salida is None


def test_herramientas_reales_no_ejecutan_payload_ni_dejan_temporal(tmp_path, monkeypatch):
    destino = tmp_path / "no_crear.txt"
    codigo = f"from pathlib import Path\nPath({str(destino)!r}).write_text('fallo')\neval(input())\n"
    temporal = []
    ejecutar = motor._ejecutar
    def registrar(*args, **kwargs):
        temporal.append(Path(kwargs["cwd"]))
        return ejecutar(*args, **kwargs)
    monkeypatch.setattr(motor, "_ejecutar", registrar)
    resultado = motor.analizar_estatico(codigo, "src/payload.py")
    assert resultado.estado == "completo", resultado.model_dump()
    assert any(h.regla == "B307" for h in resultado.hallazgos)
    assert not destino.exists()
    assert temporal and all(not p.exists() for p in temporal)
    serializado = json.dumps(resultado.model_dump())
    assert '"fuentes"' not in serializado and '"referencias"' not in serializado

