"""Instantáneas de proyectos y autorización de gasto; sin generar ni ejecutar código."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import PurePosixPath
import secrets
import sqlite3
import time

from app.config import settings

DB_PATH = settings.obtener_ruta_correcciones().parent / "presupuestos.sqlite3"
TTL = 300
LEASE = 240
MAX_FILAS = 100
MAX_SESION = 5
COOKIE = "codeguard_proyectos"


class ProyectoError(Exception):
    def __init__(self, mensaje, codigo):
        super().__init__(mensaje)
        self.codigo = codigo


def huella(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def canon(datos):
    return json.dumps(datos, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def perfil(n):
    segundos, limite = settings.limites_solicitud("/api/v1/archivos/zip")
    intentos = settings.obtener_intentos_llm()
    return {"modelo": settings.obtener_modelo_gemini(), "analisis_previstos": n,
            "intentos_por_analisis": intentos, "max_intentos_proveedor": min(n * intentos, limite),
            "plazo_cooperativo_segundos": segundos}


@contextmanager
def conexion():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
    try:
        os.chmod(DB_PATH, 0o600)
        db.execute("PRAGMA secure_delete=ON")
        db.execute("CREATE TABLE IF NOT EXISTS proyectos (id TEXT PRIMARY KEY, propietario TEXT NOT NULL, estado TEXT NOT NULL, caduca REAL NOT NULL, manifiesto TEXT NOT NULL, sha TEXT NOT NULL, snapshot TEXT, resultado TEXT)")
        db.execute("CREATE INDEX IF NOT EXISTS proyectos_caducidad ON proyectos(caduca)")
        db.execute("BEGIN IMMEDIATE")
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def limpiar():
    with conexion() as db:
        db.execute("DELETE FROM proyectos WHERE caduca <= ?", (time.time(),))


def crear(tipo, origen, sha_entrada, archivos, propietario):
    if tipo not in {"zip", "github"} or not 1 <= len(archivos) <= 5 or sum(len(c) for _, c in archivos) > 12000:
        raise ProyectoError("Proyecto fuera de los límites permitidos.", 413)
    archivos = sorted(archivos)
    if len({n for n, _ in archivos}) != len(archivos):
        raise ProyectoError("Los archivos deben tener nombres únicos.", 400)
    for nombre, codigo in archivos:
        p = PurePosixPath(nombre)
        if len(nombre) > 512 or p.is_absolute() or ".." in p.parts or "\\" in nombre or "\0" in nombre or not nombre.lower().endswith(".py") or not codigo.strip() or "\0" in codigo:
            raise ProyectoError("Archivo de proyecto inválido.", 400)
    manifiesto = {"tipo": tipo, "origen": origen, "sha256_entrada": sha_entrada,
        "archivos": [{"archivo": n, "caracteres": len(c), "sha256": huella(c)} for n, c in archivos],
        "total_archivos": len(archivos), "presupuesto": perfil(len(archivos))}
    digest = huella(canon(manifiesto))
    identificador = secrets.token_urlsafe(32)
    caduca = time.time() + TTL
    with conexion() as db:
        db.execute("DELETE FROM proyectos WHERE caduca <= ?", (time.time(),))
        total = db.execute("SELECT count(*) FROM proyectos").fetchone()[0]
        propias = db.execute("SELECT count(*) FROM proyectos WHERE propietario=?", (propietario,)).fetchone()[0]
        if total >= MAX_FILAS or propias >= MAX_SESION:
            raise ProyectoError("Límite temporal de presupuestos alcanzado.", 429)
        db.execute("INSERT INTO proyectos VALUES (?, ?, 'pendiente', ?, ?, ?, ?, NULL)",
            (huella(identificador), propietario, caduca, canon(manifiesto), digest, canon(archivos)))
    return {"version": "1", "presupuesto_id": identificador, "estado": "pendiente_confirmacion",
            **manifiesto, "sha256_manifiesto": digest,
            "caduca_en": datetime.fromtimestamp(caduca, timezone.utc).isoformat()}


def decidir(identificador, propietario, sha, decision):
    """Claim atómico: una sola ejecución por autorización, incluso entre procesos."""
    with conexion() as db:
        fila = db.execute("SELECT estado,caduca,manifiesto,sha,snapshot,resultado FROM proyectos WHERE id=? AND propietario=?",
                          (huella(identificador), propietario)).fetchone()
        if fila is None:
            raise ProyectoError("El presupuesto no existe.", 404)
        estado, caduca, texto, original, snapshot, resultado = fila
        if caduca <= time.time():
            raise ProyectoError("El presupuesto caducó. Revisa uno nuevo.", 410)
        if not secrets.compare_digest(original, sha):
            raise ProyectoError("El presupuesto no coincide con el revisado.", 409)
        if decision == "rechazar":
            if estado not in {"pendiente", "rechazado"}:
                raise ProyectoError("El análisis ya comenzó; no se puede revocar su consumo.", 409)
            db.execute("UPDATE proyectos SET estado='rechazado',snapshot=NULL,resultado=NULL WHERE id=?", (huella(identificador),))
            return {"version": "1", "presupuesto_id": identificador, "estado": "rechazado"}
        if estado == "finalizado":
            return json.loads(resultado)
        if estado != "pendiente":
            raise ProyectoError("El presupuesto ya fue utilizado o está en curso.", 409)
        manifiesto = json.loads(texto)
        if perfil(manifiesto["total_archivos"]) != manifiesto["presupuesto"]:
            raise ProyectoError("La configuración cambió. Revisa un presupuesto nuevo.", 409)
        db.execute("UPDATE proyectos SET estado='ejecutando',caduca=? WHERE id=?", (time.time() + LEASE, huella(identificador)))
        return {"snapshot": json.loads(snapshot), "manifiesto": manifiesto}


def finalizar(identificador, propietario, resultado):
    serializado = canon(resultado)
    if len(serializado.encode()) > 1_000_000:
        raise ProyectoError("El informe supera el límite temporal de almacenamiento.", 413)
    with conexion() as db:
        cambio = db.execute("UPDATE proyectos SET estado='finalizado',snapshot=NULL,resultado=?,caduca=? WHERE id=? AND propietario=? AND estado='ejecutando' AND caduca>?",
                            (serializado, time.time() + TTL, huella(identificador), propietario, time.time()))
        if cambio.rowcount != 1:
            raise ProyectoError("El análisis superó la vigencia de su autorización.", 410)


def fallar(identificador, propietario):
    # Mantener el presupuesto consumido; repetir la petición no regenera con IA.
    try:
        with conexion() as db:
            db.execute("UPDATE proyectos SET estado='fallido',snapshot=NULL,resultado=NULL WHERE id=? AND propietario=? AND estado='ejecutando'",
                       (huella(identificador), propietario))
    except (sqlite3.Error, OSError):
        pass
