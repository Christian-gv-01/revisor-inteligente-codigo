
from pathlib import Path
import os
import hashlib
import re
from collections import Counter

import chromadb


ROOT = Path(__file__).resolve().parents[1]
configurada = os.getenv("CHROMA_PATH", "").strip()
DB_PATH = Path(configurada).expanduser() if configurada else ROOT / "data" / "chroma"
COLLECTION_NAME = "contexto_proyecto"

MAX_CHARS = 3500
OVERLAP_CHARS = 350
BATCH_SIZE = 100

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".pytest_cache",
    "coverage",
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

STRUCTURE_PATTERN = re.compile(
    r"^(?:#{1,6}\s+.+|"
    r"(?:async\s+)?def\s+\w+.*|"
    r"class\s+\w+.*|"
    r"export\s+(?:default\s+)?"
    r"(?:function|class|const)\s+\w+.*)"
)


def archivo_permitido(path: Path) -> bool:
    """Determina si un archivo puede incorporarse a la ingesta."""

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

    try:
        return path.stat().st_size <= 500_000
    except OSError as error:
        raise RuntimeError(
            f"No se pudo comprobar el archivo {path}"
        ) from error


def obtener_archivos() -> list[tuple[Path, str]]:
    """Encuentra los archivos permitidos del repositorio."""

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
    """
    Divide el texto respetando líneas y priorizando límites
    estructurales. Conserva un solapamiento entre fragmentos.
    """

    if not texto:
        return

    lineas = texto.splitlines(keepends=True)
    posiciones = []
    posicion = 0

    for linea in lineas:
        posiciones.append((posicion, linea))
        posicion += len(linea)

    inicios_linea = [p for p, _ in posiciones]

    inicios_estructura = [
        p
        for p, linea in posiciones
        if STRUCTURE_PATTERN.match(linea)
    ]

    inicios_bloque = [
        p
        for p, linea in posiciones
        if not linea.strip()
    ]

    longitud = len(texto)
    inicio = 0

    while inicio < longitud:
        limite = min(inicio + MAX_CHARS, longitud)

        if limite == longitud:
            fin = longitud
        else:
            minimo = inicio + MAX_CHARS // 2

            candidatos = [
                p for p in inicios_estructura
                if minimo < p <= limite
            ]

            if not candidatos:
                candidatos = [
                    p for p in inicios_bloque
                    if minimo < p <= limite
                ]

            if not candidatos:
                candidatos = [
                    p for p in inicios_linea
                    if minimo < p <= limite
                ]

            fin = max(candidatos) if candidatos else limite

        fragmento = texto[inicio:fin].strip()

        if fragmento:
            yield inicio, fragmento

        if fin >= longitud:
            break

        objetivo = max(inicio + 1, fin - OVERLAP_CHARS)

        candidatos = [
            p for p in inicios_estructura
            if objetivo <= p < fin
        ]

        if not candidatos:
            candidatos = [
                p for p in inicios_bloque
                if objetivo <= p < fin
            ]

        if not candidatos:
            candidatos = [
                p for p in inicios_linea
                if objetivo <= p < fin
            ]

        inicio = min(candidatos) if candidatos else fin


def detectar_seccion(
    texto: str,
    inicio: int,
    ruta: str,
) -> str:
    """Obtiene una sección próxima al comienzo del fragmento."""

    siguientes = STRUCTURE_PATTERN.search(
        texto[inicio:inicio + 500]
    )

    if siguientes and siguientes.start() == 0:
        return siguientes.group().strip()[:160]

    anteriores = list(
        STRUCTURE_PATTERN.finditer(texto[:inicio])
    )

    if anteriores:
        return anteriores[-1].group().strip()[:160]

    if siguientes:
        return siguientes.group().strip()[:160]

    return ruta


def extraer_registros():
    """
    Lee y prepara los fragmentos antes de modificar ChromaDB.
    Si falla la lectura, cancela la ingesta.
    """

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
            raise RuntimeError(
                f"No se pudo leer {ruta}. "
                "Se cancela la ingesta para proteger la colección."
            ) from error

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
                        texto,
                        inicio,
                        ruta,
                    ),
                },
            })

    ids = [registro["id"] for registro in registros]

    if len(ids) != len(set(ids)):
        raise RuntimeError(
            "Se encontraron IDs duplicados. "
            "No se modificará ChromaDB."
        )

    return archivos, registros


def guardar_registros(coleccion, registros):
    """Inserta o actualiza registros por lotes sin vaciar la colección."""

    for inicio in range(0, len(registros), BATCH_SIZE):
        lote = registros[inicio:inicio + BATCH_SIZE]

        coleccion.upsert(
            ids=[registro["id"] for registro in lote],
            documents=[
                registro["texto"] for registro in lote
            ],
            metadatas=[
                registro["metadata"] for registro in lote
            ],
        )


def mostrar_resultados(coleccion, archivos, registros):
    """Muestra estadísticas y una prueba de recuperación."""

    print("\n=== INGESTA DEL CONTEXTO DEL PROYECTO ===")
    print("Archivos encontrados:", len(archivos))
    print("Fragmentos preparados:", len(registros))
    print("Colección:", COLLECTION_NAME)
    print("Registros guardados:", coleccion.count())

    print("\n=== DISTRIBUCIÓN POR ÁREA ===")

    areas = Counter(
        registro["metadata"]["area"]
        for registro in registros
    )

    for area, cantidad in sorted(areas.items()):
        print(f"{area}: {cantidad} fragmentos")

    print("\n=== PRUEBA DE RECUPERACIÓN ===")

    total = coleccion.count()

    if total == 0:
        print("La colección no contiene registros.")
        return

    resultados = coleccion.query(
        query_texts=[
            "¿Cómo se organiza el backend, "
            "el frontend y las pruebas QA?"
        ],
        n_results=min(3, total),
        include=["metadatas", "distances"],
    )

    metadatos = resultados["metadatas"][0] or []
    distancias = resultados["distances"][0] or []

    for indice, metadata in enumerate(metadatos):
        distancia = distancias[indice]

        print(
            f"{indice + 1}. "
            f"{metadata.get('source_path', 'desconocido')} "
            f"| {metadata.get('area', 'sin área')} "
            f"| distancia={distancia:.4f}"
        )


def main():
    if not DB_PATH.is_dir():
        raise SystemExit(
            f"No existe el indice ChromaDB en {DB_PATH}. "
            "Revisa primero la ingesta de seguridad."
        )

    try:
        archivos, registros = extraer_registros()
    except (RuntimeError, OSError) as error:
        raise SystemExit(
            f"INGESTA CANCELADA: {error}"
        ) from error

    if not registros:
        raise SystemExit(
            "No se encontraron registros. "
            "No se modificó ChromaDB."
        )

    cliente = chromadb.PersistentClient(path=str(DB_PATH))

    try:
        coleccion = cliente.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        guardar_registros(coleccion, registros)

        print(
            "\nLos registros antiguos no se eliminan "
            "automáticamente."
        )

        mostrar_resultados(
            coleccion,
            archivos,
            registros,
        )

    finally:
        cliente.close()


if __name__ == "__main__":
    main()
