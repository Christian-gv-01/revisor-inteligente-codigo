import { expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { parseAgentResponse } from "../src/services/api";
import { FindingsPanel } from "../src/components/FindingsPanel";
import { createReport } from "../src/services/report";
import type { AnalysisInput } from "../src/types/analysis";
import fixture from "./fixtures/herencia-integrada.json";

const input: AnalysisInput = { ...fixture.entrada, tipo: "codigo", fichero: null, url: "" };

it("conserva la severidad del modelo, reglas e identidad al mostrar y exportar", () => {
  const result = parseAgentResponse(fixture.respuesta, input);
  const finding = result.hallazgos[0];
  expect(finding.severidad).toBe("critica");
  expect(finding.severidad_original_modelo).toBe("baja");
  expect(finding.herencia_severidad).toEqual(fixture.respuesta.informe.hallazgos[0].herencia_severidad);
  expect(createReport(result).hallazgos[0]).toEqual(finding);
  const html = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
  for (const text of ["Severidad calculada por política", "B602", "confianza", "baja", "critica"]) expect(html).toContain(text);
});

it.each([
  ["severidad_original_modelo", "inventada"], ["severidad", "media"],
  ["reglas_evidencia", []], ["reglas_evidencia", ["id-fabricado"]],
  ["herencia_severidad", []], ["herencia_severidad.0.id", "id-fabricado"],
  ["herencia_severidad.0.linea", 1], ["herencia_severidad.0.confianza", "0.99"],
  ["herencia_severidad.0.columna", -1], ["herencia_severidad.0.severidad_derivada", "inventada"],
])("rechaza auditoría incoherente: %s", (path, value) => {
  const copy = structuredClone(fixture.respuesta) as unknown as Record<string, unknown>;
  let entry = (copy.informe as { hallazgos: Record<string, unknown>[] }).hallazgos[0];
  const parts = path.split(".");
  for (const part of parts.slice(0, -1)) entry = entry[part] as Record<string, unknown>;
  entry[parts.at(-1)!] = value;
  expect(() => parseAgentResponse(copy, input)).toThrow();
});
