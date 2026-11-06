"""El cupo se adquiere antes del proveedor y sobrevive entre conexiones SQLite."""

import hashlib
import multiprocessing
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.models.correcciones import SolicitudPrevisualizacion
from app.services import correcciones as servicio


def _generar_en_otro_proceso(ruta, payload, dentro, terminar, resultado):
    servicio.DB_PATH = ruta
    servicio.settings.MAX_PROPUESTAS = 1
    servicio.settings.MAX_PROPUESTAS_SESION = 1
    def generar(*_):
        dentro.set()
        if not terminar.wait(10):
            raise RuntimeError("No se liberó la generación de prueba")
        return "x = 2"
    servicio._generar_codigo_propuesto = generar
    try:
        servicio.crear_previsualizacion(SolicitudPrevisualizacion.model_validate(payload), "proceso")
        resultado.put("ok")
    except Exception as error:
        resultado.put(type(error).__name__)


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    monkeypatch.setattr(servicio, "DB_PATH", tmp_path / "reservas.sqlite3")
    monkeypatch.setattr(servicio.settings, "MAX_PROPUESTAS", 2)
    monkeypatch.setattr(servicio.settings, "MAX_PROPUESTAS_SESION", 1)
    monkeypatch.setattr(servicio, "_generar_codigo_propuesto", lambda *_: "x = 2")
    return SolicitudPrevisualizacion(
        archivo="ejemplo.py", codigo_original="x = 1",
        sha256_original=hashlib.sha256(b"x = 1").hexdigest(),
        objetivo={"linea": 1, "descripcion": "Corregir el valor."},
    )


def contar(tabla):
    with sqlite3.connect(servicio.DB_PATH) as conexion:
        return conexion.execute(f"SELECT count(*) FROM {tabla}").fetchone()[0]


@pytest.mark.parametrize("global_lleno", [True, False])
def test_cupo_lleno_no_invoca_proveedor(entorno, monkeypatch, global_lleno):
    servicio.crear_previsualizacion(entorno, "sesion")
    if global_lleno:
        servicio.crear_previsualizacion(entorno, "otra")
    llamadas = []
    monkeypatch.setattr(servicio, "_generar_codigo_propuesto", lambda *_: llamadas.append(1) or "x = 3")
    with pytest.raises(servicio.CorreccionError) as error:
        servicio.crear_previsualizacion(entorno, "tercera" if global_lleno else "sesion")
    assert error.value.status_code == 429
    assert llamadas == []


@pytest.mark.parametrize("misma_sesion", [True, False])
def test_ultimo_cupo_concurrente_se_reserva_sin_bloquear_proveedor(entorno, monkeypatch, misma_sesion):
    if not misma_sesion:
        monkeypatch.setattr(servicio.settings, "MAX_PROPUESTAS", 1)
    dentro, terminar = threading.Event(), threading.Event()
    llamadas = []

    def generar(*_):
        llamadas.append(1)
        dentro.set()
        assert terminar.wait(5)
        return "x = 2"

    monkeypatch.setattr(servicio, "_generar_codigo_propuesto", generar)
    with ThreadPoolExecutor(max_workers=2) as pool:
        primero = pool.submit(servicio.crear_previsualizacion, entorno, "sesion")
        assert dentro.wait(5)
        try:
            segundo = pool.submit(servicio.crear_previsualizacion, entorno, "sesion" if misma_sesion else "otra")
            with pytest.raises(servicio.CorreccionError) as error:
                segundo.result(timeout=2)
            assert error.value.status_code == 429
            assert len(llamadas) == 1
            assert contar("reservas_correccion") == 1
        finally:
            terminar.set()
        primero.result(timeout=5)
    assert contar("reservas_correccion") == 0
    assert contar("propuestas_correccion") == 1


def test_cupo_compartido_entre_procesos(entorno, monkeypatch):
    monkeypatch.setattr(servicio.settings, "MAX_PROPUESTAS", 1)
    contexto = multiprocessing.get_context("spawn")
    dentro, terminar, resultado = contexto.Event(), contexto.Event(), contexto.Queue()
    proceso = contexto.Process(target=_generar_en_otro_proceso,
                               args=(servicio.DB_PATH, entorno.model_dump(), dentro, terminar, resultado))
    proceso.start()
    try:
        assert dentro.wait(10)
        llamadas = []
        monkeypatch.setattr(servicio, "_generar_codigo_propuesto", lambda *_: llamadas.append(1) or "x = 3")
        with pytest.raises(servicio.CorreccionError) as error:
            servicio.crear_previsualizacion(entorno, "otro proceso")
        assert error.value.status_code == 429
        assert llamadas == []
    finally:
        terminar.set()
        proceso.join(10)
        if proceso.is_alive():
            proceso.terminate()
            proceso.join(5)
    assert proceso.exitcode == 0
    assert resultado.get(timeout=2) == "ok"
    assert contar("propuestas_correccion") == 1
    assert contar("reservas_correccion") == 0


@pytest.mark.parametrize("resultado", ["error", "x = ("])
def test_error_de_proveedor_o_validacion_libera_cupo(entorno, monkeypatch, resultado):
    def generar(*_):
        if resultado == "error":
            raise servicio.CorreccionError("proveedor", 503)
        return resultado
    monkeypatch.setattr(servicio, "_generar_codigo_propuesto", generar)
    with pytest.raises(servicio.CorreccionError):
        servicio.crear_previsualizacion(entorno, "sesion")
    assert contar("reservas_correccion") == 0
    monkeypatch.setattr(servicio, "_generar_codigo_propuesto", lambda *_: "x = 2")
    servicio.crear_previsualizacion(entorno, "sesion")


def test_reserva_vencida_no_publica_resultado_y_recupera_cupo(entorno, monkeypatch):
    reloj = [1000.0]
    monkeypatch.setattr(servicio.time, "time", lambda: reloj[0])
    dentro, terminar = threading.Event(), threading.Event()

    def generar(*_):
        dentro.set()
        assert terminar.wait(5)
        return "x = 2"

    monkeypatch.setattr(servicio, "_generar_codigo_propuesto", generar)
    with ThreadPoolExecutor(max_workers=1) as pool:
        anterior = pool.submit(servicio.crear_previsualizacion, entorno, "sesion")
        assert dentro.wait(5)
        try:
            reloj[0] += 181
            monkeypatch.setattr(servicio, "_generar_codigo_propuesto", lambda *_: "x = 3")
            nueva = servicio.crear_previsualizacion(entorno, "sesion")
        finally:
            terminar.set()
        with pytest.raises(servicio.CorreccionError) as error:
            anterior.result(timeout=5)
        assert error.value.status_code == 504
    assert nueva["codigo_propuesto"] == "x = 3"
    assert contar("propuestas_correccion") == 1
    assert contar("reservas_correccion") == 0


def test_limpieza_recupera_reserva_abandonada_y_no_almacena_codigo(entorno):
    conexion = servicio._conectar()
    columnas = {fila[1] for fila in conexion.execute("PRAGMA table_info(reservas_correccion)")}
    assert columnas == {"id_hash", "solicitante_hash", "caduca_en"}
    conexion.execute("INSERT INTO reservas_correccion VALUES (?, ?, ?)", ("hash", "sesion", 1))
    conexion.close()
    servicio.limpiar_caducadas()
    assert contar("reservas_correccion") == 0
    servicio.crear_previsualizacion(entorno, "sesion")


def test_ttl_de_propuesta_empieza_al_terminar_generacion(entorno, monkeypatch):
    reloj = [1000.0]
    monkeypatch.setattr(servicio.time, "time", lambda: reloj[0])
    def generar(*_):
        reloj[0] += 100
        return "x = 2"
    monkeypatch.setattr(servicio, "_generar_codigo_propuesto", generar)
    propuesta = servicio.crear_previsualizacion(entorno, "sesion")
    assert propuesta["caduca_en"] == servicio._iso_utc(1100 + servicio.TTL_PROPUESTA_SEGUNDOS)


def test_error_de_insercion_revierte_y_libera_reserva(entorno):
    conexion = servicio._conectar()
    conexion.execute("CREATE TRIGGER fallo_insert BEFORE INSERT ON propuestas_correccion "
                     "BEGIN SELECT RAISE(FAIL, 'fallo simulado'); END")
    conexion.close()
    with pytest.raises(servicio.CorreccionError) as error:
        servicio.crear_previsualizacion(entorno, "sesion")
    assert error.value.status_code == 500
    assert contar("reservas_correccion") == contar("propuestas_correccion") == 0
    with sqlite3.connect(servicio.DB_PATH) as conexion:
        conexion.execute("DROP TRIGGER fallo_insert")
    servicio.crear_previsualizacion(entorno, "sesion")


def test_fallo_liberacion_conserva_error_proveedor(entorno, monkeypatch):
    conectar = servicio._conectar
    def generar(*_):
        def conexion_fallida():
            raise sqlite3.OperationalError("almacenamiento no disponible")
        monkeypatch.setattr(servicio, "_conectar", conexion_fallida)
        raise servicio.CorreccionError("error significativo proveedor", 503)
    monkeypatch.setattr(servicio, "_generar_codigo_propuesto", generar)
    with pytest.raises(servicio.CorreccionError, match="error significativo proveedor") as error:
        servicio.crear_previsualizacion(entorno, "sesion")
    assert error.value.status_code == 503
    monkeypatch.setattr(servicio, "_conectar", conectar)
    assert contar("reservas_correccion") == 1  # Se recupera por caducidad.


def test_migracion_bd_legacy_y_recuperacion_tombstone(entorno, monkeypatch):
    # Esquema previo a la asociación de propuestas con una sesión.
    with sqlite3.connect(servicio.DB_PATH) as conexion:
        conexion.execute("""CREATE TABLE propuestas_correccion (
            id_hash TEXT PRIMARY KEY, archivo_original TEXT NOT NULL,
            archivo_salida TEXT NOT NULL, sha256_original TEXT NOT NULL,
            sha256_propuesto TEXT NOT NULL, codigo_propuesto TEXT NOT NULL,
            advertencias_json TEXT NOT NULL, caduca_en REAL NOT NULL,
            estado TEXT NOT NULL, creada_en REAL NOT NULL)""")
        conexion.execute("INSERT INTO propuestas_correccion VALUES "
                         "('legacy', 'a.py', 'b.py', '', '', 'x = 1', '[]', 999, 'pendiente_confirmacion', 998)")
    monkeypatch.setattr(servicio.time, "time", lambda: 1000.0)
    monkeypatch.setattr(servicio.settings, "MAX_PROPUESTAS", 1)
    servicio.crear_previsualizacion(entorno, "sesion")
    assert contar("propuestas_correccion") == 1
    assert contar("reservas_correccion") == 0
    with sqlite3.connect(servicio.DB_PATH) as conexion:
        assert conexion.execute("SELECT solicitante_hash FROM propuestas_correccion").fetchone()[0] == "sesion"
