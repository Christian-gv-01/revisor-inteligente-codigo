"""Contrato del motor Ruff/Bandit: no ejecuta código recibido ni requiere Gemini."""
from __future__ import annotations

import json
import subprocess

import pytest

from app.services import static_analysis as mod


RUFF = [{
    "code": "F401",
    "message": "import sin utilizar",
    "location": {"row": 1, "column": 1},
}]
BANDIT = {
    "results": [{
        "test_id": "B307",
        "test_name": "blacklist",
        "issue_text": "Use of possibly insecure function eval.",
        "issue_severity": "HIGH",
        "issue_confidence": "HIGH",
        "line_number": 2,
        "more_info": "https://bandit.readthedocs.io/",
    }]
}


def simular_ambos(monkeypatch):
    llamadas = []

    def falso_ejecutar(comando, *, entrada=None, cwd):
        llamadas.append((comando, entrada, cwd))
        return ("ok", json.dumps(RUFF if "ruff" in comando else BANDIT))

    monkeypatch.setattr(mod, "_ejecutar", falso_ejecutar)
    return llamadas


def test_ruta_de_repositorio_interna_aceptada(monkeypatch):
    simular_ambos(monkeypatch)
    reporte = mod.analizar_estatico("import os\nx = eval(input())\n", "src/main.py")
    assert reporte.archivo == "src/main.py"
    assert reporte.estado == "completo"


def test_normaliza_hallazgos_separados(monkeypatch):
    llamadas = simular_ambos(monkeypatch)
    resultado = mod.analizar_estatico("import os\nx = eval(input())\n", "usuarios.py")
    assert resultado.estado == "completo"
    assert [h.herramienta for h in resultado.hallazgos] == ["ruff", "bandit"]
    assert resultado.hallazgos[0].tipo == "calidad"
    assert resultado.hallazgos[1].tipo == "seguridad"
    assert resultado.hallazgos[1].severidad == "alta"
    assert resultado.hallazgos[1].confianza == "alta"
    assert [x.hallazgos for x in resultado.herramientas] == [1, 1]
    assert len(llamadas) == 2


def test_sin_hallazgos_no_inventa_vulnerabilidades(monkeypatch):
    monkeypatch.setattr(
        mod, "_ejecutar",
        lambda comando, **kw: ("ok", "[]" if "ruff" in comando else '{"results": []}')
    )
    resultado = mod.analizar_estatico("print('hola')\n")
    assert resultado.hallazgos == []
    assert resultado.estado == "completo"


def test_analizador_faltante_genera_estado_parcial(monkeypatch):
    monkeypatch.setattr(
        mod, "_ejecutar",
        lambda comando, **kw: ("no_disponible", None) if "ruff" in comando else ("ok", '{"results": []}')
    )
    resultado = mod.analizar_estatico("print('hola')\n")
    assert resultado.estado == "parcial"
    assert resultado.herramientas[0].estado == "no_disponible"
    assert resultado.mensaje


def test_ambos_indisponibles_no_finge_exito(monkeypatch):
    monkeypatch.setattr(mod, "_ejecutar", lambda *a, **k: ("timeout", None))
    assert mod.analizar_estatico("print(123)").estado == "no_disponible"


@pytest.mark.parametrize("codigo,nombre", [
    ("", "codigo.py"), ("\x00", "codigo.py"), ("x" * 12001, "codigo.py"),
    ("print(1)", "../escape.py"), ("print(1)", "subcarpeta/../archivo.py"),
    ("print(1)", "archivo.txt"), ("print(1)", "C:\\escape.py"),
])
def test_entradas_rechazadas(codigo, nombre):
    with pytest.raises(mod.EntradaEstaticaInvalida):
        mod.analizar_estatico(codigo, nombre)


def test_json_ruff_invalido_es_error_parcial(monkeypatch):
    monkeypatch.setattr(
        mod, "_ejecutar",
        lambda comando, **kw: ("ok", "no-json" if "ruff" in comando else '{"results": []}')
    )
    resultado = mod.analizar_estatico("print('ok')")
    assert resultado.estado == "parcial"
    assert resultado.herramientas[0].estado == "error"


def test_linea_bandit_fuera_de_rango_no_se_acepta(monkeypatch):
    datos = {"results": [{**BANDIT["results"][0], "line_number": 999}]}
    monkeypatch.setattr(
        mod, "_ejecutar",
        lambda comando, **kw: ("ok", "[]" if "ruff" in comando else json.dumps(datos))
    )
    resultado = mod.analizar_estatico("print(1)")
    assert resultado.herramientas[1].estado == "error"
    assert resultado.hallazgos == []


def test_subprocess_usa_shell_false_y_timeout(monkeypatch, tmp_path):
    argumentos = {}

    def falso_run(comando, **kwargs):
        argumentos.update(kwargs)
        return subprocess.CompletedProcess(comando, 0, stdout="[]", stderr="")

    monkeypatch.setattr(mod.subprocess, "run", falso_run)
    status, salida = mod._ejecutar(["python", "-m", "ruff"], cwd=str(tmp_path))
    assert status == "ok"
    assert salida == "[]"
    assert argumentos["shell"] is False
    assert argumentos["timeout"] == mod.TOOL_TIMEOUT
    assert argumentos["cwd"] == str(tmp_path)
    assert argumentos["env"]["HOME"] == str(tmp_path)


def test_timeout_y_module_no_disponible(monkeypatch, tmp_path):
    def lento(comando, **kwargs):
        raise subprocess.TimeoutExpired(comando, kwargs["timeout"])
    monkeypatch.setattr(mod.subprocess, "run", lento)
    assert mod._ejecutar(["ruff"], cwd=str(tmp_path))[0] == "timeout"

    def ausente(comando, **kwargs):
        return subprocess.CompletedProcess(
            comando, 1, stdout="", stderr="No module named ruff"
        )
    monkeypatch.setattr(mod.subprocess, "run", ausente)
    assert mod._ejecutar(["python", "-m", "ruff"], cwd=str(tmp_path))[0] == "no_disponible"


def test_directorio_temporal_se_elimina(monkeypatch):
    rutas = []

    def falso(comando, *, entrada=None, cwd):
        rutas.append(cwd)
        return "ok", "[]" if "ruff" in comando else '{"results":[]}'
    monkeypatch.setattr(mod, "_ejecutar", falso)
    mod.analizar_estatico("print(1)")
    from pathlib import Path
    assert rutas[0] == rutas[1]
    assert not Path(rutas[0]).exists()


def test_no_toma_reglas_de_seguridad_de_ruff(monkeypatch):
    argumentos = simular_ambos(monkeypatch)
    mod.analizar_estatico("import os\nprint(1)")
    comando_ruff = argumentos[0][0]
    assert "--select" in comando_ruff
    assert "E4,E7,E9,F" in comando_ruff
    assert "--isolated" in comando_ruff


def test_resumen_solo_guardado_si_herramienta_respondio(monkeypatch):
    def falso(comando, **kwargs):
        if "bandit" in comando:
            return "error", None
        return "ok", json.dumps(RUFF)
    monkeypatch.setattr(mod, "_ejecutar", falso)
    resultado = mod.analizar_estatico("import os\nprint(1)")
    assert resultado.estado == "parcial"
    assert len(resultado.hallazgos) == 1
    assert resultado.herramientas[1].hallazgos == 0


def test_ruff_real_detecta_import_no_usado():
    import importlib.util
    if importlib.util.find_spec("ruff") is None:
        pytest.skip("Ruff no está instalado en este entorno")
    codigo = "import os\\nprint('hola')\\n".replace("\\\\n", "\\n")
    with __import__("tempfile").TemporaryDirectory() as temp:
        estado, stdout = mod._ejecutar(
            [__import__("sys").executable, "-m", "ruff", "check", "--isolated",
             "--select", "F", "--output-format", "json",
             "--stdin-filename", "codigo.py", "-"],
            entrada=codigo,
            cwd=temp,
        )
    assert estado == "ok"
    assert any(h["code"] == "F401" for h in json.loads(stdout))


def test_bandit_real_detecta_eval_sin_ejecutarlo():
    import importlib.util
    if importlib.util.find_spec("bandit") is None:
        pytest.skip("Bandit no está instalado en este entorno")
    resultado = mod.analizar_estatico("eval(input())\\n".replace("\\\\n", "\\n"))
    bandit = next(h for h in resultado.herramientas if h.herramienta == "bandit")
    assert bandit.estado == "ok"
    assert any(h.herramienta == "bandit" and h.regla == "B307" for h in resultado.hallazgos)
