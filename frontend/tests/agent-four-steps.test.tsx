import { expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { parseAgentResponse } from "../src/services/api";
import { AgentTracePanel } from "../src/components/AgentTracePanel";
import type { AnalysisInput } from "../src/types/analysis";
import complete from "../../docs/contrato-agente-v2/04-respuesta-contexto-y-referencia.json";

const lines = Array.from({ length: 20 }, (_, i) => `dato_${i + 1} = ${i + 1}`);
const input: AnalysisInput = { tipo: "codigo", archivo: complete.archivo,
  codigo: lines.join("\n"), fichero: null, url: "" };

function fourSteps() {
  const original = structuredClone(complete);
  const steps = [original.pasos[0], ...[8, 9, 10].map((target, i) => ({
    numero: i + 2, herramienta: "ampliar_contexto", origen: "gemini", motivo: `Ubicación ${target}`,
    argumentos: { linea: target }, resultado: { linea_objetivo: target, linea_inicio: target - 6,
      linea_fin: target + 6, lineas: lines.slice(target - 7, target + 6).map((texto, n) => ({
        numero: target - 6 + n, texto, truncada: false })) },
  }))];
  return { ...original, informe: { ...original.informe, hallazgos: [], fuentes: [] },
    max_pasos: 4, pasos: steps, decisiones: steps.slice(1).map((s, i) => ({
    numero: i + 1, herramienta: s.herramienta, estado: "ejecutada", motivo: s.motivo, argumentos: s.argumentos,
  })) };
}

it("muestra el cuarto paso y conserva ventanas literales de trece líneas", () => {
  const r = parseAgentResponse(fourSteps(), input);
  expect(r.traza_agente?.pasos).toHaveLength(4);
  const html = renderToStaticMarkup(<AgentTracePanel trace={r.traza_agente} />);
  expect(html).toContain("dato_16 = 16");
  expect(html).toContain("Línea solicitada: 10");
});

it("rechaza texto inventado en el cuarto paso y un quinto paso", () => {
  const bad = fourSteps();
  const result = bad.pasos[3].resultado as { lineas: { texto: string }[] };
  result.lineas[0].texto = "dato_inventado = 0";
  expect(() => parseAgentResponse(bad, input)).toThrow();
  expect(() => parseAgentResponse({ ...fourSteps(), max_pasos: 5 }, input)).toThrow();
});
