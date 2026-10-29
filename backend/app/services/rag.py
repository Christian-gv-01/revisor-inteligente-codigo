
import os
from pathlib import Path

import chromadb


ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "chroma"

COLLECTION_NAMES = (
    "seguridad_python",
    "contexto_proyecto",
)

# Umbral provisional: debe calibrarse con pruebas.
try:
    MAX_DISTANCE = float(os.getenv("RAG_MAX_DISTANCE", "0.75"))
except (TypeError, ValueError):
    MAX_DISTANCE = 0.75

MAX_DISTANCE = max(0.0, min(MAX_DISTANCE, 2.0))


class RAGNoDisponibleError(RuntimeError):
    """Indica que la base de conocimiento no está preparada."""


def buscar_fragmentos(
    pregunta: str,
    limite: int = 3,
) -> list[dict]:
    """
    Recupera fragmentos de las colecciones disponibles,
    filtra por distancia y conserva sus fuentes originales.
    """

    if not pregunta.strip():
        return []

    if not DB_PATH.is_dir():
        raise RAGNoDisponibleError(
            "No existe la base vectorial. "
            "Ejecuta los scripts de ingesta."
        )

    limite = max(1, min(limite, 10))
    cliente = chromadb.PersistentClient(path=str(DB_PATH))

    try:
        fragmentos = []
        colecciones_disponibles = 0

        for nombre_coleccion in COLLECTION_NAMES:
            try:
                coleccion = cliente.get_collection(
                    name=nombre_coleccion,
                )
            except Exception:
                continue

            colecciones_disponibles += 1
            total = coleccion.count()

            if total == 0:
                continue

            resultados = coleccion.query(
                query_texts=[pregunta],
                n_results=min(limite, total),
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )

            documentos = resultados["documents"][0] or []
            metadatos = resultados["metadatas"][0] or []
            distancias = resultados["distances"][0] or []
            identificadores = resultados["ids"][0] or []

            for indice, documento in enumerate(documentos):
                if not documento:
                    continue

                distancia = (
                    distancias[indice]
                    if indice < len(distancias)
                    else None
                )

                if (
                    distancia is not None
                    and distancia > MAX_DISTANCE
                ):
                    continue

                metadata = (
                    metadatos[indice]
                    if indice < len(metadatos)
                    else None
                ) or {}

                identificador = (
                    identificadores[indice]
                    if indice < len(identificadores)
                    else ""
                )

                ruta = metadata.get("source_path", "")
                es_seguridad = (
                    nombre_coleccion == "seguridad_python"
                )

                fragmentos.append({
                    "id": identificador,
                    "texto": documento,
                    "seccion": metadata.get("section", ""),
                    "documento": metadata.get("document") or ruta,
                    "fuente": metadata.get("source_name") or ruta,
                    "url": metadata.get("source_url", ""),
                    "distancia": distancia,
                    "area": metadata.get(
                        "area",
                        "seguridad" if es_seguridad else "proyecto",
                    ),
                    "tipo_fuente": (
                        "seguridad"
                        if es_seguridad
                        else "contexto_proyecto"
                    ),
                    "coleccion": nombre_coleccion,
                    "source_section": metadata.get(
                        "source_section", ""
                    ),
                    "review_date": metadata.get(
                        "review_date", ""
                    ),
                })

        if colecciones_disponibles == 0:
            raise RAGNoDisponibleError(
                "No se encontraron las colecciones de conocimiento. "
                "Ejecuta scripts/ingest.py y "
                "scripts/ingest_proyecto.py."
            )

        fragmentos.sort(
            key=lambda fragmento: (
                fragmento["distancia"]
                if fragmento["distancia"] is not None
                else float("inf")
            )
        )

        return fragmentos

    finally:
        cliente.close()
