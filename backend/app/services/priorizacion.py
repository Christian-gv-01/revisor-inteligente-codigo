
"""Reglas deterministas para priorizar hallazgos."""

import unicodedata
from collections.abc import Sequence

from app.models.analisis import Hallazgo


# Criterio principal: severidad.
ORDEN_SEVERIDAD = {
    "critica": 1,
    "alta": 2,
    "media": 3,
    "baja": 4,
}


# Criterio secundario: categorías relacionadas con seguridad.
CATEGORIAS_SEGURIDAD = {
    "seguridad",
    "credenciales",
    "ejecucion arbitraria",
    "inyeccion sql",
    "inyeccion de sql",
    "path traversal",
    "traversal de rutas",
    "acceso inseguro a archivos",
    "cwe 22",
    "cwe 78",
    "cwe 89",
    "cwe 798",
}

CATEGORIAS_CALIDAD = {
    "calidad",
}


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
    2. Categoría: seguridad antes que calidad.
    3. Conserva el orden original en los empates.

    No modifica la lista original.
    No reduce la severidad de ningún hallazgo.
    """

    def clave(hallazgo: Hallazgo) -> tuple[int, int]:
        severidad = getattr(hallazgo, "severidad", None)

        try:
            orden = ORDEN_SEVERIDAD[severidad]
        except (KeyError, TypeError) as error:
            raise ValueError(
                f"Severidad no soportada: {severidad}"
            ) from error

        return (
            orden,
            prioridad_categoria(hallazgo),
        )

    return sorted(lista, key=clave)
