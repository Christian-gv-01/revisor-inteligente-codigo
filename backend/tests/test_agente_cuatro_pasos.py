"""Regresiones del cuarto paso y de contexto: cero llamadas externas."""
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.models.analisis import InformeModelo
from app.services import agente, llm
from app.services.herramientas_contextuales import ArgumentosLinea, ArgumentosCategoria, ampliar_contexto
from app.services.static_analysis import ResultadoEstatico


def test_cuarto_paso_llega_a_la_sintesis_y_no_inicia_quinta_decision(monkeypatch):
    codigo = "\n".join(f"valor_{i} = {i}" for i in range(1, 21))
    decisiones = iter([
        {"herramienta": "ampliar_contexto", "motivo": "Revisar primera ubicación", "argumentos": {"linea": 8}},
        {"herramienta": "ampliar_contexto", "motivo": "Revisar otra ubicación", "argumentos": {"linea": 9}},
        {"herramienta": "ampliar_contexto", "motivo": "Revisar última ubicación", "argumentos": {"linea": 10}},
    ])
    plan = Mock(side_effect=lambda c, p: next(decisiones))
    evidencias = []
    def sintetizar(c, *, evidencia):
        evidencias.append(evidencia)
        return InformeModelo(hallazgos=[])
    monkeypatch.setattr(llm, "analizar_codigo", sintetizar)
    s = agente.SolicitudAgente(archivo="ejemplo.py", codigo=codigo, max_pasos=4, version_herramientas="2")
    r = agente.ejecutar_agente(s, planificador=plan, inspeccion_estatica=lambda c, a:
        ResultadoEstatico(archivo=a, estado="completo", hallazgos=[], herramientas=[]))
    assert [p.numero for p in r.pasos] == [1, 2, 3, 4]
    assert [d.numero for d in r.decisiones] == [1, 2, 3]
    assert r.terminacion == "max_pasos" and plan.call_count == 3
    assert [v.linea_objetivo for v in evidencias[0].contextos_ampliados] == [8, 9, 10]
    assert len(evidencias[0].contextos_ampliados[-1].lineas) == 13


@pytest.mark.parametrize("linea,inicio,fin", [(1, 1, 7), (10, 4, 16), (20, 14, 20)])
def test_contexto_seis_lineas_por_lado_sin_inventar_lineas(linea, inicio, fin):
    codigo = "\n".join(f"dato_{i} = {i}" for i in range(1, 21))
    r = ampliar_contexto(codigo, ArgumentosLinea(linea=linea))
    assert (r.linea_inicio, r.linea_fin) == (inicio, fin)
    assert [l.texto for l in r.lineas] == codigo.splitlines()[inicio - 1:fin]


def test_limite_cuatro_rechaza_cinco_y_conserva_default_tres():
    assert agente.SolicitudAgente(archivo="x.py", codigo="x=1").max_pasos == 3
    with pytest.raises(ValidationError):
        agente.SolicitudAgente(archivo="x.py", codigo="x=1", max_pasos=5, version_herramientas="2")
    assert ArgumentosCategoria(categoria="deserializacion").categoria == "deserializacion"
