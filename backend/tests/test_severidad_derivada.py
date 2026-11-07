import pytest

from app.services.evidencia import ReglaEvidencia, construir_evidencia
from app.services.static_analysis import HallazgoEstatico, ResultadoEstatico
from app.services.herramientas_contextuales import ResultadoContexto

from app.services.severidad import (
    derivar_severidad,
    combinar_severidades,
)


@pytest.mark.parametrize(
    "herramienta,severidad,confianza,esperada",
    [
        ("bandit", "alta", "alta", "critica"),
        ("bandit", "alta", "media", "alta"),
        ("bandit", "alta", "baja", "alta"),
        ("bandit", "media", "alta", "media"),
        ("bandit", "baja", "alta", "baja"),
        ("bandit", "critica", "alta", "critica"),
        ("bandit", "alta", None, "alta"),
        ("ruff", "alta", "alta", "alta"),
        ("ruff", "baja", None, "baja"),
    ],
)
def test_derivacion_severidad(
    herramienta, severidad, confianza, esperada
):
    assert derivar_severidad(
        herramienta, severidad, confianza
    ) == esperada


def test_herencia_eleva_severidad_al_maximo():
    assert combinar_severidades(
        "alta", ["critica"]
    ) == "critica"


def test_herencia_no_reduce_severidad_original():
    assert combinar_severidades(
        "critica", ["alta", "media"]
    ) == "critica"


def test_sin_reglas_vinculadas_conserva_severidad():
    assert combinar_severidades("media") == "media"


def test_varias_reglas_conservan_la_mas_alta():
    assert combinar_severidades(
        "baja", ["media", "critica", "alta"]
    ) == "critica"

def test_regla_evidencia_deriva_severidad_al_validarse():
    regla = ReglaEvidencia(
        herramienta="bandit",
        regla="B602",
        linea=10,
        severidad="alta",
        confianza="alta",
    )

    assert regla.severidad == "alta"
    assert regla.confianza == "alta"
    assert regla.severidad_derivada == "critica"


def test_construir_evidencia_transfiere_confianza_y_derivacion():
    hallazgo = HallazgoEstatico(
        herramienta="bandit",
        regla="B602",
        tipo="seguridad",
        linea=10,
        severidad="alta",
        titulo="Uso de subprocess",
        descripcion="Prueba de severidad derivada",
        confianza="alta",
    )

    estatico = ResultadoEstatico(
        archivo="muestra.py",
        estado="completo",
        hallazgos=[hallazgo],
        herramientas=[],
    )

    evidencia = construir_evidencia("muestra.py", [], estatico)

    regla = evidencia.reglas[0]

    assert regla.severidad == "alta"
    assert regla.confianza == "alta"
    assert regla.severidad_derivada == "critica"

    # Verificar que ambos valores llegan a la serializacion.
    datos = evidencia.model_dump()

    assert datos["reglas"][0]["severidad"] == "alta"
    assert datos["reglas"][0]["severidad_derivada"] == "critica"


def test_ruff_no_recibe_severidad_derivada_por_confianza():
    hallazgo = HallazgoEstatico(
        herramienta="ruff",
        regla="F821",
        tipo="calidad",
        linea=5,
        severidad="alta",
        titulo="Variable no definida",
        descripcion="Prueba de Ruff",
        confianza=None,
    )

    estatico = ResultadoEstatico(
        archivo="muestra.py",
        estado="completo",
        hallazgos=[hallazgo],
        herramientas=[],
    )

    evidencia = construir_evidencia("muestra.py", [], estatico)

    regla = evidencia.reglas[0]

    assert regla.confianza is None
    assert regla.severidad == "alta"
    assert regla.severidad_derivada == "alta"


def test_bandit_confianza_media_no_eleva_severidad():
    regla = ReglaEvidencia(
        herramienta="bandit",
        regla="B602",
        linea=10,
        severidad="alta",
        confianza="media",
    )

    assert regla.severidad == "alta"
    assert regla.severidad_derivada == "alta"

def crear_contexto_prueba(objetivo, inicio, fin):
    return ResultadoContexto.model_validate({
        "linea_objetivo": objetivo,
        "linea_inicio": inicio,
        "linea_fin": fin,
        "lineas": [
            {
                "numero": numero,
                "texto": f"codigo_linea_{numero}",
                "truncada": False,
            }
            for numero in range(inicio, fin + 1)
        ],
    })


def crear_estatico_prueba(linea):
    hallazgo = HallazgoEstatico(
        herramienta="bandit",
        regla="B602",
        tipo="seguridad",
        linea=linea,
        severidad="alta",
        titulo="Uso de subprocess",
        descripcion="Prueba de vinculaci?n",
        confianza="alta",
    )

    return ResultadoEstatico(
        archivo="muestra.py",
        estado="completo",
        hallazgos=[hallazgo],
        herramientas=[],
    )


def test_vinculo_regla_contexto_en_linea_objetivo():
    contexto = crear_contexto_prueba(10, 4, 16)

    evidencia = construir_evidencia(
        "muestra.py",
        [{
            "herramienta": "ampliar_contexto",
            "origen": "local",
            "resultado": contexto.model_dump(),
        }],
        crear_estatico_prueba(10),
    )

    assert len(evidencia.vinculos_reglas_contexto) == 1

    vinculo = evidencia.vinculos_reglas_contexto[0]

    assert vinculo.regla == "B602"
    assert vinculo.linea_regla == 10
    assert vinculo.linea_objetivo == 10
    assert vinculo.severidad_original == "alta"
    assert vinculo.confianza == "alta"
    assert vinculo.severidad_derivada == "critica"


def test_vincula_regla_en_cualquier_linea_de_ventana():
    contexto = crear_contexto_prueba(10, 4, 16)

    evidencia = construir_evidencia(
        "muestra.py",
        [{
            "herramienta": "ampliar_contexto",
            "origen": "local",
            "resultado": contexto.model_dump(),
        }],
        crear_estatico_prueba(11),
    )

    assert len(evidencia.vinculos_reglas_contexto) == 1

    vinculo = evidencia.vinculos_reglas_contexto[0]
    assert vinculo.linea_regla == 11
    assert vinculo.linea_objetivo == 10


def test_sin_contexto_no_se_crean_vinculos():
    evidencia = construir_evidencia(
        "muestra.py",
        [],
        crear_estatico_prueba(10),
    )

    assert evidencia.vinculos_reglas_contexto == []


def test_vinculo_conserva_severidad_original_y_derivada():
    contexto = crear_contexto_prueba(10, 10, 10)

    evidencia = construir_evidencia(
        "muestra.py",
        [{
            "herramienta": "ampliar_contexto",
            "origen": "local",
            "resultado": contexto.model_dump(),
        }],
        crear_estatico_prueba(10),
    )

    datos = evidencia.model_dump()
    vinculo = datos["vinculos_reglas_contexto"][0]

    assert vinculo["severidad_original"] == "alta"
    assert vinculo["severidad_derivada"] == "critica"

def test_no_vincula_regla_fuera_de_ventana_contextual():
    contexto = crear_contexto_prueba(10, 4, 16)

    evidencia = construir_evidencia(
        "muestra.py",
        [{
            "herramienta": "ampliar_contexto",
            "origen": "local",
            "resultado": contexto.model_dump(),
        }],
        crear_estatico_prueba(17),
    )

    assert evidencia.vinculos_reglas_contexto == []
