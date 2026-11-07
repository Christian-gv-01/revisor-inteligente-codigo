"""Herencia con identidad explícita, sin depender de proximidad ni de orden."""
import itertools

import pytest

from app.models.analisis import Hallazgo, HerenciaSeveridad, InformeGenerativo
from app.services.evidencia import ReglaEvidencia, construir_evidencia
from app.services.herramientas_contextuales import ampliar_contexto
from app.services.severidad import heredar_severidad_contextual, identificar_regla, politica_severidad
from app.services.static_analysis import HallazgoEstatico, ResultadoEstatico


def regla(linea=10, severidad="alta", confianza="alta", codigo="B602", columna=None):
    return ReglaEvidencia(herramienta="bandit", regla=codigo, linea=linea, columna=columna,
                         severidad=severidad, confianza=confianza)


def hallazgo(linea=10, severidad="baja", ids=()):
    return Hallazgo(linea=linea, severidad=severidad, categoria="seguridad",
        titulo="Hallazgo de prueba", explicacion="Fixture controlado", correccion_sugerida="Revisar",
        referencias=["documento-sintetico"], reglas_evidencia=list(ids))


def test_regla_citada_misma_linea_eleva_y_conserva_valores_originales():
    r = regla(); original = hallazgo(ids=[r.id]); antes = original.model_dump()
    resultado = heredar_severidad_contextual([original], [r])[0]
    assert resultado.severidad == "critica" and resultado.severidad_original_modelo == "baja"
    assert original.model_dump() == antes
    assert resultado.herencia_severidad[0].model_dump() == {
        "id": r.id, "herramienta": "bandit", "regla": "B602", "linea": 10, "columna": None,
        "severidad_original": "alta", "confianza": "alta", "severidad_derivada": "critica"}
    assert resultado is not original and r.severidad == "alta"


@pytest.mark.parametrize("linea,ids", [(12, ()), (12, ("citar",)), (10, ()), (10, ("desconocida",))])
def test_no_hereda_por_cercania_ni_por_una_cita_desconocida(linea, ids):
    r = regla(); seleccion = [r.id] if ids == ("citar",) else ids
    resultado = heredar_severidad_contextual([hallazgo(linea=linea, ids=seleccion)], [r])[0]
    assert resultado.severidad == "baja"
    assert resultado.reglas_evidencia == [] and resultado.herencia_severidad == []


def test_todas_las_permutaciones_de_reglas_y_citas_dan_el_mismo_resultado():
    reglas = [regla(codigo="B602"), regla(severidad="media", codigo="B608"), regla(severidad="baja", codigo="B105")]
    esperado = None
    for orden in itertools.permutations(reglas):
        for ids in itertools.permutations([r.id for r in reglas]):
            resultado = heredar_severidad_contextual([hallazgo(ids=ids)], orden)[0].model_dump()
            esperado = esperado or resultado
            assert resultado == esperado


def test_no_reduce_critica_y_no_inventa_confianza():
    r = regla(severidad="alta", confianza=None)
    resultado = heredar_severidad_contextual([hallazgo(severidad="critica", ids=[r.id])], [r])[0]
    assert resultado.severidad == resultado.severidad_original_modelo == "critica"
    assert resultado.herencia_severidad[0].confianza is None


def test_identidades_duplicadas_con_datos_contradictorios_no_autorizan_herencia():
    a = regla(); b = regla(confianza=None)
    assert a.id == b.id
    resultado = heredar_severidad_contextual([hallazgo(ids=[a.id])], [a, b])[0]
    assert resultado.severidad == "baja" and not resultado.herencia_severidad


def test_sin_reglas_citadas_no_se_acepta_auditoria_fabricada_por_el_modelo():
    r = regla(); original = hallazgo()
    original.severidad_original_modelo = "alta"
    original.herencia_severidad = [HerenciaSeveridad(id=r.id, herramienta="bandit", regla=r.regla,
        linea=r.linea, severidad_original="alta", severidad_derivada="critica")]
    resultado = heredar_severidad_contextual([original], [r])[0]
    assert resultado.severidad == "baja"
    assert resultado.severidad_original_modelo is None and not resultado.herencia_severidad


def test_ventanas_superpuestas_preservan_ambos_vinculos_y_su_orden_no_cambia_la_herencia():
    codigo = "\n".join(f"dato_{n} = {n}" for n in range(1, 25))
    estatico = ResultadoEstatico(archivo="muestra.py", estado="completo", herramientas=[], hallazgos=[
        HallazgoEstatico(herramienta="bandit", regla="B602", tipo="seguridad", linea=10,
            severidad="alta", confianza="alta", titulo="Fixture", descripcion="Fixture")])
    salidas = []
    for orden in ([10, 11], [11, 10]):
        pasos = [{"herramienta": "ampliar_contexto", "origen": "gemini",
                  "resultado": ampliar_contexto(codigo, {"linea": n}).model_dump()} for n in orden]
        e = construir_evidencia("muestra.py", pasos, estatico)
        assert {v.linea_objetivo for v in e.vinculos_reglas_contexto} == {10, 11}
        salidas.append(heredar_severidad_contextual([hallazgo(ids=[e.reglas[0].id])], e.reglas)[0].model_dump())
    assert salidas[0] == salidas[1] and salidas[0]["severidad"] == "critica"


def test_no_hace_falta_que_el_planificador_amplie_para_heredar_regla_citada():
    r = regla()
    assert heredar_severidad_contextual([hallazgo(ids=[r.id])], [r])[0].severidad == "critica"


def test_id_distingue_columnas_y_el_esquema_generativo_no_pide_auditoria():
    assert identificar_regla("bandit", "B602", 10, 1) != identificar_regla("bandit", "B602", 10, 20)
    props = InformeGenerativo.model_json_schema()["$defs"]["HallazgoGenerativo"]["properties"]
    assert "reglas_evidencia" in props
    assert "herencia_severidad" not in props and "severidad_original_modelo" not in props


def test_matriz_cubre_severidad_confianza_y_desconocida():
    matriz = politica_severidad()
    assert set(matriz["bandit"]) == {"critica", "alta", "media", "baja"}
    assert all(set(fila) == {"alta", "media", "baja", "desconocida"} for fila in matriz["bandit"].values())
    assert matriz["bandit"]["alta"]["alta"] == "critica"
