
from __future__ import annotations

import os
import re
from pathlib import Path

import chromadb


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "knowledge" / "seguridad_python.md"
configurada = os.getenv("CHROMA_PATH", "").strip()
DB_PATH = Path(configurada).expanduser() if configurada else ROOT / "data" / "chroma"
COLLECTION_NAME = "seguridad_python"

HEADING_PATTERN = re.compile(
    r"^##\s+(?P<title>.+?)\s*$",
    re.MULTILINE,
)

METADATA_LINE_PATTERN = re.compile(
    r"^\s*(?:"
    r"Documento fuente|"
    r"Seccion fuente|Sección fuente|"
    r"Seccion|Sección|"
    r"URL fuente|"
    r"Fecha de revision|Fecha de revisión|"
    r"Fecha de vigencia|"
    r"Vigencia desde|"
    r"Fecha de entrada en vigor|"
    r"Categoria|Categoría"
    r")\s*:",
    re.IGNORECASE,
)


def get_field(text: str, *labels: str) -> str | None:
    """Obtiene un campo de metadatos sin distinguir mayúsculas."""

    for label in labels:
        pattern = (
            rf"^\s*{re.escape(label)}\s*:\s*(.*?)\s*$"
        )
        match = re.search(
            pattern,
            text,
            flags=re.MULTILINE | re.IGNORECASE,
        )

        if match and match.group(1).strip():
            return match.group(1).strip()

    return None


def clean_text(text: str) -> str:
    """Normaliza saltos de línea y espacios innecesarios."""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_sections(text: str) -> list[dict]:
    """Extrae secciones Markdown y conserva sus metadatos."""

    text = clean_text(text)
    headings = list(HEADING_PATTERN.finditer(text))

    if not headings:
        raise ValueError(
            "El documento no contiene secciones Markdown ##."
        )

    header = text[:headings[0].start()]

    document_review_date = get_field(
        header,
        "Fecha de revision",
        "Fecha de revisión",
    )

    document_effective_date = get_field(
        header,
        "Fecha de vigencia",
        "Vigencia desde",
        "Fecha de entrada en vigor",
    )

    sections = []

    for index, heading in enumerate(headings):
        end = (
            headings[index + 1].start()
            if index + 1 < len(headings)
            else len(text)
        )

        block = text[heading.start():end].strip()
        title = heading.group("title").strip()

        source_name = get_field(
            block,
            "Documento fuente",
        )

        source_section = get_field(
            block,
            "Seccion fuente",
            "Sección fuente",
            "Seccion",
            "Sección",
        )

        source_url = get_field(
            block,
            "URL fuente",
            "URL",
        )

        review_date = get_field(
            block,
            "Fecha de revision",
            "Fecha de revisión",
        ) or document_review_date

        effective_date = get_field(
            block,
            "Fecha de vigencia",
            "Vigencia desde",
            "Fecha de entrada en vigor",
        ) or document_effective_date

        category = get_field(
            block,
            "Categoria",
            "Categoría",
        ) or "seguridad_python"

        body_lines = []

        for line in block.splitlines()[1:]:
            if METADATA_LINE_PATTERN.match(line):
                continue

            body_lines.append(line)

        body = clean_text("\n".join(body_lines))
        document_text = clean_text(f"{title}\n\n{body}")

        if not body:
            raise ValueError(
                f"La sección '{title}' no contiene contenido."
            )

        metadata = {
            "document": SOURCE_FILE.name,
            "section": title,
            "category": category,
        }

        if source_name:
            metadata["source_name"] = source_name

        if source_section:
            metadata["source_section"] = source_section

        if source_url:
            metadata["source_url"] = source_url

        if review_date:
            metadata["review_date"] = review_date

        # Solo registrar la vigencia cuando está documentada.
        # No confundir la fecha de revisión con la de vigencia.
        if effective_date:
            metadata["effective_date"] = effective_date

        sections.append({
            "id": f"{SOURCE_FILE.stem}-{index + 1:03d}",
            "text": document_text,
            "metadata": metadata,
        })

    return sections


def main() -> None:
    if not SOURCE_FILE.is_file():
        raise FileNotFoundError(
            f"No se encontro la fuente de conocimiento: {SOURCE_FILE}"
        )

    text = SOURCE_FILE.read_text(encoding="utf-8-sig")
    sections = extract_sections(text)

    if not sections:
        raise ValueError("No hay secciones para indexar.")

    DB_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(DB_PATH))

    try:
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        # Identificar los registros anteriores de este documento.
        previous = collection.get(
            where={"document": SOURCE_FILE.name},
        )

        previous_ids = set(previous.get("ids", []))
        new_ids = {item["id"] for item in sections}

        # Actualizar o insertar los fragmentos.
        # ChromaDB genera embeddings automáticamente a partir
        # del texto si no se proporcionan embeddings explícitos.
        collection.upsert(
            ids=[item["id"] for item in sections],
            documents=[item["text"] for item in sections],
            metadatas=[item["metadata"] for item in sections],
        )

        # Eliminar los fragmentos que ya no existen en el documento.
        obsolete_ids = list(previous_ids - new_ids)

        if obsolete_ids:
            collection.delete(ids=obsolete_ids)

        print(f"Fuente: {SOURCE_FILE.relative_to(ROOT)}")
        print(f"Base vectorial: {DB_PATH}")
        print(f"Coleccion: {COLLECTION_NAME}")
        print(f"Fragmentos procesados: {len(sections)}")
        print(
            "Fragmentos obsoletos eliminados:",
            len(obsolete_ids),
        )
        print(
            "Total de registros en la coleccion:",
            collection.count(),
        )

        # Comprobación básica de recuperación semántica.
        results = collection.query(
            query_texts=[
                "¿Que riesgo tiene usar eval con datos externos?"
            ],
            n_results=min(3, collection.count()),
            include=["metadatas", "distances"],
        )

        print("\nResultados de la consulta de prueba:")

        metadatas = results["metadatas"][0] or []
        distances = results["distances"][0] or []

        if not metadatas:
            print("No se recuperaron fragmentos.")
        else:
            for rank, metadata in enumerate(metadatas, start=1):
                distance = distances[rank - 1]

                print(
                    f"{rank}. "
                    f"{metadata.get('section', 'Sin seccion')}"
                )
                print(
                    "   Fuente:",
                    metadata.get("source_name", "No indicada"),
                )
                print(
                    "   URL:",
                    metadata.get("source_url", "No indicada"),
                )
                print(
                    "   Fecha de vigencia:",
                    metadata.get("effective_date", "No indicada"),
                )
                print(f"   Distancia: {distance:.4f}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
