from app.services import rag


class FakeCollection:

    def __init__(self):
        self.query_kwargs = None

        self.metadata = {
            "section": "Regla 1: Evitar eval",
            "document": "seguridad_python.md",
            "source_name": "MITRE CWE-94",
            "source_url": "https://cwe.mitre.org/data/definitions/94.html",
            "source_section": "Code Injection",
            "review_date": "2026-10-28",
            "effective_date": "2026-01-15",
        }

    def count(self):
        return 1

    def query(self, **kwargs):
        self.query_kwargs = kwargs

        return {
            "documents": [["Contenido de prueba de seguridad"]],
            "metadatas": [[self.metadata]],
            "distances": [[0.1]],
            "ids": [["seguridad_python-test-001"]],
        }


class FakeClient:

    def __init__(self, collection):
        self.collection = collection
        self.closed = False
        self.requested_collections = []

    def get_collection(self, name):
        self.requested_collections.append(name)

        if name != "seguridad_python":
            raise ValueError("Coleccion no disponible")

        return self.collection

    def close(self):
        self.closed = True


def preparar_rag(monkeypatch, tmp_path):

    collection = FakeCollection()
    client = FakeClient(collection)

    monkeypatch.setattr(rag, "DB_PATH", tmp_path)

    monkeypatch.setattr(
        rag.chromadb,
        "PersistentClient",
        lambda path: client,
    )

    return collection, client


def test_filtro_effective_date(
    monkeypatch,
    tmp_path,
):

    collection, client = preparar_rag(
        monkeypatch,
        tmp_path,
    )

    resultados = rag.buscar_fragmentos(
        "Uso inseguro de eval",
        limite=3,
        effective_date="2026-01-15",
    )

    assert collection.query_kwargs["where"] == {
        "effective_date": {
            "$eq": "2026-01-15"
        }
    }

    assert len(resultados) == 1

    assert resultados[0]["effective_date"] == "2026-01-15"

    assert client.requested_collections == [
        "seguridad_python"
    ]

    assert client.closed


def test_filtro_effective_date_combinado(
    monkeypatch,
    tmp_path,
):

    collection, client = preparar_rag(
        monkeypatch,
        tmp_path,
    )

    resultados = rag.buscar_fragmentos(
        "Uso inseguro de eval",
        limite=3,
        source_name="MITRE CWE-94",
        effective_date="2026-01-15",
    )

    assert collection.query_kwargs["where"] == {
        "$and": [
            {"source_name": {"$eq": "MITRE CWE-94"}},
            {"effective_date": {"$eq": "2026-01-15"}},
        ]
    }

    assert len(resultados) == 1

    assert resultados[0]["effective_date"] == "2026-01-15"

    assert client.closed