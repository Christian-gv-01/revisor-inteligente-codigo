"""Garantías del paquete: revisión exacta, limpieza, integridad y límite."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

SPEC = importlib.util.spec_from_file_location("empaquetador", Path(__file__).resolve().parents[1] / "scripts/empaquetar_entrega.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class Paquete(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        (self.repo / "README.md").write_text("version comprometida\n")
        self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), "-c", "user.name=QA", "-c", "user.email=qa@example.invalid", *args], stderr=subprocess.PIPE)

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture de paquete")

    def test_revision_exacta_sin_copiar_entorno_y_salida_reproducible(self):
        (self.repo / "README.md").write_text("cambio no comprometido\n")
        (self.repo / ".env").write_text("MARCADOR_FICTICIO_NO_ES_CREDENCIAL=ejemplo\n")
        out = self.root / "uno.zip"
        report = MOD.empaquetar(self.repo, out)
        report2 = MOD.empaquetar(self.repo, self.root / "dos.zip")
        self.assertEqual(report["sha256_zip"], report2["sha256_zip"])
        with zipfile.ZipFile(out) as z:
            self.assertEqual(z.read("README.md"), b"version comprometida\n")
            self.assertNotIn(".env", z.namelist())
            manifest = json.loads(z.read("ENTREGA-manifiesto.json"))
            self.assertEqual(manifest["revision"], self.git("rev-parse", "HEAD").decode().strip())
            self.assertEqual(manifest["pdf_presentacion"], [])
            self.assertIsNone(z.testzip())

    def test_proyecto_sin_pdf_vigente_se_bloquea(self):
        # El control específico de CODEGUARD no debe romper el uso genérico
        # del empaquetador con repositorios mínimos ni permitir paquetes
        # académicos sin su PDF de sustentación.
        p = self.repo / "docs" / "presentacion"
        p.mkdir(parents=True)
        (p / "README.md").write_text("Control de presentación CODEGUARD\n")
        self.commit()
        with self.assertRaisesRegex(ValueError, "PDF de entrega incorrecto"):
            MOD.empaquetar(self.repo, self.root / "sin_pdf.zip")

    def test_env_versionado_bloquea_entrega(self):
        (self.repo / ".env").write_text("MARCADOR_FICTICIO=ejemplo\n")
        self.commit()
        with self.assertRaisesRegex(ValueError, "no permitido"):
            MOD.empaquetar(self.repo, self.root / "salida.zip")

    def test_enlace_simbolico_no_se_empaqueta(self):
        try:
            os.symlink("../externo", self.repo / "enlace")
        except (OSError, NotImplementedError):
            self.skipTest("El equipo no permite crear enlaces simbólicos")
        self.commit()
        with self.assertRaisesRegex(ValueError, "no regular"):
            MOD.empaquetar(self.repo, self.root / "salida.zip")

    def test_exceso_no_deja_zip_publicable(self):
        salida = self.root / "salida.zip"
        with self.assertRaisesRegex(ValueError, "20 MB"):
            MOD.empaquetar(self.repo, salida, limite=10)
        self.assertFalse(salida.exists())
        self.assertFalse(salida.with_suffix(".zip.tmp").exists())


if __name__ == "__main__":
    unittest.main()
