"""Integración real de evidencia Ruff/Bandit con el planificador del agente.

Se simulan las herramientas externas para validar contratos sin llamar a Gemini.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models.analisis import InformeModelo
from app.routes.agente import router
from app.services.agente import (
    DecisionAgente,
    SolicitudAgente,
    ejecutar_agente,
    resumen_estatico_planificador,
)
from app.services.llm import LLMError
from app.services.static_analysis import (
    EstadoHerramienta,
    HallazgoEstatico,
    ResultadoEstatico,
)


def solicitud(max_pasos=3):
    return SolicitudAgente(
        archivo="prueba.py",
        codigo="import os\nresultado = eval(input())\n",
        max_pasos=max_pasos,
    )


def analisis_estatico(archivo="prueba.py"):
    return ResultadoEstatico(
        archivo=archivo,
        estado="completo",
        herramientas=[
            EstadoHerramienta(herramienta="ruff", estado="ok", hallazgos=1),
            EstadoHerramienta(herramienta="bandit", estado="ok", hallazgos=1),
        ],
        hallazgos=[
            HallazgoEstatico(
                herramienta="ruff", regla="F401", tipo="calidad",
                linea=1, severidad="baja",
                titulo="Importación sin usar",
                descripcion="Observación de calidad",
            ),
            HallazgoEstatico(
                herramienta="bandit", regla="B307", tipo="seguridad",
                linea=2, severidad="alta",
                titulo="Posible eval inseguro",
                descripcion="Patrón de riesgo",
                confianza="alta",
            ),
        ],
    )


def test_planificador_consume_reglas_reales_antes_de_escoger_herramienta():
    llamadas = []
    estaticos = []

    def ejecutar_estatico(codigo, archivo):
        estaticos.append((codigo, archivo))
        return analisis_estatico(archivo)

    def planificador(codigo, pasos):
        evidencia = pasos[0].resultado["evidencia_ruff_bandit"]
        llamadas.append(evidencia)
        assert evidencia["estado"] == "completo"
        assert evidencia["total_hallazgos"] == 2
        assert [h["regla"] for h in evidencia["reglas"]] == ["F401", "B307"]
        assert not any("descripcion" in h for h in evidencia["reglas"])
        return DecisionAgente(
            herramienta="detectar_llamadas_sensibles" if len(pasos) == 1 else "finalizar",
            motivo="Validar B307 detectado por Bandit",
        )

    resultado = ejecutar_agente(
        solicitud(), planificador=planificador,
        analizador=lambda codigo: InformeModelo(hallazgos=[]),
        inspeccion_estatica=ejecutar_estatico,
    )
    assert len(estaticos) == 1
    assert len(llamadas) == 2
    assert resultado.estatico == analisis_estatico()
    assert [p.origen for p in resultado.pasos] == ["automatico", "gemini"]
    assert [d.estado for d in resultado.decisiones] == ["ejecutada", "finalizar"]
    assert len(resultado.pasos) <= solicitud().max_pasos


def test_informe_estatico_no_se_reduce_al_resumen_para_gemini():
    base = analisis_estatico()
    for i in range(30):
        base.hallazgos.append(HallazgoEstatico(
            herramienta="bandit", regla=f"B{i + 400}", tipo="seguridad",
            linea=2, severidad="baja", titulo="Regla de prueba",
            descripcion="Texto que no se debe enviar al planificador",
        ))
    resumen = resumen_estatico_planificador(base)
    assert len(resumen["reglas"]) == 20
    assert resumen["total_hallazgos"] == len(base.hallazgos)
    assert "Texto que no se debe enviar" not in str(resumen)
    assert len(base.hallazgos) == 32


def test_fallo_estatico_no_se_presenta_como_inspeccion_correcta():
    def falla(codigo, archivo):
        raise RuntimeError("NO_PUBLICAR_ERROR_ESTATICO_INTERNO")

    report = ejecutar_agente(
        solicitud(max_pasos=1),
        planificador=lambda *args: (_ for _ in ()).throw(
            AssertionError("No usar Gemini si max_pasos=1")
        ),
        analizador=lambda codigo: InformeModelo(hallazgos=[]),
        inspeccion_estatica=falla,
    )
    assert report.estatico.estado == "no_disponible"
    assert all(h.estado == "error" for h in report.estatico.herramientas)
    assert "NO_PUBLICAR" not in report.estatico.mensaje
    assert report.decisiones == []


def test_api_expone_estatico_y_lo_conserva_si_gemini_falla(monkeypatch):
    import app.routes.agente as route

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    def ejecucion_con_fallo(entrada):
        def planificador(codigo, pasos):
            return DecisionAgente(
                herramienta="detectar_llamadas_sensibles",
                motivo="Validar regla B307",
            )

        def falla_llm(codigo):
            raise LLMError("MENSAJE_INTERNO_NO_PUBLICAR", 503)

        return ejecutar_agente(
            entrada, planificador=planificador,
            analizador=falla_llm,
            inspeccion_estatica=lambda codigo, archivo: analisis_estatico(archivo),
        )

    monkeypatch.setattr(route, "ejecutar_agente", ejecucion_con_fallo)
    response = client.post(
        "/api/v1/agente/analizar", json=solicitud().model_dump()
    )
    assert response.status_code == 200
    data = response.json()
    assert data["modo"] == "degradado"
    assert data["fase_error"] == "informe"
    assert data["informe"]["hallazgos"] == []
    assert data["informe"]["fuentes"] == []
    assert [h["regla"] for h in data["analisis_estatico"]["hallazgos"]] == [
        "F401", "B307"
    ]
    assert data["analisis_estatico"]["estado"] == "completo"
    assert len(data["pasos"]) <= 3
    assert "MENSAJE_INTERNO_NO_PUBLICAR" not in response.text


def test_api_exito_conserva_hallazgos_estaticos_fuera_del_rag(monkeypatch):
    import app.routes.agente as route

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    def ejecutar_simulado(entrada):
        return ejecutar_agente(
            entrada,
            planificador=lambda codigo, pasos: DecisionAgente(
                herramienta="finalizar", motivo="Evidencia suficiente",
            ),
            analizador=lambda codigo: InformeModelo(hallazgos=[]),
            inspeccion_estatica=lambda codigo, archivo: analisis_estatico(archivo),
        )

    monkeypatch.setattr(route, "ejecutar_agente", ejecutar_simulado)
    response = client.post(
        "/api/v1/agente/analizar", json=solicitud().model_dump()
    )
    assert response.status_code == 200
    data = response.json()
    assert data["modo"] == "gemini_real"
    assert data["informe"]["hallazgos"] == []
    assert data["analisis_estatico"]["estado"] == "completo"
    assert len(data["analisis_estatico"]["hallazgos"]) == 2
    assert len(data["decisiones"]) == 1
    assert data["decisiones"][0]["herramienta"] == "finalizar"


def test_panel_publica_evidencia_estatica_sin_disfrazarla_como_cita_rag():
    app = FastAPI()
    app.include_router(router)
    response = TestClient(app).get("/agente/demo")
    assert response.status_code == 200
    assert "Ruff + Bandit" in response.text
    assert "analisis_estatico" in response.text
    assert "No constituyen citas RAG" in response.text
