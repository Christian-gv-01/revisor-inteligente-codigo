
from types import SimpleNamespace

import pytest

from app.models.analisis import Hallazgo
from app.services.priorizacion import priorizar_hallazgos


def crear_hallazgo(severidad, titulo, categoria=""):
    return Hallazgo.model_construct(
        linea=1,
        severidad=severidad,
        categoria=categoria,
        titulo=titulo,
        explicacion="Explicacion de prueba",
        correccion_sugerida="Correccion de prueba",
        referencias=[],
    )


def test_prioriza_por_severidad():
    baja = crear_hallazgo("baja", "Baja")
    critica = crear_hallazgo("critica", "Critica")
    media = crear_hallazgo("media", "Media")
    alta = crear_hallazgo("alta", "Alta")

    resultado = priorizar_hallazgos(
        [baja, critica, media, alta]
    )

    assert resultado == [critica, alta, media, baja]


def test_conserva_orden_original_en_empates():
    primero = crear_hallazgo("alta", "Primero")
    segundo = crear_hallazgo("alta", "Segundo")
    tercero = crear_hallazgo("critica", "Tercero")

    resultado = priorizar_hallazgos(
        [primero, segundo, tercero]
    )

    assert resultado[0] is tercero
    assert resultado[1] is primero
    assert resultado[2] is segundo


def test_prioriza_seguridad_antes_que_calidad_en_empates():
    calidad = crear_hallazgo(
        "alta", "Problema de calidad", "calidad"
    )

    sql = crear_hallazgo(
        "alta", "Inyeccion SQL", "Inyección SQL"
    )

    credenciales = crear_hallazgo(
        "alta", "Credenciales", "Credenciales"
    )

    resultado = priorizar_hallazgos(
        [calidad, sql, credenciales]
    )

    assert resultado == [sql, credenciales, calidad]


def test_severidad_prevalece_sobre_categoria():
    calidad_critica = crear_hallazgo(
        "critica", "Problema crítico", "calidad"
    )

    seguridad_alta = crear_hallazgo(
        "alta", "Problema de seguridad", "seguridad"
    )

    resultado = priorizar_hallazgos(
        [seguridad_alta, calidad_critica]
    )

    assert resultado == [calidad_critica, seguridad_alta]


def test_normaliza_categoria_y_acentos():
    calidad = crear_hallazgo(
        "alta", "Calidad", "calidad"
    )

    ejecucion = crear_hallazgo(
        "alta", "Ejecución", "EJECUCIÓN ARBITRARIA"
    )

    resultado = priorizar_hallazgos(
        [calidad, ejecucion]
    )

    assert resultado == [ejecucion, calidad]


def test_categoria_desconocida_no_se_clasifica_como_seguridad():
    desconocida = crear_hallazgo(
        "alta", "Desconocido", "categoria_nueva"
    )

    seguridad = crear_hallazgo(
        "alta", "Seguridad", "seguridad"
    )

    resultado = priorizar_hallazgos(
        [desconocida, seguridad]
    )

    assert resultado == [seguridad, desconocida]


def test_lista_vacia():
    assert priorizar_hallazgos([]) == []


def test_no_modifica_lista_original():
    baja = crear_hallazgo("baja", "Baja")
    critica = crear_hallazgo("critica", "Critica")

    original = [baja, critica]

    resultado = priorizar_hallazgos(original)

    assert original[0] is baja
    assert original[1] is critica
    assert resultado is not original


def test_rechaza_severidad_desconocida():
    invalido = crear_hallazgo(
        "desconocida", "Invalido"
    )

    with pytest.raises(ValueError):
        priorizar_hallazgos([invalido])



def crear_hallazgo_confianza(severidad, titulo, confianza, categoria="calidad"):
    return SimpleNamespace(
        severidad=severidad,
        titulo=titulo,
        confianza=confianza,
        categoria=categoria,
    )


def test_confianza_orden_descendente_y_desconocida_despues():
    baja = crear_hallazgo_confianza("alta", "LOW", "baja")
    desconocida = crear_hallazgo_confianza("alta", "UNKNOWN", None)
    media = crear_hallazgo_confianza("alta", "MEDIUM", "media")
    alta = crear_hallazgo_confianza("alta", "HIGH", "alta")

    resultado = priorizar_hallazgos([baja, desconocida, media, alta])

    assert [h.titulo for h in resultado] == [
        "HIGH", "MEDIUM", "LOW", "UNKNOWN"
    ]


def test_severidad_prevalece_sobre_confianza():
    critica = crear_hallazgo_confianza("critica", "CRITICA", None)
    alta = crear_hallazgo_confianza("alta", "ALTA", "alta")

    resultado = priorizar_hallazgos([alta, critica])

    assert resultado == [critica, alta]


def test_desconocidos_conservan_categoria_y_orden_estable():
    calidad_1 = crear_hallazgo_confianza(
        "alta", "CALIDAD 1", None, "calidad"
    )
    seguridad = crear_hallazgo_confianza(
        "alta", "SEGURIDAD", None, "seguridad"
    )
    calidad_2 = crear_hallazgo_confianza(
        "alta", "CALIDAD 2", None, "calidad"
    )

    resultado = priorizar_hallazgos(
        [calidad_1, seguridad, calidad_2]
    )

    assert [h.titulo for h in resultado] == [
        "SEGURIDAD", "CALIDAD 1", "CALIDAD 2"
    ]
