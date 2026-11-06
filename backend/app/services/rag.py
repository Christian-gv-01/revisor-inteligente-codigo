from pathlib import Path

import chromadb

from app.config import obtener_distancia_rag


ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "chroma"

COLLECTION_NAMES = (
    "seguridad_python",
    "contexto_proyecto",
)

# Umbral maximo de distancia permitido, centralizado en app.config.
# La configuracion valida el valor y lo limita al intervalo [0, 2].
MAX_DISTANCE = obtener_distancia_rag()


class RAGNoDisponibleError(RuntimeError):
    """Indica que la base de conocimiento no esta preparada."""


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
    - Excluye evidencias historicas de la recuperacion ordinaria.
    - Conserva los metadatos y referencias originales.
    - Ordena por relevancia semantica.
    - Aplica el limite individualmente a cada coleccion.
    - Evita que el contexto del proyecto desplace las fuentes
      documentales de seguridad.

    La coleccion de seguridad es obligatoria para las consultas
    generales y para los filtros documentales de seguridad.
    La coleccion del proyecto es complementaria, salvo cuando
    se solicita expresamente un filtro propio de esa coleccion.
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

    tiene_filtros_seguridad = any(
        isinstance(valor, str) and valor.strip()
        for valor in (source_name, review_date, effective_date)
    )

    tiene_filtros_proyecto = any(
        isinstance(valor, str) and valor.strip()
        for valor in (area, extension, source_type)
    )

    consultar_seguridad = (
        not tiene_filtros_proyecto
        or tiene_filtros_seguridad
    )

    consultar_proyecto = (
        not tiene_filtros_seguridad
        or tiene_filtros_proyecto
    )

    colecciones_obligatorias = set()

    if consultar_seguridad:
        colecciones_obligatorias.add("seguridad_python")

    if tiene_filtros_proyecto:
        colecciones_obligatorias.add("contexto_proyecto")

    try:
        cliente = chromadb.PersistentClient(
            path=str(DB_PATH)
        )
    except Exception as error:
        raise RAGNoDisponibleError(
            "No fue posible conectar con la base vectorial ChromaDB."
        ) from error

    try:
        fragmentos = []
        colecciones_disponibles = set()

        for nombre_coleccion in COLLECTION_NAMES:

            if (
                nombre_coleccion == "seguridad_python"
                and not consultar_seguridad
            ):
                continue

            if (
                nombre_coleccion == "contexto_proyecto"
                and not consultar_proyecto
            ):
                continue

            # Recuperar la coleccion.
            try:
                coleccion = cliente.get_collection(
                    name=nombre_coleccion
                )
            except Exception as error:
                if nombre_coleccion in colecciones_obligatorias:
                    raise RAGNoDisponibleError(
                        f"La coleccion obligatoria "
                        f"'{nombre_coleccion}' no esta disponible. "
                        "Comprueba la ingesta correspondiente."
                    ) from error

                # El contexto interno es complementario en consultas
                # generales; su ausencia no invalida la fuente oficial.
                continue

            colecciones_disponibles.add(nombre_coleccion)

            try:
                total = coleccion.count()
            except Exception as error:
                if nombre_coleccion in colecciones_obligatorias:
                    raise RAGNoDisponibleError(
                        f"No fue posible consultar la coleccion "
                        f"'{nombre_coleccion}'."
                    ) from error
                continue

            if total == 0:
                if nombre_coleccion in colecciones_obligatorias:
                    raise RAGNoDisponibleError(
                        f"La coleccion obligatoria "
                        f"'{nombre_coleccion}' esta vacia. "
                        "Ejecuta la ingesta correspondiente."
                    )
                continue

            # Recuperar candidatos de cada coleccion.
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

            try:
                resultados = coleccion.query(**query_kwargs)
            except Exception as error:
                if nombre_coleccion in colecciones_obligatorias:
                    raise RAGNoDisponibleError(
                        f"Fallo la recuperacion de la coleccion "
                        f"'{nombre_coleccion}'."
                    ) from error
                continue

            documentos = (
                resultados.get("documents", [[]])[0] or []
            )
            metadatos = (
                resultados.get("metadatas", [[]])[0] or []
            )
            distancias = (
                resultados.get("distances", [[]])[0] or []
            )
            identificadores = (
                resultados.get("ids", [[]])[0] or []
            )

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

                # Excluir evidencias historicas.
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

        # La coleccion de seguridad debe estar disponible en consultas
        # generales, incluso si la coleccion del proyecto existe.
        if (
            consultar_seguridad
            and "seguridad_python" not in colecciones_disponibles
        ):
            raise RAGNoDisponibleError(
                "No se encontro la coleccion obligatoria "
                "'seguridad_python'. Ejecuta scripts/ingest.py."
            )

        if not colecciones_disponibles:
            raise RAGNoDisponibleError(
                "No se encontraron las colecciones de conocimiento. "
                "Ejecuta scripts/ingest.py y "
                "scripts/ingest_proyecto.py."
            )

        # Ordenar por distancia semantica ascendente.
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

        # El limite se aplica individualmente en cada coleccion.
        # No aplicar un segundo limite global porque podria eliminar
        # referencias de seguridad relevantes.
        return fragmentos

    finally:
        cliente.close()
