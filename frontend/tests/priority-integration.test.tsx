import { expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import fixture from "./fixtures/prioridad-integrada.json";
import { parseResponse } from "../src/services/api";
import { createReport } from "../src/services/report";
import { StaticFindingsPanel } from "../src/components/StaticFindingsPanel";
import type { AnalysisInput } from "../src/types/analysis";

it("conserva en pantalla y exportación la prioridad calculada por la API", () => {
  const input: AnalysisInput = { tipo: "codigo", archivo: "prioridad.py", codigo: fixture.codigo, url: "", fichero: null };
  const original = structuredClone(fixture.respuesta);
  const result = parseResponse(fixture.respuesta, input);
  const findings = result.analisis_estatico![0].hallazgos;
  const expected = ["B003", "B004", "B005", "B002", "B001", "B006", "F401"];
  expect(findings.map(f => f.regla)).toEqual(expected);
  const html = renderToStaticMarkup(<StaticFindingsPanel informes={result.analisis_estatico} />);
  const positions = expected.map(id => html.indexOf(`· ${id}`));
  expect(positions.every(position => position >= 0)).toBe(true);
  expect(positions).toEqual([...positions].sort((a, b) => a - b));
  const report = createReport(result);
  expect(report.analisis_estatico[0].hallazgos.map(f => f.regla)).toEqual(expected);
  expect(report.analisis_estatico[0].hallazgos.find(f => f.regla === "B001")!.confianza).toBeNull();
  expect(report.analisis_estatico[0].hallazgos.find(f => f.regla === "F401")!.confianza).toBeNull();
  expect(result.estado).toBe("parcial");
  expect(result.hallazgos).toEqual([]);
  expect(fixture.respuesta).toEqual(original);
});
