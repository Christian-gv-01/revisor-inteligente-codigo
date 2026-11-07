"""Reglas deterministas de severidad derivada y herencia."""

from typing import Iterable, Literal

from app.config.priorizacion import ORDEN_SEVERIDAD


Severidad = Literal["critica", "alta", "media", "baja"]
Confianza = Literal["alta", "media", "baja"] | None
Herramienta = Literal["ruff", "bandit"]


def derivar_severidad(
    herramienta: Herramienta,
    severidad: Severidad,
    confianza: Confianza,
) -> Severidad:
    """Deriva severidad sin inventar confianza ni modificar el dato original."""

    if severidad not in ORDEN_SEVERIDAD:
        raise ValueError("Severidad no reconocida.")

    if herramienta == "bandit":
        if severidad == "alta" and confianza == "alta":
            return "critica"

    return severidad


def combinar_severidades(
    severidad_original: Severidad,
    severidades_vinculadas: Iterable[Severidad] = (),
) -> Severidad:
    """Conserva la severidad más alta entre el hallazgo y sus reglas vinculadas."""

    candidatas = [severidad_original, *severidades_vinculadas]

    if any(s not in ORDEN_SEVERIDAD for s in candidatas):
        raise ValueError("Existe una severidad no reconocida.")

    return min(candidatas, key=ORDEN_SEVERIDAD.__getitem__)

def heredar_severidad_contextual(hallazgos: Iterable, vinculos: Iterable) -> list:
    """Hereda la mayor severidad vinculada a la linea objetivo del hallazgo."""

    elevaciones = {}

    for vinculo in vinculos:
        linea = vinculo.linea_objetivo
        severidad = vinculo.severidad_derivada

        if linea not in elevaciones:
            elevaciones[linea] = severidad
        else:
            elevaciones[linea] = combinar_severidades(
                elevaciones[linea],
                [severidad],
            )

    resultado = []

    for hallazgo in hallazgos:
        heredada = elevaciones.get(hallazgo.linea)

        if heredada is None:
            resultado.append(hallazgo)
            continue

        severidad_final = combinar_severidades(
            hallazgo.severidad,
            [heredada],
        )

        if severidad_final == hallazgo.severidad:
            resultado.append(hallazgo)
        else:
            resultado.append(
                hallazgo.model_copy(
                    update={"severidad": severidad_final},
                    deep=True,
                )
            )

    return resultado
