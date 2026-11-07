"""Política v1: severidad, confianza, categoría y empate estable."""

ORDEN_SEVERIDAD = {
    "critica": 1,
    "alta": 2,
    "media": 3,
    "baja": 4,
}

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


# Orden de confianza informado por Bandit.
# No representa probabilidades calibradas.
ORDEN_CONFIANZA = {
    "alta": 1,
    "media": 2,
    "baja": 3,
}


# Pesos de severidad: ponderaciones del proyecto, no probabilidades.
PESOS_SEVERIDAD = {
    "critica": 8,
    "alta": 4,
    "media": 2,
    "baja": 1,
}

# Factores de confianza informados por Bandit.
FACTORES_CONFIANZA = {
    "alta": 1.0,
    "media": 0.8,
    "baja": 0.6,
}
