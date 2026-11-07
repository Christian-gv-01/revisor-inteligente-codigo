from types import SimpleNamespace

from app.models.analisis import Hallazgo
from app.services.severidad import heredar_severidad_contextual


def crear_hallazgo(linea, severidad):
    return Hallazgo(
        linea=linea,
        severidad=severidad,
        categoria="seguridad",
        titulo="Hallazgo de prueba",
        explicacion="Explicacion de prueba",
        correccion_sugerida="Correccion de prueba",
    )


def crear_vinculo(linea_objetivo, severidad):
    return SimpleNamespace(
        linea_objetivo=linea_objetivo,
        severidad_derivada=severidad,
    )


def test_hereda_critica_en_linea_objetivo():
    original = crear_hallazgo(10, "alta")
    vinculo = crear_vinculo(10, "critica")

    resultado = heredar_severidad_contextual(
        [original], [vinculo]
    )

    assert resultado[0].severidad == "critica"
    assert original.severidad == "alta"


def test_no_hereda_en_otra_linea():
    original = crear_hallazgo(11, "alta")
    vinculo = crear_vinculo(10, "critica")

    resultado = heredar_severidad_contextual(
        [original], [vinculo]
    )

    assert resultado[0].severidad == "alta"


def test_no_reduce_severidad_critica():
    original = crear_hallazgo(10, "critica")
    vinculo = crear_vinculo(10, "alta")

    resultado = heredar_severidad_contextual(
        [original], [vinculo]
    )

    assert resultado[0].severidad == "critica"


def test_varios_vinculos_conservan_la_mayor_severidad():
    original = crear_hallazgo(10, "baja")

    vinculos = [
        crear_vinculo(10, "media"),
        crear_vinculo(10, "alta"),
        crear_vinculo(10, "critica"),
    ]

    resultado = heredar_severidad_contextual(
        [original], vinculos
    )

    assert resultado[0].severidad == "critica"


def test_sin_vinculos_conserva_el_hallazgo():
    original = crear_hallazgo(10, "media")

    resultado = heredar_severidad_contextual(
        [original], []
    )

    assert resultado[0] is original


def test_no_modifica_el_hallazgo_original():
    original = crear_hallazgo(10, "alta")

    resultado = heredar_severidad_contextual(
        [original],
        [crear_vinculo(10, "critica")],
    )

    assert original.severidad == "alta"
    assert resultado[0].severidad == "critica"
    assert resultado[0] is not original

def test_integracion_bandit_contexto_herencia_gemini():
    from app.services.evidencia import construir_evidencia
    from app.services.static_analysis import (
        HallazgoEstatico,
        ResultadoEstatico,
    )
    from app.services.herramientas_contextuales import ResultadoContexto

    contexto = ResultadoContexto.model_validate({
        "linea_objetivo": 10,
        "linea_inicio": 4,
        "linea_fin": 16,
        "lineas": [
            {
                "numero": numero,
                "texto": f"codigo_linea_{numero}",
                "truncada": False,
            }
            for numero in range(4, 17)
        ],
    })

    bandit = HallazgoEstatico(
        herramienta="bandit",
        regla="B602",
        tipo="seguridad",
        linea=10,
        severidad="alta",
        titulo="Uso de subprocess",
        descripcion="Uso de shell",
        confianza="alta",
    )

    estatico = ResultadoEstatico(
        archivo="muestra.py",
        estado="completo",
        hallazgos=[bandit],
        herramientas=[],
    )

    evidencia = construir_evidencia(
        "muestra.py",
        [{
            "herramienta": "ampliar_contexto",
            "origen": "local",
            "resultado": contexto.model_dump(),
        }],
        estatico,
    )

    assert len(evidencia.vinculos_reglas_contexto) == 1

    vinculo = evidencia.vinculos_reglas_contexto[0]

    assert vinculo.severidad_original == "alta"
    assert vinculo.confianza == "alta"
    assert vinculo.severidad_derivada == "critica"

    gemini = crear_hallazgo(10, "alta")

    resultado = heredar_severidad_contextual(
        [gemini],
        evidencia.vinculos_reglas_contexto,
    )

    assert resultado[0].severidad == "critica"
    assert gemini.severidad == "alta"
