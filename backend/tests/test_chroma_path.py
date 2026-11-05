"""Validacion de ruta configurable de ChromaDB para despliegue."""

from pathlib import Path

from app.services import rag


def test_chroma_default_sin_variable(monkeypatch):
    monkeypatch.delenv("CHROMA_PATH", raising=False)
    assert rag.obtener_ruta_chroma() == rag.ROOT / "data" / "chroma"


def test_chroma_usa_volumen_externo(monkeypatch, tmp_path):
    volumen = tmp_path / "indice"
    monkeypatch.setenv("CHROMA_PATH", str(volumen))
    assert rag.obtener_ruta_chroma() == volumen
    assert isinstance(rag.obtener_ruta_chroma(), Path)


def test_chroma_variable_vacia_preserva_ruta_local(monkeypatch):
    monkeypatch.setenv("CHROMA_PATH", "   ")
    assert rag.obtener_ruta_chroma() == rag.ROOT / "data" / "chroma"
