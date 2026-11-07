"""Pruebas deterministas de la evaluación A/B. Nunca llaman a Gemini."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "eval"))

import evaluar_planificador_agente as modulo  # noqa: E402
from app.services.agente import DecisionAgente  # noqa: E402
from app.services.llm import LLMError  # noqa: E402
from app.services.static_analysis import (  # noqa: E402
    EstadoHerramienta, HallazgoEstatico, ResultadoEstatico,
)


def estatico_completo(codigo: str, archivo: str) -> ResultadoEstatico:
    return ResultadoEstatico(
        archivo=archivo,
        estado="completo",
        herramientas=[
            EstadoHerramienta(herramienta="ruff", estado="ok", hallazgos=0),
            EstadoHerramienta(herramienta="bandit", estado="ok", hallazgos=1),
        ],
        hallazgos=[
            HallazgoEstatico(
                herramienta="bandit", regla="B307", tipo="seguridad",
                linea=1, severidad="media", titulo="Ejemplo simulado",
                descripcion="No debe aparecer en resumen enviado a Gemini",
            ),
        ],
    )


def test_dataset_sintetico_valido_sin_ejecutar_codigo():
    casos = modulo.cargar_casos(modulo.CASOS_DEFECTO)
    assert len(casos) == 6
    assert len({c["id"] for c in casos}) == 6
    assert {c["categoria"] for c in casos} == {
        "llamada_sensible", "sql_dinamico", "control_limpio"
    }
    assert all(c["archivo"].endswith(".py") for c in casos)


def test_comparacion_modifica_unicamente_contexto_y_contrabalancea_orden():
    casos = modulo.cargar_casos(modulo.CASOS_DEFECTO)[:2]
    llamadas = []
    estaticos = []

    def analizar(codigo, archivo):
        estaticos.append(archivo)
        return estatico_completo(codigo, archivo)

    def decidir(codigo, pasos):
        assert len(pasos) == 1
        assert pasos[0].herramienta == "inspeccionar_estructura"
        datos = pasos[0].resultado
        tiene_contexto = "evidencia_ruff_bandit" in datos
        if tiene_contexto:
            assert datos["evidencia_ruff_bandit"]["reglas"][0]["regla"] == "B307"
            assert "descripcion" not in datos["evidencia_ruff_bandit"]["reglas"][0]
        llamadas.append((codigo, datos["total_lineas"], tiene_contexto))
        return DecisionAgente(
            herramienta="detectar_llamadas_sensibles" if tiene_contexto else "finalizar",
            motivo="Decisión simulada para validar experimento",
        )

    filas, excluidos = modulo.ejecutar_pares(
        casos, repeticiones=2, pausa=0,
        planificador=decidir, analizador_estatico=analizar,
    )
    assert not excluidos
    assert estaticos == [c["archivo"] for c in casos]
    assert len(llamadas) == 8
    assert len(filas) == 8
    assert {f["condicion"] for f in filas} == set(modulo.CONDICIONES)
    for c in casos:
        filas_c = [f for f in filas if f["caso_id"] == c["id"]]
        assert len(filas_c) == 4
        for rep in (1, 2):
            pareja = [f for f in filas_c if f["repeticion"] == rep]
            assert len(pareja) == 2
            assert pareja[0]["condicion"] != pareja[1]["condicion"]
            assert {f["sha256_codigo"] for f in pareja} == {
                pareja[0]["sha256_codigo"]
            }

    informe = modulo.resumen_estudio(filas, excluidos)
    assert informe["pares_completos"] == 4
    assert informe["pares_con_cambio"] == 4
    assert informe["tasa_cambio_de_decision"] == 1.0
    assert informe["pares_no_comparables"] == 0


def test_fallo_del_proveedor_no_cuenta_como_cambio_ni_acierto():
    casos = modulo.cargar_casos(modulo.CASOS_DEFECTO)[:2]

    def decidir(codigo, pasos):
        if "evidencia_ruff_bandit" in pasos[0].resultado:
            raise LLMError("DETALLE_CRUDO_NO_PUBLICAR", 503)
        return DecisionAgente(herramienta="finalizar", motivo="No continuar")

    filas, excluidos = modulo.ejecutar_pares(
        casos, planificador=decidir,
        analizador_estatico=estatico_completo,
    )
    informe = modulo.resumen_estudio(filas, excluidos)
    assert informe["pares_completos"] == 0
    assert informe["pares_no_comparables"] == 2
    assert informe["tasa_cambio_de_decision"] is None
    assert informe["condiciones"]["con_contexto"]["errores"] == 2
    assert all(
        "DETALLE_CRUDO_NO_PUBLICAR" not in json.dumps(f)
        for f in filas
    )


def test_excluye_casos_sin_ruff_y_bandit_completos():
    casos = modulo.cargar_casos(modulo.CASOS_DEFECTO)[:2]

    def parcial(codigo, archivo):
        resultado = estatico_completo(codigo, archivo)
        resultado.estado = "parcial"
        resultado.herramientas[1].estado = "no_disponible"
        return resultado

    def no_llamar(*args):
        raise AssertionError("El planificador no se debe ejecutar sin herramientas")

    filas, excluidos = modulo.ejecutar_pares(
        casos, planificador=no_llamar, analizador_estatico=parcial,
    )
    assert filas == []
    assert len(excluidos) == 2
    assert all(x["motivo"] == "ruff_bandit_no_completados" for x in excluidos)


@pytest.mark.parametrize("repeticiones", [0, -1, 4])
def test_rechaza_repeticiones_fuera_del_presupuesto(repeticiones):
    casos = modulo.cargar_casos(modulo.CASOS_DEFECTO)[:2]
    with pytest.raises(ValueError):
        modulo.ejecutar_pares(
            casos, repeticiones=repeticiones,
            analizador_estatico=estatico_completo,
        )


def test_reporte_exporta_resumen_sin_codigo_o_motivos_privados(tmp_path):
    casos = modulo.cargar_casos(modulo.CASOS_DEFECTO)[:2]
    filas, excluidos = modulo.ejecutar_pares(
        casos, planificador=lambda codigo, pasos: DecisionAgente(
            herramienta="finalizar", motivo="NO EXPORTAR ESTE TEXTO"
        ),
        analizador_estatico=estatico_completo,
    )
    resumen = modulo.resumen_estudio(filas, excluidos)
    archivo = modulo.guardar(
        filas, resumen, salida=tmp_path,
        metadatos={"modelo": "modelo-test", "casos": 2},
    )
    assert archivo.exists()
    assert (tmp_path / "resultados.csv").exists()
    assert (tmp_path / "resumen.md").exists()
    for salida in tmp_path.iterdir():
        contenido = salida.read_text(encoding="utf-8")
        assert "NO EXPORTAR ESTE TEXTO" not in contenido
        assert "import os" not in contenido
    assert json.loads(archivo.read_text())["resumen"]["pares_completos"] == 2


def test_dry_run_no_hace_ninguna_llamada_real(monkeypatch, capsys):
    def no_ejecutar(*args, **kwargs):
        raise AssertionError("No se permiten consultas a Gemini sin --ejecutar")

    monkeypatch.setattr(modulo, "ejecutar_pares", no_ejecutar)
    monkeypatch.setattr(sys, "argv", ["evaluar_planificador_agente.py"])
    assert modulo.main() == 0
    out = capsys.readouterr().out
    assert "ninguna solicitud" in out
    assert "Máximo de solicitudes: 12" in out


def test_seis_pares_v2_miden_argumentos_y_no_atribuyen_uso_a_un_stub():
    casos = modulo.cargar_casos(modulo.CASOS_DEFECTO)
    vistas = []
    def decidir(codigo, pasos, *, version_herramientas):
        vistas.append(version_herramientas)
        return DecisionAgente(herramienta="ampliar_contexto", motivo="No publicar motivo",
            argumentos={"linea": 2 if "evidencia_ruff_bandit" in pasos[0].resultado else 1})
    filas, excluidos = modulo.ejecutar_pares(casos, version_herramientas="2",
        planificador=decidir, analizador_estatico=estatico_completo)
    s = modulo.resumen_estudio(filas, excluidos)
    assert vistas == ["2"] * 12
    assert s["pares_completos"] == s["pares_con_cambio"] == 6
    assert all(f["consumo_ia"]["intentos"] == 0 for f in filas)
    assert all("No publicar motivo" not in json.dumps(f) for f in filas)
