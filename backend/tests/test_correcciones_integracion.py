"""Regresiones de aislamiento, límites y decisiones simultáneas; sin Gemini."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import sqlite3

from fastapi.testclient import TestClient
import pytest

from app.config import settings
from app.main import app
from app.services import correcciones
from app.models.correcciones import SolicitudDecision
from types import SimpleNamespace

ORIGINAL = 'dato = input()\nprint(dato)\n'
PROPUESTA = 'dato = input()\nprint(repr(dato))\n'


@pytest.fixture
def cliente(monkeypatch, tmp_path):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CORRECTIONS_COOKIE_SECURE", "0")
    monkeypatch.setattr(correcciones, "DB_PATH", tmp_path / "propuestas.sqlite3")
    monkeypatch.setattr(correcciones, "_generar_codigo_propuesto", lambda *_: PROPUESTA)
    return TestClient(app)


def crear(cliente):
    r = cliente.post('/api/v1/correcciones/previsualizar', json={
        'archivo': 'ejemplo.py', 'codigo_original': ORIGINAL,
        'sha256_original': hashlib.sha256(ORIGINAL.encode()).hexdigest(),
        'objetivo': {'linea': 2, 'descripcion': 'Revisar impresión'},
    })
    assert r.status_code == 200
    return r


def decidir(cliente, p, decision='aprobar'):
    return cliente.post(f"/api/v1/correcciones/{p['propuesta_id']}/decision", json={
        'decision': decision, 'sha256_original': p['sha256_original'],
        'sha256_propuesto': p['sha256_propuesto'],
    })


def test_cookie_http_only_y_sin_cache(cliente):
    r = crear(cliente)
    assert 'HttpOnly' in r.headers['set-cookie']
    assert 'SameSite=strict' in r.headers['set-cookie']
    assert r.headers['cache-control'] == 'no-store'
    assert decidir(cliente, r.json()).headers['cache-control'] == 'no-store'


def test_id_y_hashes_no_autorizan_otra_sesion(cliente):
    p = crear(cliente).json()
    otro = TestClient(app)
    assert decidir(otro, p).status_code == 404
    crear(otro)
    assert decidir(otro, p).status_code == 404
    assert decidir(cliente, p).status_code == 200


def test_cookie_secure_en_produccion(cliente, monkeypatch):
    monkeypatch.setenv('CORRECTIONS_COOKIE_SECURE', '1')
    assert '; Secure' in crear(cliente).headers['set-cookie']


def test_rechazo_borra_contenido(cliente):
    p = crear(cliente).json()
    assert decidir(cliente, p, 'rechazar').status_code == 200
    with sqlite3.connect(correcciones.DB_PATH) as c:
        assert c.execute('SELECT codigo_propuesto FROM propuestas_correccion').fetchone()[0] == ''


def test_purga_sin_nuevas_previsualizaciones(cliente):
    crear(cliente)
    with sqlite3.connect(correcciones.DB_PATH) as c:
        c.execute('UPDATE propuestas_correccion SET caduca_en=1')
    correcciones.limpiar_caducadas()
    with sqlite3.connect(correcciones.DB_PATH) as c:
        assert c.execute('SELECT count(*) FROM propuestas_correccion WHERE codigo_propuesto <> ?', ('',)).fetchone()[0] == 0


def test_limite_por_sesion(cliente, monkeypatch):
    monkeypatch.setattr(settings, 'MAX_PROPUESTAS_SESION', 1)
    crear(cliente)
    r = cliente.post('/api/v1/correcciones/previsualizar', json={
        'archivo':'ejemplo.py', 'codigo_original': ORIGINAL,
        'sha256_original':hashlib.sha256(ORIGINAL.encode()).hexdigest(),
        'objetivo':{'linea':2,'descripcion':'Revisar'},
    })
    assert r.status_code == 429


def test_decisiones_contrarias_simultaneas_solo_una_gana(cliente):
    p = crear(cliente).json()
    owner = hashlib.sha256(cliente.cookies.get(settings.COOKIE_CORRECCIONES).encode()).hexdigest()
    def llamar(decision):
        try:
            correcciones.decidir_propuesta(p['propuesta_id'], SolicitudDecision(
                decision=decision, sha256_original=p['sha256_original'],
                sha256_propuesto=p['sha256_propuesto']), owner)
            return 200
        except correcciones.CorreccionError as e:
            return e.status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(llamar, ['aprobar','rechazar'])) == [200,409]


def test_error_422_no_refleja_codigo(cliente):
    marcador = 'DATO_PRIVADO_CONTROLADO'
    r = cliente.post('/api/v1/correcciones/previsualizar', json={
        'archivo':'../ejemplo.py', 'codigo_original':marcador,
        'sha256_original':'0'*64,'objetivo':{'linea':1,'descripcion':'Revisar'},
    })
    assert r.status_code == 422
    assert marcador not in r.text


def test_correcciones_tienen_presupuesto_publico(cliente, monkeypatch):
    from app.main import LimitadorPonderado
    import app.main as api
    monkeypatch.setenv('RATE_LIMIT_ENABLED','1')
    monkeypatch.setattr(api,'limitador_peticiones',LimitadorPonderado(limite_cliente=3))
    p = crear(cliente).json()
    assert decidir(cliente,p).status_code == 429


def test_ruta_de_propuestas_junto_al_volumen_chroma(monkeypatch):
    monkeypatch.delenv('CORRECTIONS_DB_PATH',raising=False)
    monkeypatch.setenv('CHROMA_PATH','/data/chroma')
    assert settings.obtener_ruta_correcciones().as_posix() == '/data/correcciones.sqlite3'


@pytest.mark.parametrize('motivo',['STOP','MAX_TOKENS'])
def test_generador_cierra_cliente_y_rechaza_truncamiento(monkeypatch, motivo):
    from google import genai
    monkeypatch.setenv('GEMINI_API_KEY','fixture-local')
    cerrados = []
    class Cliente:
        def __init__(self, **_): self.models = self
        def generate_content(self, **_):
            return SimpleNamespace(text=PROPUESTA, candidates=[SimpleNamespace(finish_reason=motivo)])
        def close(self): cerrados.append(True)
    monkeypatch.setattr(genai,'Client',Cliente)
    if motivo == 'MAX_TOKENS':
        with pytest.raises(correcciones.CorreccionError, match='truncada'):
            correcciones._generar_codigo_propuesto(ORIGINAL,{'linea':2})
    else:
        assert correcciones._generar_codigo_propuesto(ORIGINAL,{'linea':2}) == PROPUESTA.strip()
    assert cerrados == [True]
