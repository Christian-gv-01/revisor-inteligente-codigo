
"""Evalua el RAG utilizando el mismo flujo del analizador real.

No realiza llamadas a Gemini.
Utiliza la transformacion de consultas y la recuperacion
de fuentes de seguridad implementadas en el servicio LLM.
"""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = ROOT / "backend"

sys.path.insert(0, str(BACKEND_PATH))

from app.services.llm import (  # noqa: E402
    _construir_consulta_rag,
    _recuperar_contexto_rag,
)


K = 3


# Casos basados en codigo real.
# Las referencias esperadas corresponden a los documentos
# de seguridad que deben respaldar cada vulnerabilidad.

CASOS_EVALUACION = [
    {
        "nombre": "Uso inseguro de eval",
        "codigo": """
entrada = input("Valor: ")
resultado = eval(entrada)
""",
        "relevantes": {
            "seguridad_python-001",
        },
    },
    {
        "nombre": "Inyeccion SQL",
        "codigo": """
nombre = input("Nombre: ")
query = "SELECT * FROM usuarios WHERE nombre = '" + nombre + "'"
cursor.execute(query)
""",
        "relevantes": {
            "seguridad_python-002",
            "seguridad_python-004",
        },
    },
    {
        "nombre": "Inyeccion de comandos",
        "codigo": """
import os
host = input("Host: ")
os.system("ping " + host)
""",
        "relevantes": {
            "seguridad_python-003",
            "seguridad_python-004",
        },
    },
]


def precision_at_k(ids_recuperados, ids_relevantes, k):
    """Proporcion de resultados relevantes entre los primeros k."""

    primeros = ids_recuperados[:k]

    encontrados = sum(
        identificador in ids_relevantes
        for identificador in primeros
    )

    return encontrados / k


def recall_at_k(ids_recuperados, ids_relevantes, k):
    """Proporcion de documentos relevantes recuperados."""

    if not ids_relevantes:
        return 0.0

    primeros = set(ids_recuperados[:k])

    return len(
        primeros.intersection(ids_relevantes)
    ) / len(ids_relevantes)


def reciprocal_rank_at_k(ids_recuperados, ids_relevantes, k):
    """Inverso de la posicion del primer resultado relevante."""

    for posicion, identificador in enumerate(
        ids_recuperados[:k],
        start=1,
    ):
        if identificador in ids_relevantes:
            return 1.0 / posicion

    return 0.0


def evaluar_caso(caso):
    """
    Ejecuta el mismo flujo RAG que utiliza el analizador.

    No llama a Gemini.
    """

    codigo = caso["codigo"]

    consulta = _construir_consulta_rag(codigo)

    contexto, fuentes = _recuperar_contexto_rag(codigo)

    ids_recuperados = [
        str(fuente["id"])
        for fuente in fuentes
        if fuente.get("id")
    ]

    ids_relevantes = caso["relevantes"]

    return {
        "nombre": caso["nombre"],
        "consulta": consulta,
        "contexto": contexto,
        "fuentes": fuentes,
        "ids_recuperados": ids_recuperados,
        "relevantes": ids_relevantes,
        "precision": precision_at_k(
            ids_recuperados,
            ids_relevantes,
            K,
        ),
        "recall": recall_at_k(
            ids_recuperados,
            ids_relevantes,
            K,
        ),
        "mrr": reciprocal_rank_at_k(
            ids_recuperados,
            ids_relevantes,
            K,
        ),
    }


def imprimir_resultado(resultado):
    """Muestra los resultados de cada consulta."""

    print("\n" + "=" * 65)
    print(resultado["nombre"])
    print("=" * 65)

    print("\nConsulta transformada:")
    print(resultado["consulta"])

    print(
        "\nContexto generado:",
        bool(resultado["contexto"]),
    )

    print(
        "Fuentes de seguridad:",
        len(resultado["fuentes"]),
    )

    print(f"\nPrecision@{K}: {resultado['precision']:.3f}")
    print(f"Recall@{K}:    {resultado['recall']:.3f}")
    print(f"MRR@{K}:       {resultado['mrr']:.3f}")

    if not resultado["fuentes"]:
        print("\nNo se recuperaron fuentes de seguridad.")
        return

    print("\nFragmentos recuperados:")

    for posicion, fuente in enumerate(
        resultado["fuentes"],
        start=1,
    ):
        identificador = fuente.get("id", "")

        distancia = fuente.get("distancia")

        distancia_texto = (
            f"{distancia:.4f}"
            if distancia is not None
            else "no disponible"
        )

        relevante = (
            identificador in resultado["relevantes"]
        )

        print(
            f"\n{posicion}. ID={identificador}"
            f" | distancia={distancia_texto}"
            f" | relevante={relevante}"
        )

        print("   Fuente:", fuente.get("fuente", ""))
        print("   Seccion:", fuente.get("seccion", ""))


def main():
    """Ejecuta la evaluacion completa del flujo RAG."""

    resultados = []

    print("=" * 65)
    print("EVALUACION DEL FLUJO RAG REAL")
    print("=" * 65)

    print("Raiz:", ROOT)
    print("Coleccion: seguridad_python")
    print("Limite de evaluacion:", K)
    print("Proveedor Gemini: no utilizado")

    try:
        for caso in CASOS_EVALUACION:
            resultado = evaluar_caso(caso)

            resultados.append(resultado)

            imprimir_resultado(resultado)

    except Exception as error:
        print("\nERROR DURANTE LA EVALUACION RAG")
        print("Tipo:", type(error).__name__)
        print("Detalle:", str(error))
        raise SystemExit(1) from error

    if not resultados:
        print("\nNo existen resultados de evaluacion.")
        raise SystemExit(1)

    total = len(resultados)

    precision_media = sum(
        resultado["precision"]
        for resultado in resultados
    ) / total

    recall_medio = sum(
        resultado["recall"]
        for resultado in resultados
    ) / total

    mrr_medio = sum(
        resultado["mrr"]
        for resultado in resultados
    ) / total

    cobertura = sum(
        bool(resultado["fuentes"])
        for resultado in resultados
    ) / total

    print("\n" + "=" * 65)
    print("RESUMEN GLOBAL")
    print("=" * 65)

    print("Consultas evaluadas:", total)
    print(f"Precision@{K} media: {precision_media:.3f}")
    print(f"Recall@{K} medio:    {recall_medio:.3f}")
    print(f"MRR@{K} medio:       {mrr_medio:.3f}")
    print(f"Cobertura:           {cobertura:.1%}")

    print("\nEvaluacion finalizada.")

    if cobertura == 0:
        print("ERROR: ninguna consulta recupero fuentes de seguridad.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
