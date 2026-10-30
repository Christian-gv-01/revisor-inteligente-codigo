import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { EvidenceTrace } from "../src/components/EvidenceTrace";
import { demoResult, SQL_EXAMPLE_CODE } from "../src/services/demo";
import type { AnalysisInput, AnalysisResult, Finding } from "../src/types/analysis";

const input: AnalysisInput = { tipo: "codigo", archivo: "usuarios.py", codigo: SQL_EXAMPLE_CODE, url: "", fichero: null };
const demo = () => demoResult(input, "hallazgos");
const html = (result: AnalysisResult | null, selected: Finding | null = null, loading = false) => renderToStaticMarkup(<EvidenceTrace result={result} selected={selected} loading={loading} />);

describe("Trazabilidad de la revisión", () => {
  it("vincula el ejemplo SQL con la línea 6 y una referencia explícitamente simulada", () => {
    const result = demo();
    expect(result.demo).toBe(true);
    expect(result.hallazgos).toHaveLength(1);
    expect(result.hallazgos[0]).toMatchObject({ linea: 6, referencias: ["seguridad_python-002"] });
    expect(result.fuentes?.[0].distancia).toBeNull();
    const output = html(result);
    expect(output).toContain("usuarios.py:6");
    expect(output).toContain("seguridad_python-002");
    expect(output).toContain("Referencias de ejemplo de la demostración");
  });
  it("cambia la relación cuando se selecciona otro hallazgo", () => {
    const result = demo();
    const other = { ...result.hallazgos[0], id: "otro", archivo: "otro.py", linea: 2, referencias: [], fuentes: [] };
    result.hallazgos.push(other);
    const output = html(result, other);
    expect(output).toContain("otro.py:2");
    expect(output).not.toContain("seguridad_python-002");
    expect(output).toContain("Sin referencia documental recibida");
  });
  it("no conserva relaciones anteriores mientras carga", () => {
    const output = html(demo(), null, true);
    expect(output).toContain("Preparando los hallazgos");
    expect(output).not.toContain("usuarios.py:6");
    expect(output).not.toContain("seguridad_python-002");
  });
  it("distingue abstención de un análisis sin hallazgos", () => {
    const result = { ...demo(), hallazgos: [], fuentes: [], demo: false };
    expect(html({ ...result, estado: "abstenido" })).toContain("se abstuvo");
    expect(html({ ...result, estado: "analizado" })).toContain("no reportó hallazgos");
  });
  it("no atribuye referencias de ejemplo a código que no coincide con las reglas", () => {
    const result = demoResult({ ...input, codigo: 'print("Hola")' }, "hallazgos");
    expect(result.hallazgos).toEqual([]);
    expect(result.fuentes).toEqual([]);
  });
  it("mantiene un estado inicial sin inventar trazabilidad", () => {
    const output = html(null);
    expect(output).toContain("Al analizar tu código");
    expect(output).not.toContain("Fuente citada");
  });
});
