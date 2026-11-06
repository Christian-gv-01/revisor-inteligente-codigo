import { readFileSync } from "node:fs";
import { afterAll, beforeAll, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { analyzeCode, analyzeWithAgent } from "../src/services/api";
import { createReport } from "../src/services/report";
import { FindingsPanel } from "../src/components/FindingsPanel";
import { EvidenceTrace } from "../src/components/EvidenceTrace";
import type { AnalysisInput } from "../src/types/analysis";

const base = process.env.INTEGRATION_API_BASE_URL;
const suite = base ? describe : describe.skip;
const staticEnabled = process.env.INTEGRATION_STATIC_ANALYSIS === "1";
const sql = 'nombre = input("Nombre: ")\ncursor.execute("SELECT * FROM usuarios WHERE nombre = \'" + nombre + "\'")\n';
const input: AnalysisInput = { tipo: "codigo", archivo: "usuarios.py", codigo: sql, url: "", fichero: null };

// Se ejecuta con eval/run_integration.py. No se sustituye fetch ni el parser.
// El servidor debe identificarse como fixture para evitar usar por error una API de IA real.
suite("Integración HTTP: frontend → FastAPI → RAG real → proveedor simulado", () => {
  beforeAll(async () => {
    const response = await fetch(`${base}/health`);
    expect(response.headers.get("X-Integration-Provider")).toBe("stub");
    expect(response.status).toBe(200);
    vi.stubEnv("VITE_API_BASE_URL", base!);
  });
  afterAll(() => vi.unstubAllEnvs());

  it.each(["codigo", "python"] as const)("integra el agente con informe, herramientas y traza en la misma ejecución: %s", async tipo => {
    const result = await analyzeWithAgent({ ...input, tipo, fichero: tipo === "python" ? new File([sql], "usuarios.py") : null });
    expect(result.estado).toBe("analizado");
    expect(result.hallazgos[0].fragmento_codigo).toContain("SELECT");
    expect(result.traza_agente?.modo).toBe("gemini_real");
    expect(result.traza_agente?.decisiones[0].herramienta).toBe("finalizar");
    // El agente ejecuta Ruff/Bandit obligatoriamente, incluso si las rutas
    // directas tienen desactivado el análisis estático opcional.
    expect(result.analisis_estatico?.[0].estado).toBe("completo");
    const html = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
    expect(html).toContain("Proceso de revisión del agente");
    expect(html).toContain("Consulta SQL de la prueba");
    expect(createReport(result).traza_agente).toEqual(result.traza_agente);
  });
  it("procesa JSON real y resuelve los IDs recuperados por ChromaDB", async () => {
    const result = await analyzeCode(input);
    expect(result.demo).toBe(false);
    expect(result.estado).toBe("analizado");
    expect(result.hallazgos[0].referencias).toEqual(["seguridad_python-002"]);
    expect(result.hallazgos[0].fuentes?.[0].id).toBe("seguridad_python-002");
    expect(result.hallazgos[0].fuentes?.[0].distancia).toEqual(expect.any(Number));
  });
  it("muestra en la interfaz y exporta las fuentes devueltas por FastAPI", async () => {
    const result = await analyzeCode(input);
    const panel = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
    const trace = renderToStaticMarkup(<EvidenceTrace result={result} selected={result.hallazgos[0]} loading={false} />);
    expect(panel).toContain("seguridad_python-002");
    expect(panel).toContain("Consultar fuente");
    expect(panel).not.toContain("Referencias ilustrativas de la demostración");
    expect(trace).toContain("usuarios.py:2");
    expect(createReport(result)).toMatchObject({ modo: "backend", estado: "analizado", fuentes: result.fuentes });
  });
  it("envía multipart Python al validador real del backend", async () => {
    const result = await analyzeCode({ ...input, tipo: "python", fichero: new File([sql], "usuarios.py") });
    expect(result.archivos[0]).toEqual({ nombre: "usuarios.py", codigo: sql });
    expect(result.hallazgos[0].fuentes?.[0].id).toBe("seguridad_python-002");
  });
  it("integra ZIP con un archivo analizado y otro abstenido", async () => {
    const bytes = readFileSync(process.env.INTEGRATION_ZIP_PATH!);
    const file = new File([bytes], "proyecto.zip", { type: "application/zip" });
    const result = await analyzeCode({ ...input, tipo: "zip", fichero: file });
    expect(result.archivos.map(item => item.nombre)).toEqual(["usuarios.py", "sin_cita.py"]);
    expect(result.archivos.every(item => item.codigo === null)).toBe(true);
    expect(result.hallazgos).toHaveLength(1);
    expect(result.hallazgos[0].archivo).toBe("usuarios.py");
    expect(result.mensaje).toContain("sin_cita.py");
    expect(createReport(result).mensaje).toContain("sin_cita.py");
  });
  it.each(["INTEGRACION_SIN_CITA", "INTEGRACION_CITA_INVALIDA"])("conserva la abstención generada por la validación real: %s", async marker => {
    const result = await analyzeCode({ ...input, codigo: `# ${marker}\n${sql}` });
    expect(result.estado).toBe("abstenido");
    expect(result.hallazgos).toEqual([]);
    expect(result.mensaje).toBeTruthy();
    const panel = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
    expect(panel).toContain("No hay evidencia suficiente");
    expect(panel).not.toContain("No se encontraron hallazgos");
  });
  it("distingue una respuesta analizada sin hallazgos de una abstención", async () => {
    const result = await analyzeCode({ ...input, codigo: `# INTEGRACION_VACIO\n${sql}` });
    expect(result.estado).toBe("analizado");
    expect(result.hallazgos).toEqual([]);
    expect(result.fuentes?.length).toBeGreaterThan(0);
  });
  it("un timeout conserva el contrato de la configuración estática", async () => {
    const operation = analyzeCode({ ...input, codigo: `# INTEGRACION_ERROR\n${sql}` });
    if (staticEnabled) {
      await expect(operation).resolves.toMatchObject({ estado: "parcial", hallazgos: [] });
    } else {
      await expect(operation).rejects.toMatchObject({ kind: "servidor", message: expect.stringContaining("HTTP 504") });
    }
  });
  it("rechaza un archivo no Python en el endpoint real", async () => {
    const form = new FormData();
    form.append("archivo", new File(["texto"], "invalido.txt"));
    const response = await fetch(`${base}/api/v1/archivos`, { method: "POST", body: form });
    expect([400, 422]).toContain(response.status);
  });

  it("integra GitHub con lector real y API externa controlada", async () => {
    const result = await analyzeCode({ ...input, tipo: "github", url: "https://github.com/qa-fixture/proyecto" });
    expect(result.estado).toBe("analizado");
    expect(result.archivos[0].nombre).toBe("usuarios.py");
    expect(result.hallazgos[0].fuentes?.[0].id).toBe("seguridad_python-002");
    if (staticEnabled) expect(createReport(result).analisis_estatico[0].estado).toBe("completo");
    else expect(result.analisis_estatico).toBeUndefined();
  });

  it.skipIf(!staticEnabled).each(["codigo", "python", "zip", "github"] as const)(
    "muestra y exporta análisis parcial con Ruff/Bandit reales: %s", async tipo => {
      const codigo = "# INTEGRACION_ERROR\neval(user_input)\n";
      const fichero = tipo === "zip"
        ? new File([readFileSync(process.env.INTEGRATION_PARTIAL_ZIP_PATH!)], "parcial.zip")
        : tipo === "python" ? new File([codigo], "usuarios.py") : null;
      const result = await analyzeCode({ ...input, tipo, codigo, fichero, url: "https://github.com/qa-fixture/parcial" });
      expect(result.estado).toBe("parcial");
      expect(result.hallazgos).toEqual([]);
      expect(result.fuentes ?? []).toEqual([]);
      const reports = createReport(result).analisis_estatico;
      expect(reports.map(report => report.archivo)).toEqual(result.archivos.map(file => file.nombre));
      for (const report of reports) {
        expect(report.estado).toBe("completo");
        expect(report.herramientas.map(tool => tool.estado)).toEqual(["ok", "ok"]);
        expect(report.hallazgos.some(finding => finding.regla === "B307")).toBe(true);
      }
      const html = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
      expect(html).toContain("Revisión contextual incompleta");
      expect(html).toContain("B307");
      expect(html).not.toContain("No se encontraron hallazgos");
    },
  );

  it.skipIf(!staticEnabled)("acepta por HTTP 202 alertas combinadas reales sin perderlas en JSON", async () => {
    const result = await analyzeCode({ ...input, codigo: "eval(user_input)\n".repeat(101) });
    expect(createReport(result).analisis_estatico[0].hallazgos).toHaveLength(202);
  });
});

