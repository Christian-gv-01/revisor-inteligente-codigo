"""Procesos controlados del test; nunca se ejecuta el código recibido por la API."""
import subprocess
import sys
from pathlib import Path
import time

import pytest

from app.services import static_analysis as motor


def test_importacion_estatica_no_requiere_clientes_de_ia():
    codigo = '''
import importlib.abc
import sys
class SinIA(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "httpx" or fullname == "google" or fullname.startswith("google."):
            raise ModuleNotFoundError("Dependencia de IA no disponible: " + fullname)
sys.meta_path.insert(0, SinIA())
from app.services import static_analysis
assert static_analysis.TOOL_TIMEOUT > 0
'''
    proceso = subprocess.run([sys.executable, "-c", codigo],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=15)
    assert proceso.returncode == 0, proceso.stderr


def ejecutar(script, tmp_path, entrada=None):
    return motor._ejecutar([sys.executable, "-I", "-c", script], entrada=entrada, cwd=str(tmp_path))


@pytest.mark.parametrize("canal", ["stdout", "stderr"])
def test_exceso_mata_hijo_antes_de_terminar_su_salida(monkeypatch, tmp_path, canal):
    monkeypatch.setattr(motor, "MAX_STDOUT", 8192)
    monkeypatch.setattr(motor, "TOOL_TIMEOUT", 3)
    procesos = []
    crear = subprocess.Popen

    def registrar(*args, **kwargs):
        proceso = crear(*args, **kwargs)
        procesos.append(proceso)
        return proceso

    monkeypatch.setattr(motor.subprocess, "Popen", registrar)
    script = (
        "import sys; from pathlib import Path\n"
        f"salida=sys.{canal}.buffer\n"
        "for _ in range(10000):\n"
        " salida.write(b'x'*4096); salida.flush()\n"
        "Path('no_debe_terminar.txt').write_text('fin')\n"
    )
    assert ejecutar(script, tmp_path) == ("error", None)
    assert not (tmp_path / "no_debe_terminar.txt").exists()
    assert procesos and all(p.poll() is not None for p in procesos)


def test_limite_se_comparte_entre_stdout_y_stderr(monkeypatch, tmp_path):
    monkeypatch.setattr(motor, "MAX_STDOUT", 8192)
    script = "import sys; sys.stdout.buffer.write(b'x'*5000); sys.stdout.flush(); sys.stderr.buffer.write(b'y'*5000)"
    assert ejecutar(script, tmp_path) == ("error", None)


def test_frontera_exacta_y_stderr_privado(monkeypatch, tmp_path):
    monkeypatch.setattr(motor, "MAX_STDOUT", 1000)
    estado, salida = ejecutar("import sys; sys.stdout.write('x'*700); sys.stderr.write('y'*300)", tmp_path)
    assert (estado, salida) == ("ok", "x"*700)


def test_limite_cuenta_bytes_utf8(monkeypatch, tmp_path):
    monkeypatch.setattr(motor, "MAX_STDOUT", 1000)
    assert ejecutar("import sys; sys.stdout.buffer.write(bytes([195,169])*501)", tmp_path) == ("error", None)


def test_timeout_mata_y_recolecta_hijo(monkeypatch, tmp_path):
    monkeypatch.setattr(motor, "TOOL_TIMEOUT", 0.3)
    procesos = []
    crear = subprocess.Popen

    def registrar(*args, **kwargs):
        proceso = crear(*args, **kwargs)
        procesos.append(proceso)
        return proceso

    monkeypatch.setattr(motor.subprocess, "Popen", registrar)
    inicio = time.monotonic()
    assert ejecutar("import time; time.sleep(10)", tmp_path) == ("timeout", None)
    assert time.monotonic() - inicio < 5
    assert procesos and all(p.poll() is not None for p in procesos)


def test_drena_dos_canales_y_lee_stdin_sin_bloquear(tmp_path):
    script = (
        "import sys\n"
        "sys.stdout.write('x'*100000); sys.stdout.flush()\n"
        "sys.stderr.write('y'*100000); sys.stderr.flush()\n"
        "assert sys.stdin.read() == 'dato'*3000\n"
    )
    assert ejecutar(script, tmp_path, entrada="dato"*3000) == ("ok", "x"*100000)
