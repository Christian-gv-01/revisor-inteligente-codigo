"""Una búsqueda elegida por el planificador no debe borrar la recuperación base."""
from unittest.mock import Mock

from app.services import llm, rag
from app.services.evidencia import EvidenciaRevision
from app.services.herramientas_contextuales import ResultadoReferencia


def fuente(numero):
    return {"id": f"seguridad_python-{numero:03}", "texto": f"Documento {numero}",
            "area": "seguridad", "distancia": 0.1}


def evidencia(*numeros):
    return EvidenciaRevision(archivo="ejemplo.py", inspecciones=[], estado_estatico="completo",
        reglas=[], total_reglas=0, referencias_buscadas=[
        ResultadoReferencia(categoria="ejecucion_codigo", fragmentos=[fuente(n) for n in numeros])])


def test_busqueda_impertinente_no_elimina_la_fuente_base_eval(monkeypatch):
    consulta = Mock(return_value=[fuente(1)])
    monkeypatch.setattr(rag, "buscar_fragmentos", consulta)
    contexto, fuentes = llm._recuperar_contexto_agente("eval(input())", evidencia(5, 3))
    assert {f["id"] for f in fuentes} == {"seguridad_python-001", "seguridad_python-005", "seguridad_python-003"}
    assert "Documento 1" in contexto
    consulta.assert_called_once()


def test_busqueda_conserva_fuentes_elegidas_sin_duplicar_la_base(monkeypatch):
    monkeypatch.setattr(rag, "buscar_fragmentos", lambda *a, **k: [fuente(1), fuente(2)])
    _, fuentes = llm._recuperar_contexto_agente("eval(input())", evidencia(1, 3))
    assert [f["id"] for f in fuentes] == ["seguridad_python-001", "seguridad_python-002", "seguridad_python-003"]


def test_union_no_excede_seis_ni_desplaza_las_tres_fuentes_base(monkeypatch):
    monkeypatch.setattr(rag, "buscar_fragmentos", lambda *a, **k: [fuente(n) for n in (1, 2, 3)])
    e = evidencia(4, 5)
    e.referencias_buscadas.append(ResultadoReferencia(categoria="inyeccion_sql", fragmentos=[fuente(6), fuente(7)]))
    _, fuentes = llm._recuperar_contexto_agente("eval(input())", e)
    assert len(fuentes) == 6
    assert [f["id"] for f in fuentes[:3]] == ["seguridad_python-001", "seguridad_python-002", "seguridad_python-003"]


def test_sin_fuentes_base_conserva_la_busqueda_real(monkeypatch):
    monkeypatch.setattr(rag, "buscar_fragmentos", lambda *a, **k: [])
    _, fuentes = llm._recuperar_contexto_agente("eval(input())", evidencia(1))
    assert [f["id"] for f in fuentes] == ["seguridad_python-001"]
