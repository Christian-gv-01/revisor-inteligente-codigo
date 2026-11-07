
"""Reglas deterministas para priorizar hallazgos."""

import unicodedata
from collections.abc import Sequence

from app.models.analisis import Hallazgo
from app.config.priorizacion import (
    FACTORES_CONFIANZA,
    PESOS_SEVERIDAD,
    ORDEN_SEVERIDAD,
    CATEGORIAS_SEGURIDAD,
    CATEGORIAS_CALIDAD,
)


# Criterio principal: severidad.
# Criterio secundario: confianza conocida.
# Criterio terciario: categoría normalizada.
# Los empates restantes conservan el orden original.

def calcular_puntuacion(
    severidad: object,
    confianza: object,
) -> float | None:
    """
    Calcula peso de severidad por factor de confianza.

    Devuelve None si falta alguno de los valores o no está reconocido.
    Los factores son ponderaciones operativas del proyecto, no probabilidades.
    """
    if not isinstance(severidad, str) or not isinstance(confianza, str):
        return None

    peso = PESOS_SEVERIDAD.get(severidad)
    factor = FACTORES_CONFIANZA.get(confianza)

    if peso is None or factor is None:
        return None

    return peso * factor


def normalizar_categoria(categoria: object) -> str:
    """Normaliza categorías para compararlas de forma consistente."""

    if not isinstance(categoria, str):
        return ""

    texto = unicodedata.normalize("NFKD", categoria)

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return " ".join(
        texto.casefold()
        .replace("_", " ")
        .replace("-", " ")
        .split()
    )


def prioridad_categoria(hallazgo: Hallazgo) -> int:
    """
    Determina la prioridad secundaria de cada categoría.

    0: Seguridad.
    1: Categoría desconocida o no clasificada.
    2: Calidad.
    """

    categoria = normalizar_categoria(
        getattr(hallazgo, "categoria", "")
    )

    if categoria in CATEGORIAS_SEGURIDAD:
        return 0

    if categoria in CATEGORIAS_CALIDAD:
        return 2

    return 1


def priorizar_hallazgos(
    lista: Sequence[Hallazgo],
) -> list[Hallazgo]:
    """
    Ordena los hallazgos mediante criterios deterministas.

    1. Severidad: crítica, alta, media y baja.
    2. Confianza conocida: alta, media y baja; la ausente queda detrás.
    3. Categoría: seguridad, desconocida y calidad.
    4. Conserva el orden original en los empates restantes.

    La puntuación ponderada equivale al orden lexicográfico para las doce
    combinaciones conocidas. Se conserva el orden lexicográfico actual.
    No modifica la severidad original ni la lista recibida.
    """

    def clave(hallazgo: Hallazgo) -> tuple[int, int, int, int]:
        severidad = getattr(hallazgo, "severidad", None)

        try:
            orden = ORDEN_SEVERIDAD[severidad]
        except (KeyError, TypeError) as error:
            raise ValueError(
                f"Severidad no soportada: {severidad}"
            ) from error

        confianza = getattr(hallazgo, "confianza", None)
        puntuacion = calcular_puntuacion(severidad, confianza)

        return (
            orden,
            1 if puntuacion is None else 0,
            -(puntuacion if puntuacion is not None else 0.0),
            prioridad_categoria(hallazgo),
        )

    return sorted(lista, key=clave)

