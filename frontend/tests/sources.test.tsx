import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { parseResponse, parseZipResponse } from "../src/services/api";
import { createReport } from "../src/services/report";
import { FindingsPanel } from "../src/components/FindingsPanel";
import { SourceList } from "../src/components/SourceList";
import { safeSourceUrl } from "../src/services/sources";
import type { AnalysisInput } from "../src/types/analysis";

const input: AnalysisInput = { tipo: "codigo", archivo: "ejemplo.py", codigo: "eval(input())", url: "", fichero: null };
const source = { id: "seguridad_python-001", documento: "seguridad_python.md", seccion: "Regla 1", fuente: "MITRE CWE-94", url: "https://cwe.mitre.org/data/definitions/94.html", distancia: 0.4 };
const finding = { linea: 1, severidad: "alta", categoria: "Código", titulo: "eval externo", explicacion: "Riesgo", correccion_sugerida: "Evitar eval", referencias: [source.id] };
const response = { archivo: input.archivo, estado: "analizado", hallazgos: [finding], fuentes: [source] };
const markup = (value = response) => renderToStaticMarkup(<FindingsPanel result={parseResponse(value, input)} loading={false} onSelect={() => {}} />);

describe("Fuentes y abstención", () => {
  it("muestra título, sección, ID y enlace en elementos separados", () => {
    const html = markup();
    expect(html).toContain('class="source-title">MITRE CWE-94</strong>');
    expect(html).toContain('class="source-section">Regla 1</span>');
    expect(html).toContain('<code>seguridad_python-001</code>');
    expect(html).toContain('rel="noopener noreferrer"');
  });
  it.each(["javascript:alert(1)", "data:text/html,test", "https://user:password@example.com", "https://", "/ruta-local"])("no convierte %s en enlace", (url) => {
    expect(safeSourceUrl(url)).toBeNull();
    expect(renderToStaticMarkup(<SourceList sources={[{ ...source, url }]} />)).not.toContain("href=");
  });
  it("escapa contenido recibido como texto", () => {
    const html = renderToStaticMarkup(<SourceList sources={[{ ...source, fuente: '<img src=x onerror="alert(1)">' }]} />);
    expect(html).not.toContain("<img");
    expect(html).toContain("&lt;img");
  });
  it("no inventa fuentes para identificadores desconocidos", () => {
    const html = markup({ ...response, hallazgos: [{ ...finding, referencias: ["desconocida"] }] });
    expect(html).toContain("Referencias sin metadatos: desconocida");
    expect(html).toContain("No se han recibido referencias");
  });
  it("conserva abstención y mensaje en la vista y el informe", () => {
    const result = parseResponse({ ...response, estado: "abstenido", hallazgos: [], mensaje: "Faltan fuentes" }, input);
    expect(createReport(result)).toMatchObject({ estado: "abstenido", mensaje: "Faltan fuentes" });
    const html = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
    expect(html).toContain("No hay evidencia suficiente");
    expect(html).not.toContain("No se encontraron hallazgos");
  });
  it("rechaza abstención con hallazgos", () => {
    expect(() => parseResponse({ ...response, estado: "abstenido" }, input)).toThrow();
  });
  it("deduplica fuentes idénticas y rechaza metadatos contradictorios", () => {
    expect(parseResponse({ ...response, fuentes: [source, source] }, input).fuentes).toHaveLength(1);
    expect(() => parseResponse({ ...response, fuentes: [source, { ...source, url: "https://example.com" }] }, input)).toThrow();
  });
  it("no atribuye al primer archivo una fuente recibida solo en otro informe ZIP", () => {
    const zipInput = { ...input, fichero: new File(["PK"], "proyecto.zip") };
    const result = parseZipResponse({ archivo_zip: "proyecto.zip", estado: "analizado", total_archivos: 2, informes: [{ ...response, fuentes: [] }, { ...response, archivo: "otro.py" }] }, zipInput);
    expect(result.hallazgos[0].fuentes).toEqual([]);
    expect(result.hallazgos[1].fuentes).toEqual([source]);
  });
  it("informa abstención parcial en ZIP, incluso si el resto no tiene hallazgos", () => {
    const result = parseZipResponse({ archivo_zip: "proyecto.zip", estado: "analizado", total_archivos: 2, informes: [{ ...response, hallazgos: [] }, { ...response, archivo: "otro.py", estado: "abstenido", hallazgos: [], mensaje: "Sin respaldo" }] }, { ...input, fichero: new File(["PK"], "proyecto.zip") });
    const html = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
    expect(html).toContain("Análisis con observaciones");
    expect(html).toContain("otro.py: Sin respaldo");
    expect(createReport(result).mensaje).toContain("otro.py");
  });
  it("oculta fuentes anteriores mientras está cargando", () => {
    const html = renderToStaticMarkup(<FindingsPanel result={parseResponse(response, input)} loading onSelect={() => {}} />);
    expect(html).not.toContain("Fuentes de conocimiento consultadas");
  });
});
