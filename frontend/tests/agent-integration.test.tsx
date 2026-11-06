import { afterEach, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { analyzeWithAgent, parseAgentResponse } from "../src/services/api";
import { createReport } from "../src/services/report";
import { FindingsPanel } from "../src/components/FindingsPanel";
import type { AnalysisInput } from "../src/types/analysis";

const input: AnalysisInput = { tipo: "codigo", archivo: "muestra.py", codigo: "dato=input()\nreturn_value=eval(dato)\n", url: "", fichero: null };
const response = {
  archivo: "muestra.py", modo: "gemini_real", max_pasos: 3, fase_error: null,
  pasos: [{ numero: 1, herramienta: "inspeccionar_estructura", motivo: "Estructura", origen: "automatico", resultado: { sintaxis_valida: true } },
    { numero: 2, herramienta: "detectar_llamadas_sensibles", motivo: "Comprobar llamada", origen: "gemini", resultado: { sintaxis_valida: true, indicadores: [{ linea: 2, llamada: "eval" }] } }],
  decisiones: [{ numero: 1, herramienta: "detectar_llamadas_sensibles", motivo: "Comprobar llamada", estado: "ejecutada" }],
  analisis_estatico: { archivo: "muestra.py", estado: "completo", hallazgos: [], herramientas: [{ herramienta: "ruff", estado: "ok", hallazgos: 0 }, { herramienta: "bandit", estado: "ok", hallazgos: 0 }], mensaje: null },
  informe: { archivo: "muestra.py", estado: "analizado", fuentes: [{ id: "seguridad_python-001", documento: "seguridad.md", seccion: "eval", fuente: "CWE", url: "https://cwe.mitre.org/", distancia: 0.1 }],
    hallazgos: [{ linea: 2, fragmento_codigo: "return_value=eval(dato)", linea_reportada_modelo: 1, severidad: "alta", categoria: "ejecución", titulo: "Eval inseguro", explicacion: "Revisar entrada", correccion_sugerida: "Parser limitado", referencias: ["seguridad_python-001"] }] },
};

afterEach(() => vi.unstubAllGlobals());

it("presenta y exporta informe y traza de una sola respuesta", () => {
  const result = parseAgentResponse(response, input);
  const html = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
  expect(html).toContain("Proceso de revisión del agente");
  expect(html).toContain("Línea 2: eval");
  expect(html).toContain("Eval inseguro");
  expect(createReport(result).traza_agente?.pasos).toHaveLength(2);
  expect(result.hallazgos[0].linea_reportada_modelo).toBe(1);
});

it("rechaza una traza inventada con herramienta fuera de la lista", () => {
  expect(() => parseAgentResponse({ ...response, pasos: [{ ...response.pasos[0], herramienta: "ejecutar_shell" }] }, input)).toThrow();
});

it("rechaza indicadores fuera del archivo y hallazgos sin anclaje", () => {
  const copia = structuredClone(response);
  copia.pasos[1].resultado.indicadores = [{ linea: 999, llamada: "eval" }];
  expect(() => parseAgentResponse(copia, input)).toThrow();
  const otra = structuredClone(response);
  otra.informe.hallazgos[0].linea = 1;
  expect(() => parseAgentResponse(otra, input)).toThrow();
});

it("mantiene el respaldo parcial y la fase de error", () => {
  const result = parseAgentResponse({ ...response, modo: "degradado", fase_error: "informe", informe: { ...response.informe, estado: "parcial", hallazgos: [], fuentes: [] } }, input);
  expect(result.estado).toBe("parcial");
  expect(result.traza_agente?.fase_error).toBe("informe");
});

it("el servicio usa el endpoint del agente también para un archivo Python", async () => {
  const fetcher = vi.fn().mockResolvedValue({ ok: true, json: async () => response });
  vi.stubGlobal("fetch", fetcher);
  await analyzeWithAgent({ ...input, tipo: "python", fichero: new File([input.codigo], input.archivo) });
  expect(fetcher.mock.calls[0][0]).toContain("/api/v1/agente/analizar");
  expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({ archivo: input.archivo, codigo: input.codigo, max_pasos: 3, version_herramientas: "2" });
});
