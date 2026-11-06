import { afterEach, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { ProjectBudgetReview } from "../src/components/ProjectBudgetReview";
import { approveProject, budgetHash, previewProject, rejectProject, validateBudget } from "../src/services/projectBudget";
import type { ProjectBudget } from "../src/services/projectBudget";
import { sha256 } from "../src/services/corrections";
import type { AnalysisInput } from "../src/types/analysis";

const input: AnalysisInput = { tipo: "github", url: "https://github.com/grupo/caso", archivo: "", codigo: "", fichero: null };
const signal = () => new AbortController().signal;
afterEach(() => vi.unstubAllGlobals());
async function proposal(): Promise<ProjectBudget> {
  const p: ProjectBudget = { version: "1", presupuesto_id: "a".repeat(43), estado: "pendiente_confirmacion",
    tipo: "github", origen: input.url, sha256_entrada: await sha256(input.url),
    archivos: [{ archivo: "uno.py", caracteres: 9, sha256: await sha256("print(1)\n") }],
    total_archivos: 1, presupuesto: { modelo: "fixture", analisis_previstos: 1, intentos_por_analisis: 2,
      max_intentos_proveedor: 2, plazo_cooperativo_segundos: 150 },
    sha256_manifiesto: "", caduca_en: new Date(Date.now() + 300000).toISOString() };
  p.sha256_manifiesto = await budgetHash(p);
  return p;
}
it("valida el manifiesto y vincula la entrada", async () => {
  const p = await proposal();
  expect(await validateBudget(p, input)).toEqual(p);
  await expect(validateBudget(p, { ...input, url: input.url + "-otro" })).rejects.toThrow("presupuesto");
});
it("rechaza alteraciones de presupuesto, archivos y contenido", async () => {
  const p = await proposal();
  await expect(validateBudget({ ...p, presupuesto: { ...p.presupuesto, max_intentos_proveedor: 1 } }, input)).rejects.toThrow();
  await expect(validateBudget({ ...p, archivos: [{ ...p.archivos[0], archivo: "../uno.py" }] }, input)).rejects.toThrow();
  await expect(validateBudget({ ...p, archivos: [{ ...p.archivos[0], sha256: "0".repeat(64) }] }, input)).rejects.toThrow();
});
it("impide aprobar un presupuesto caducado antes de enviar HTTP", async () => {
  const p = await proposal(); p.caduca_en = "2000-01-01T00:00:00Z";
  const fetch = vi.fn(); vi.stubGlobal("fetch", fetch);
  await expect(approveProject(p, input, signal())).rejects.toThrow();
  expect(fetch).not.toHaveBeenCalled();
});
it("previsualizar solo pide una propuesta, nunca envía aprobación", async () => {
  const p = await proposal();
  const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify(p)));
  vi.stubGlobal("fetch", fetch);
  expect(await previewProject(input, signal())).toEqual(p);
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch.mock.calls[0][0]).toContain("/previsualizar/github");
  expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({ url: input.url });
});
it("aprobar envía consentimiento explícito y normaliza el informe real", async () => {
  const p = await proposal();
  const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify({ version: "1", presupuesto_id: p.presupuesto_id,
    sha256_manifiesto: p.sha256_manifiesto, estado: "finalizado", resultado: { repositorio: input.url, estado: "analizado",
      total_archivos: 1, informes: [{ archivo: "uno.py", estado: "analizado", hallazgos: [], fuentes: [], mensaje: null }] } })));
  vi.stubGlobal("fetch", fetch);
  const result = await approveProject(p, input, signal());
  expect(result.archivos[0].nombre).toBe("uno.py");
  expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({ decision: "aprobar", confirmar: true, sha256_manifiesto: p.sha256_manifiesto });
});
it("no acepta el resultado de otra autorización", async () => {
  const p = await proposal();
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ version: "1", presupuesto_id: "ajeno", estado: "finalizado" }))));
  await expect(approveProject(p, input, signal())).rejects.toThrow("presupuesto");
});
it("rechazar envía confirmar=false", async () => {
  const p = await proposal();
  const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify({ version: "1", presupuesto_id: p.presupuesto_id, estado: "rechazado" })));
  vi.stubGlobal("fetch", fetch);
  await rejectProject(p, signal());
  expect(JSON.parse(fetch.mock.calls[0][1].body).confirmar).toBe(false);
});
it("muestra límite y aprobación bloqueada inicialmente", async () => {
  const html = renderToStaticMarkup(<ProjectBudgetReview proposal={await proposal()} disabled={false} onApprove={() => {}} onReject={() => {}} />);
  expect(html).toContain("máximo 2 intentos");
  expect(html).toMatch(/disabled="">Aprobar presupuesto/);
  expect(html).not.toContain('checked=""');
  expect(html).toContain("no es una cotización monetaria");
  expect(html).toContain("no revoca las llamadas iniciadas");
});
it("una señal ya abortada no permite enviar aprobación", async () => {
  const p = await proposal(); const controller = new AbortController(); controller.abort();
  const fetch = vi.fn(); vi.stubGlobal("fetch", fetch);
  await expect(approveProject(p, input, controller.signal)).rejects.toThrow();
  expect(fetch).not.toHaveBeenCalled();
});
