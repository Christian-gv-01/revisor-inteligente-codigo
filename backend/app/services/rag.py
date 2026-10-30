
import os
from pathlib import Path

import chromadb


ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "chroma"

COLLECTION_NAMES = (
    "seguridad_python",
    "contexto_proyecto",
)

# Umbral máximo de distancia permitido.
# Puede configurarse mediante RAG_MAX_DISTANCE.
try:
    MAX_DISTANCE = float(
        os.getenv("RAG_MAX_DISTANCE", "0.75")
    )
except (TypeError, ValueError):
    MAX_DISTANCE = 0.75

# La distancia coseno de ChromaDB se limita a [0, 2].
MAX_DISTANCE = max(0.0, min(MAX_DISTANCE, 2.0))


class RAGNoDisponibleError(RuntimeError):
    """Indica que la base de conocimiento no está preparada."""


def buscar_fragmentos(
    pregunta: str,
    limite: int = 3,
    *,
    area: str | None = None,
    extension: str | None = None,
    source_type: str | None = None,
    source_name: str | None = None,
    section: str | None = None,
    review_date: str | None = None,
    effective_date: str | None = None,
) -> list[dict]:
    """
    Recupera fragmentos de las colecciones disponibles.

    - Busca en seguridad_python y contexto_proyecto.
    - Descarta resultados que superen el umbral de distancia.
    - Excluye evidencias históricas de la recuperación ordinaria.
    - Conserva los metadatos y referencias originales.
    - Ordena por relevancia semántica.
    - Aplica el límite individualmente a cada colección.
    - Evita que el contexto del proyecto desplace las fuentes
      documentales de seguridad.
    """

    if not isinstance(pregunta, str) or not pregunta.strip():
        return []

    if not DB_PATH.is_dir():
        raise RAGNoDisponibleError(
            "No existe la base vectorial. "
            "Ejecuta los scripts de ingesta."
        )

    try:
        limite = int(limite)
    except (TypeError, ValueError):
        limite = 3

    limite = max(1, min(limite, 10))

    cliente = chromadb.PersistentClient(
        path=str(DB_PATH)
    )

    try:
        fragmentos = []
        colecciones_disponibles = 0

        tiene_filtros_seguridad = any(
            isinstance(valor, str) and valor.strip()
            for valor in (source_name, review_date, effective_date)
        )

        tiene_filtros_proyecto = any(
            isinstance(valor, str) and valor.strip()
            for valor in (area, extension, source_type)
        )

        for nombre_coleccion in COLLECTION_NAMES:

            if nombre_coleccion == "seguridad_python":
                if tiene_filtros_proyecto and not tiene_filtros_seguridad:
                    continue

            elif nombre_coleccion == "contexto_proyecto":
                if tiene_filtros_seguridad and not tiene_filtros_proyecto:
                    continue

            # Recuperar la colección.
            try:
                coleccion = cliente.get_collection(
                    name=nombre_coleccion
                )
            except Exception:
                continue

            colecciones_disponibles += 1

            total = coleccion.count()

            if total == 0:
                continue

            # Recuperar candidatos de cada colección.
            query_kwargs = {
                "query_texts": [pregunta],
                "n_results": min(limite, total),
                "include": [
                    "documents",
                    "metadatas",
                    "distances",
                ],
            }

            if nombre_coleccion == "seguridad_python":
                filtros_metadata = {
                    "source_name": source_name,
                    "section": section,
                    "review_date": review_date,
                    "effective_date": effective_date,
                }

            elif nombre_coleccion == "contexto_proyecto":
                filtros_metadata = {
                    "area": area,
                    "extension": extension,
                    "source_type": source_type,
                    "section": section,
                }

            else:
                filtros_metadata = {}

            condiciones = [
                {campo: {"$eq": valor.strip()}}
                for campo, valor in filtros_metadata.items()
                if isinstance(valor, str) and valor.strip()
            ]

            if len(condiciones) == 1:
                query_kwargs["where"] = condiciones[0]

            elif len(condiciones) > 1:
                query_kwargs["where"] = {
                    "$and": condiciones
                }

            resultados = coleccion.query(**query_kwargs)

            documentos = resultados["documents"][0] or []
            metadatos = resultados["metadatas"][0] or []
            distancias = resultados["distances"][0] or []
            identificadores = resultados["ids"][0] or []

            for indice, documento in enumerate(documentos):

                if not documento:
                    continue

                # Obtener los metadatos antes de utilizarlos.
                metadata = (
                    metadatos[indice]
                    if indice < len(metadatos)
                    else None
                ) or {}

                # Obtener y comprobar la distancia.
                distancia = (
                    distancias[indice]
                    if indice < len(distancias)
                    else None
                )

                if distancia is not None:
                    if distancia > MAX_DISTANCE:
                        continue

                # Excluir evidencias históricas.
                ruta_documento = str(
                    metadata.get("source_path", "")
                ).replace("\\", "/").lower()

                if ruta_documento.startswith(
                    "docs/evidencias/"
                ):
                    continue

                # Recuperar el identificador original.
                identificador = (
                    identificadores[indice]
                    if indice < len(identificadores)
                    else ""
                )

                ruta = metadata.get("source_path", "")

                es_seguridad = (
                    nombre_coleccion == "seguridad_python"
                )

                # Construir el fragmento conservando sus fuentes.
                fragmentos.append({
                    "id": identificador,
                    "texto": documento,
                    "seccion": metadata.get("section", ""),
                    "documento": (
                        metadata.get("document")
                        or ruta
                    ),
                    "fuente": (
                        metadata.get("source_name")
                        or ruta
                    ),
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
                    "effective_date": metadata.get(
                        "effective_date", ""
                    ),
                })

        # Comprobar que al menos una colección existe.
        if colecciones_disponibles == 0:
            raise RAGNoDisponibleError(
                "No se encontraron las colecciones de conocimiento. "
                "Ejecuta scripts/ingest.py y "
                "scripts/ingest_proyecto.py."
            )

        # Ordenar por distancia semántica ascendente.
        # La fuente de seguridad solo desempata distancias iguales.
        fragmentos.sort(
            key=lambda fragmento: (
                (
                    fragmento["distancia"]
                    if fragmento["distancia"] is not None
                    else float("inf")
                ),
                (
                    0
                    if fragmento["tipo_fuente"] == "seguridad"
                    else 1
                ),
            )
        )

        # IMPORTANTE:
        # El límite ya se aplica individualmente en cada colección.
        # No aplicar un segundo límite global porque podría eliminar
        # referencias de seguridad relevantes.
        return fragmentos

    finally:
        cliente.close()
