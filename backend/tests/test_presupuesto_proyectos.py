"""Autorización de consumo: HTTP real, SQLite real, proveedor sustituido sin red."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import json
import threading
import zipfile

from fastapi.testclient import TestClient
import pytest

from app import main
from app.models.analisis import RespuestaAnalisis
from app.routes import proyectos as rutas
from app.services import proyectos as p


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("PROJECT_BUDGET_ENABLED", "1")
    monkeypatch.setenv("CORRECTIONS_COOKIE_SECURE", "0")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "0")
    monkeypatch.setattr(p, "DB_PATH", tmp_path / "presupuestos.sqlite3")
    llamadas = []

    async def analizar(codigo, archivo, **kwargs):
        llamadas.append((archivo, codigo, kwargs))
        return RespuestaAnalisis(archivo=archivo, estado="analizado", hallazgos=[])
    monkeypatch.setattr(main, "analizar_con_respaldo", analizar)
    return TestClient(main.app), llamadas


def zip_bytes(archivos=None):
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w") as z:
        for nombre, codigo in (archivos or {"uno.py": "print(1)\n"}).items():
            z.writestr(nombre, codigo)
    return stream.getvalue()


def previa(cliente, archivos=None):
    respuesta = cliente.post("/api/v1/proyectos/previsualizar/zip",
        files={"archivo": ("caso.zip", zip_bytes(archivos), "application/zip")})
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def decidir(cliente, propuesta, decision="aprobar", **cambios):
    cuerpo = {"decision": decision, "confirmar": decision == "aprobar",
              "sha256_manifiesto": propuesta["sha256_manifiesto"], **cambios}
    return cliente.post(f"/api/v1/proyectos/{propuesta['presupuesto_id']}/decision", json=cuerpo)


def test_previa_no_consulta_y_hashes_corresponden(entorno):
    cliente, llamadas = entorno
    propuesta = previa(cliente, {"dos.py": "print(2)\n", "uno.py": "print(1)\n"})
    assert llamadas == []
    assert propuesta["presupuesto"]["max_intentos_proveedor"] == 2 * p.settings.obtener_intentos_llm()
    nucleo = {k: propuesta[k] for k in ("tipo", "origen", "sha256_entrada", "archivos", "total_archivos", "presupuesto")}
    assert propuesta["sha256_manifiesto"] == p.huella(p.canon(nucleo))
    assert propuesta["archivos"][0]["sha256"] == p.huella("print(2)\n")
    assert "print(2)" not in json.dumps(propuesta)
    cookie = cliente.cookies.get(p.COOKIE)
    with p.conexion() as db:
        assert db.execute("SELECT propietario FROM proyectos").fetchone()[0] == p.huella(cookie)


def test_aprobacion_repetida_no_duplica_consumo_y_borra_codigo(entorno):
    cliente, llamadas = entorno
    propuesta = previa(cliente)
    uno = decidir(cliente, propuesta)
    dos = decidir(cliente, propuesta)
    assert uno.status_code == dos.status_code == 200
    assert uno.json() == dos.json()
    assert len(llamadas) == 1
    assert decidir(cliente, propuesta, "rechazar").status_code == 409
    with p.conexion() as db:
        assert db.execute("SELECT snapshot FROM proyectos").fetchone() == (None,)


def test_rechazar_es_idempotente_sin_consumo(entorno):
    cliente, llamadas = entorno
    propuesta = previa(cliente)
    assert decidir(cliente, propuesta, "rechazar").json()["estado"] == "rechazado"
    assert decidir(cliente, propuesta, "rechazar").status_code == 200
    assert decidir(cliente, propuesta).status_code == 409
    assert llamadas == []


@pytest.mark.parametrize("cambio,codigo", [
    ({"confirmar": False}, 422), ({"confirmar": "true"}, 422),
    ({"sha256_manifiesto": "0" * 64}, 409), ({"extra": "dato"}, 422)])
def test_consentimiento_y_manifiesto_no_eludibles(entorno, cambio, codigo):
    cliente, llamadas = entorno
    assert decidir(cliente, previa(cliente), **cambio).status_code == codigo
    assert llamadas == []


def test_otra_sesion_no_puede_utilizar_propuesta(entorno):
    cliente, llamadas = entorno
    propuesta = previa(cliente)
    ajeno = TestClient(main.app)
    assert decidir(ajeno, propuesta).status_code == 404
    previa(ajeno)
    assert decidir(ajeno, propuesta).status_code == 404
    assert llamadas == []


def test_caducidad_y_limpieza(entorno):
    cliente, llamadas = entorno
    propuesta = previa(cliente)
    with p.conexion() as db:
        db.execute("UPDATE proyectos SET caduca=0")
    assert decidir(cliente, propuesta).status_code == 410
    p.limpiar()
    with p.conexion() as db:
        assert db.execute("SELECT count(*) FROM proyectos").fetchone()[0] == 0
    assert llamadas == []


def test_cambio_configuracion_exige_otro_presupuesto(entorno, monkeypatch):
    cliente, llamadas = entorno
    propuesta = previa(cliente)
    monkeypatch.setenv("GEMINI_MODEL", "otro-modelo")
    assert decidir(cliente, propuesta).status_code == 409
    assert llamadas == []


def test_github_aprueba_instantanea_sin_descargar_de_nuevo(entorno, monkeypatch):
    cliente, llamadas = entorno
    descargas = []
    def obtener(url):
        descargas.append(url)
        return [("src/caso.py", "print('original')")]
    monkeypatch.setattr(rutas, "obtener_archivos_python_github", obtener)
    propuesta = cliente.post("/api/v1/proyectos/previsualizar/github", json={"url": "https://github.com/grupo/caso"}).json()
    assert llamadas == []
    monkeypatch.setattr(rutas, "obtener_archivos_python_github", lambda _: pytest.fail("Segunda descarga"))
    assert decidir(cliente, propuesta).status_code == 200
    assert len(descargas) == 1
    assert llamadas[0][1] == "print('original')"


def test_rutas_anteriores_bloqueadas_con_funcion_activa(entorno):
    cliente, llamadas = entorno
    assert cliente.post("/api/v1/archivos/zip", files={"archivo": ("caso.zip", zip_bytes())}).status_code == 428
    assert cliente.post("/api/v1/repositorios/github", json={"url": "https://github.com/grupo/caso"}).status_code == 428
    assert cliente.post("/api/v1/repositorios/github", json={"url": "http://github.com/grupo/caso"}).status_code == 400
    assert cliente.post("/api/v1/archivos/zip", files={"archivo": ("caso.zip", b"roto")}).status_code == 400
    assert llamadas == []


def test_flag_apagado_preserva_rutas_anteriores(entorno, monkeypatch):
    cliente, llamadas = entorno
    monkeypatch.setenv("PROJECT_BUDGET_ENABLED", "0")
    assert cliente.post("/api/v1/proyectos/previsualizar/zip", files={"archivo": ("caso.zip", zip_bytes())}).status_code == 404
    assert cliente.post("/api/v1/archivos/zip", files={"archivo": ("caso.zip", zip_bytes())}).status_code == 200
    assert len(llamadas) == 1


def test_fallo_consume_permiso_y_no_regenera(entorno, monkeypatch):
    cliente, llamadas = entorno
    from app.services.llm import LLMError
    async def fallar(*args, **kwargs):
        llamadas.append("fallo")
        raise LLMError("Proveedor no disponible", 503)
    monkeypatch.setattr(main, "analizar_con_respaldo", fallar)
    propuesta = previa(cliente)
    assert decidir(cliente, propuesta).status_code == 503
    assert decidir(cliente, propuesta).status_code == 409
    assert len(llamadas) == 1
    with p.conexion() as db:
        assert db.execute("SELECT estado,snapshot FROM proyectos").fetchone() == ("fallido", None)


def test_dos_aprobaciones_concurrentes_solo_generan_una_vez(entorno, monkeypatch):
    cliente, llamadas = entorno
    entro, liberar = threading.Event(), threading.Event()
    async def lento(codigo, archivo, **kwargs):
        llamadas.append(archivo)
        entro.set()
        await asyncio.to_thread(liberar.wait, 5)
        return RespuestaAnalisis(archivo=archivo, estado="analizado", hallazgos=[])
    monkeypatch.setattr(main, "analizar_con_respaldo", lento)
    propuesta = previa(cliente)
    segundo = TestClient(main.app)
    segundo.cookies.update(cliente.cookies)
    with ThreadPoolExecutor(2) as pool:
        futuro = pool.submit(decidir, cliente, propuesta)
        assert entro.wait(5)
        try:
            assert decidir(segundo, propuesta).status_code == 409
        finally:
            liberar.set()
        assert futuro.result(timeout=5).status_code == 200
    assert len(llamadas) == 1


def test_cuota_de_instantaneas_limitada(entorno, monkeypatch):
    cliente, llamadas = entorno
    monkeypatch.setattr(p, "MAX_SESION", 1)
    previa(cliente)
    respuesta = cliente.post("/api/v1/proyectos/previsualizar/zip", files={"archivo": ("caso.zip", zip_bytes())})
    assert respuesta.status_code == 429
    assert llamadas == []


def test_presupuesto_aprobado_limita_intentos_reales_del_sdk(entorno, monkeypatch):
    cliente, _ = entorno
    from google.genai import types
    from unittest.mock import Mock
    from app.services import presupuesto
    sdk = Mock()
    sdk.models.generate_content.return_value = "ok"
    monkeypatch.setenv("LLM_RETRY_ATTEMPTS", "1")
    async def consumir(codigo, archivo, **kwargs):
        for _ in range(2):
            try:
                presupuesto.generar_con_presupuesto(sdk, model="fixture", contents=codigo,
                    config=types.GenerateContentConfig(), timeout_ms=1000)
            except presupuesto.ConsumoAgotado:
                break
        return RespuestaAnalisis(archivo=archivo, estado="analizado", hallazgos=[])
    monkeypatch.setattr(main, "analizar_con_respaldo", consumir)
    propuesta = previa(cliente)
    assert propuesta["presupuesto"]["max_intentos_proveedor"] == 1
    assert decidir(cliente, propuesta).status_code == 200
    assert sdk.models.generate_content.call_count == 1


def test_vencimiento_durante_ejecucion_no_publica_y_no_regenera(entorno, monkeypatch):
    cliente, llamadas = entorno
    async def vencido(codigo, archivo, **kwargs):
        llamadas.append(archivo)
        with p.conexion() as db:
            db.execute("UPDATE proyectos SET caduca=0")
        return RespuestaAnalisis(archivo=archivo, estado="analizado", hallazgos=[])
    monkeypatch.setattr(main, "analizar_con_respaldo", vencido)
    propuesta = previa(cliente)
    assert decidir(cliente, propuesta).status_code == 410
    assert decidir(cliente, propuesta).status_code == 410
    assert len(llamadas) == 1


def test_parcial_con_fuentes_no_cancela_ia_del_siguiente_archivo(entorno, monkeypatch):
    cliente, llamadas = entorno
    async def parcial(codigo, archivo, **kwargs):
        llamadas.append(kwargs["omitir_ia"])
        return RespuestaAnalisis(archivo=archivo, estado="parcial", hallazgos=[], fuentes=[{"id": "fuente-controlada"}])
    monkeypatch.setattr(main, "analizar_con_respaldo", parcial)
    propuesta = previa(cliente, {"uno.py": "print(1)", "dos.py": "print(2)"})
    assert decidir(cliente, propuesta).json()["resultado"]["estado"] == "parcial"
    assert llamadas == [False, False]
