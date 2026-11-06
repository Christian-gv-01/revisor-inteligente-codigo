import { afterEach, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { analyzeWithAgent, parseAgentResponse } from "../src/services/api";
import { AgentTracePanel } from "../src/components/AgentTracePanel";
import { createReport } from "../src/services/report";
import type { AnalysisInput } from "../src/types/analysis";
import request from "../../docs/contrato-agente-v2/01-solicitud-contexto-y-referencia.json";
import complete from "../../docs/contrato-agente-v2/04-respuesta-contexto-y-referencia.json";
import earlyRequest from "../../docs/contrato-agente-v2/05-solicitud-finalizacion-anticipada.json";
import early from "../../docs/contrato-agente-v2/07-respuesta-finalizacion-anticipada.json";
import failed from "../../docs/contrato-agente-v2/08-respuesta-error-herramienta.json";
import legacy from "../../docs/contrato-agente-v2/09-respuesta-v1-compatible.json";

const input: AnalysisInput = { tipo: "codigo", ...request, fichero: null, url: "" };
const shortInput: AnalysisInput = { ...input, ...earlyRequest };
afterEach(() => vi.unstubAllGlobals());

it("conserva resultados y argumentos v2 del contrato publicado al mostrar y exportar", () => {
  const result = parseAgentResponse(complete, input);
  const trace = result.traza_agente;
  expect(trace).toMatchObject({ version_herramientas: "2", terminacion: "max_pasos" });
  expect(trace?.pasos[1]).toMatchObject({ argumentos: { linea: 2 }, resultado: complete.pasos[1].resultado });
  expect(trace?.pasos[2]).toMatchObject({ argumentos: { categoria: "inyeccion_sql" }, resultado: complete.pasos[2].resultado });
  expect(createReport(result).traza_agente).toEqual(trace);
  const html = renderToStaticMarkup(<AgentTracePanel trace={trace} />);
  for (const text of ["Ampliar contexto", "Buscar referencia", "Línea solicitada: 2", "inyeccion_sql", "seguridad_python-002", "Límite de pasos alcanzado"]) expect(html).toContain(text);
  expect(html).not.toContain("No se pudo interpretar la sintaxis");
});

it("presenta finalización anticipada con síntesis, sin inventar pasos adicionales", () => {
  const result = parseAgentResponse(early, shortInput);
  expect(result.traza_agente?.pasos).toHaveLength(1);
  const html = renderToStaticMarkup(<AgentTracePanel trace={result.traza_agente} />);
  expect(html).toContain("Finalización anticipada");
  expect(html).toContain("La evidencia reunida permite pasar a la síntesis");
  expect(html).toContain("síntesis final");
});

it("muestra decisión fallida, fase herramienta y respaldo sin resultado inventado", () => {
  const result = parseAgentResponse(failed, input);
  expect(result.estado).toBe("parcial");
  const html = renderToStaticMarkup(<AgentTracePanel trace={result.traza_agente} />);
  expect(html).toContain("No completada");
  expect(html).toContain("herramienta contextual");
  expect(html).toContain("Respaldo local");
});

it("mantiene la lectura del contrato v1", () => {
  const result = parseAgentResponse(legacy, input);
  expect(result.traza_agente?.version_herramientas).toBeUndefined();
  expect(result.traza_agente?.terminacion).toBeUndefined();
});

function alter(path: string, value: unknown, original: unknown = complete): unknown {
  const copy = structuredClone(original) as Record<string, unknown>;
  const parts = path.split(".");
  let current = copy;
  for (const part of parts.slice(0, -1)) current = current[part] as Record<string, unknown>;
  current[parts.at(-1)!] = value;
  return copy;
}

it.each([
  ["version_herramientas", "3"], ["version_herramientas", undefined],
  ["terminacion", "seguro"], ["terminacion", "finalizacion_anticipada"],
  ["pasos.1.argumentos.linea", "2"], ["pasos.1.argumentos.linea", true],
  ["pasos.1.argumentos.linea", 0], ["pasos.1.argumentos.url", "https://evil.invalid"],
  ["pasos.1.resultado.linea_objetivo", 1], ["pasos.1.resultado.lineas.0.numero", 2],
  ["pasos.1.resultado.lineas.0.texto", "inventado"], ["pasos.1.resultado.lineas.0.truncada", true],
  ["pasos.1.resultado.linea_fin", 1000], ["pasos.1.resultado.lineas.0.url", "https://evil.invalid"],
  ["pasos.2.argumentos.categoria", "arbitraria"],
  ["pasos.2.resultado.categoria", "rutas"],
  ["pasos.2.resultado.fragmentos.0.texto", "x".repeat(2001)],
  ["pasos.2.resultado.fragmentos.0.area", "proyecto"],
  ["pasos.2.resultado.fragmentos.0.url", "javascript:alert(1)"],
  ["pasos.2.resultado.fragmentos.0.url", "https://evil.invalid"],
  ["pasos.2.resultado.fragmentos.0.distancia", Infinity],
  ["pasos.2.resultado.fragmentos", Array(3).fill(complete.pasos[2].resultado.fragmentos![0])],
  ["decisiones.0.argumentos.linea", 1], ["decisiones.0.estado", "error"],
  ["decisiones.0.herramienta", "ejecutar_codigo"],
])("rechaza contrato incoherente o fuera de límites: %s = %j", (path, value) => {
  expect(() => parseAgentResponse(alter(path as string, value), input)).toThrow();
});

it("permite repetir herramienta con argumentos distintos y detiene una repetición exacta", () => {
  const copy = structuredClone(complete);
  copy.pasos[2] = { ...copy.pasos[1], numero: 3, argumentos: { linea: 1 }, resultado: { ...copy.pasos[1].resultado, linea_objetivo: 1 } } as typeof copy.pasos[number];
  copy.decisiones[1] = { ...copy.decisiones[0], numero: 2, argumentos: { linea: 1 } } as typeof copy.decisiones[number];
  expect(parseAgentResponse(copy, input).traza_agente?.pasos).toHaveLength(3);
  const repeated = { ...copy, pasos: copy.pasos.slice(0, 2), terminacion: "herramienta_repetida", decisiones: [copy.decisiones[0], { ...copy.decisiones[0], numero: 2, estado: "repetida" }] };
  expect(parseAgentResponse(repeated, input).traza_agente?.terminacion).toBe("herramienta_repetida");
  expect(() => parseAgentResponse(alter("pasos.2.argumentos.linea", 2, copy), input)).toThrow();
});

it("escapa código y documentos sin enlaces activos", () => {
  const copy = alter("pasos.2.resultado.fragmentos.0.texto", "<script>alert(1)</script>");
  const result = parseAgentResponse(copy, input);
  const html = renderToStaticMarkup(<AgentTracePanel trace={result.traza_agente} />);
  expect(html).toContain("&lt;script&gt;");
  expect(html).not.toContain("<script>");
  expect(html).not.toContain("<a ");
});

it("solicita v2 explícitamente sin cambiar el máximo de pasos", async () => {
  const fetcher = vi.fn().mockResolvedValue({ ok: true, json: async () => complete });
  vi.stubGlobal("fetch", fetcher);
  await analyzeWithAgent(input);
  expect(JSON.parse(fetcher.mock.calls[0][1].body)).toMatchObject({ version_herramientas: "2", max_pasos: 3 });
});
