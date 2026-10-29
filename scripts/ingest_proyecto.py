from pathlib import Path
import hashlib
import re
from collections import Counter

import chromadb


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "chroma"
COLLECTION_NAME = "contexto_proyecto"

MAX_CHARS = 3500
OVERLAP_CHARS = 350

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules",
    "__pycache__", "dist", "build",
    ".pytest_cache", "coverage",
}

SOURCE_DIRS = [
    (ROOT / "docs", {".md", ".json"}, "documentacion"),
    (ROOT / "backend" / "app", {".py", ".md"}, "backend"),
    (ROOT / "backend" / "tests", {".py"}, "qa"),
    (ROOT / "frontend" / "src", {".ts", ".tsx"}, "frontend"),
]

EXTRA_FILES = [
    (ROOT / "README.md", "documentacion"),
    (ROOT / "backend" / "requirements.txt", "backend"),
    (ROOT / "frontend" / "package.json", "frontend"),
    (ROOT / "frontend" / "tsconfig.json", "frontend"),
]

SECRET_PATTERN = re.compile(
    r"""(?im)^(\s*(?:GEMINI_API_KEY|OPENAI_API_KEY|GITHUB_TOKEN|SECRET_KEY|ACCESS_TOKEN|PASSWORD)\s*=\s*)(["'])(.{12,}?)\2\s*$"""
)


def archivo_permitido(path: Path) -> bool:
    relativa = path.relative_to(ROOT)

    if any(
        parte.lower() in SKIP_DIRS
        for parte in relativa.parts[:-1]
    ):
        return False

    nombre = path.name.lower()

    if nombre.startswith(".env"):
        return False

    if any(
        palabra in nombre
        for palabra in ("secret", "credential", "private_key")
    ):
        return False

    if path.stat().st_size > 500_000:
        return False

    return True


def obtener_archivos() -> list[tuple[Path, str]]:
    encontrados = {}

    for carpeta, extensiones, area in SOURCE_DIRS:
        if not carpeta.is_dir():
            continue

        for path in carpeta.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in extensiones:
                continue

            if archivo_permitido(path):
                encontrados[path.resolve()] = area

    for path, area in EXTRA_FILES:
        if path.is_file() and archivo_permitido(path):
            encontrados[path.resolve()] = area

    return sorted(
        encontrados.items(),
        key=lambda item: str(item[0]),
    )


def dividir_texto(texto: str):
    inicio = 0

    while inicio < len(texto):
        fin = min(inicio + MAX_CHARS, len(texto))

        if fin < len(texto):
            corte = texto.rfind(
                "\n",
                inicio + MAX_CHARS // 2,
                fin,
            )
            if corte > inicio:
                fin = corte

        fragmento = texto[inicio:fin].strip()

        if fragmento:
            yield inicio, fragmento

        if fin >= len(texto):
            break

        inicio = max(fin - OVERLAP_CHARS, inicio + 1)


def detectar_seccion(texto: str, inicio: int, ruta: str) -> str:
    patron = re.compile(
        r"(?m)^\s*(?:#{1,6}\s+.+|"
        r"(?:async\s+)?def\s+\w+.*|"
        r"class\s+\w+.*|"
        r"export\s+(?:default\s+)?(?:function|class|const)\s+\w+.*)$"
    )

    coincidencias = list(patron.finditer(texto[:inicio]))

    if coincidencias:
        return coincidencias[-1].group().strip()[:160]

    siguientes = patron.search(texto[inicio:inicio + 500])

    if siguientes:
        return siguientes.group().strip()[:160]

    return ruta


def extraer_registros():
    archivos = obtener_archivos()
    registros = []

    for path, area in archivos:
        ruta = path.relative_to(ROOT).as_posix()

        try:
            texto = path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        except OSError as error:
            print(f"No se pudo leer {ruta}: {type(error).__name__}")
            continue

        # Evitar indexar accidentalmente algunas claves escritas
        # directamente como valores de asignaciones.
        texto = SECRET_PATTERN.sub(
            lambda match: match.group(1) + '"<REDACTED>"',
            texto,
        )

        if not texto.strip():
            continue

        for numero, (inicio, fragmento) in enumerate(
            dividir_texto(texto),
            start=1,
        ):
            identificador = hashlib.sha256(
                f"{ruta}:{numero}".encode("utf-8")
            ).hexdigest()[:24]

            registros.append({
                "id": f"proyecto-{identificador}",
                "texto": fragmento,
                "metadata": {
                    "source_type": "project_context",
                    "source_path": ruta,
                    "area": area,
                    "extension": path.suffix.lower(),
                    "chunk_index": numero,
                    "section": detectar_seccion(
                        texto, inicio, ruta
                    ),
                },
            })

    return archivos, registros


def main():
    if not DB_PATH.is_dir():
        raise SystemExit(
            "No existe data/chroma. Revisa primero la ingesta de seguridad."
        )

    archivos, registros = extraer_registros()

    if not registros:
        raise SystemExit(
            "No se encontraron archivos para indexar. No se modificó ChromaDB."
        )

    cliente = chromadb.PersistentClient(path=str(DB_PATH))

    try:
        coleccion = cliente.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        anteriores = coleccion.get()

        if anteriores["ids"]:
            coleccion.delete(ids=anteriores["ids"])

        coleccion.add(
            ids=[r["id"] for r in registros],
            documents=[r["texto"] for r in registros],
            metadatas=[r["metadata"] for r in registros],
        )

        print("\n=== INGESTA DEL CONTEXTO DEL PROYECTO ===")
        print("Archivos encontrados:", len(archivos))
        print("Fragmentos indexados:", len(registros))
        print("Colección:", COLLECTION_NAME)
        print("Registros guardados:", coleccion.count())

        print("\n=== DISTRIBUCIÓN POR ÁREA ===")
        areas = Counter(r["metadata"]["area"] for r in registros)

        for area, cantidad in sorted(areas.items()):
            print(f"{area}: {cantidad} fragmentos")

        print("\n=== PRUEBA DE RECUPERACIÓN ===")

        resultados = coleccion.query(
            query_texts=[
                "¿Cómo se organiza el backend, el frontend y las pruebas QA?"
            ],
            n_results=min(3, coleccion.count()),
            include=["metadatas", "distances"],
        )

        for indice, metadata in enumerate(
            resultados["metadatas"][0] or [],
            start=1,
        ):
            distancia = resultados["distances"][0][indice - 1]

            print(
                f"{indice}. {metadata['source_path']} "
                f"| {metadata['area']} "
                f"| distancia={distancia:.4f}"
            )

    finally:
        cliente.close()


if __name__ == "__main__":
    main()
