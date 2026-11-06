import { expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { FindingsPanel } from "../src/components/FindingsPanel";
import { StaticFindingsPanel } from "../src/components/StaticFindingsPanel";
import type { AnalysisResult, Finding, StaticAnalysis } from "../src/types/analysis";

function finding(id: string, severidad: Finding["severidad"]): Finding {
  return { id, titulo: id, severidad, archivo: "caso.py", linea: 1, categoria: "Prueba", explicacion: "Caso controlado", correccion_sugerida: "Revisar", referencias: [] };
}
const data = (): AnalysisResult => ({ archivos: [{ nombre: "caso.py", codigo: "print('ejemplo')" }], hallazgos: [finding("Riesgo menor", "baja"), finding("Riesgo crítico", "critica")], demo: false, estado: "parcial" });
it("muestra parcial incluso con hallazgos y sin mensaje del backend", () => {
  const html = renderToStaticMarkup(<FindingsPanel result={data()} loading={false} onSelect={() => {}} />);
  expect(html).toContain("Análisis parcial: revisión incompleta");
  expect(html).not.toContain("No se encontraron hallazgos");
});
it("prioriza por severidad sin cambiar el resultado que se exporta", () => {
  const result = data(); const original = structuredClone(result);
  const html = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
  expect(html.indexOf("Riesgo crítico")).toBeLessThan(html.indexOf("Riesgo menor"));
  expect(html).toContain("Prioridad de revisión 1");
  expect(result).toEqual(original);
});
it("oculta el estado anterior mientras carga otra revisión", () => {
  const html = renderToStaticMarkup(<FindingsPanel result={data()} loading onSelect={() => {}} />);
  expect(html).not.toContain("Análisis parcial: revisión incompleta");
  expect(html).not.toContain("Riesgo crítico");
});
it("prioriza observaciones estáticas dentro de su panel, sin inventar fuentes RAG", () => {
  const report: StaticAnalysis = { archivo: "caso.py", estado: "completo", mensaje: null, herramientas: [],
    hallazgos: ["baja", "alta"].map((severity, index) => ({ herramienta: "bandit", regla: `B${index}`, tipo: "seguridad", linea: 1, columna: null, severidad: severity as "baja" | "alta", titulo: `Alerta ${severity}`, descripcion: "Indicador", confianza: "media", referencia: null })) };
  const original = structuredClone(report);
  const html = renderToStaticMarkup(<StaticFindingsPanel informes={[report]} />);
  expect(html.indexOf("Alerta alta")).toBeLessThan(html.indexOf("Alerta baja"));
  expect(html).not.toContain("MITRE"); expect(html).not.toContain("OWASP");
  expect(report).toEqual(original);
});
