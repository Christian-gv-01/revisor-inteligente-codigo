import { AnalysisError, parseZipResponse, validateInput } from "./api";
import { sha256 } from "./corrections";
import type { AnalysisInput, AnalysisResult } from "../types/analysis";

export interface ProjectBudget {
  version: "1"; presupuesto_id: string; estado: "pendiente_confirmacion";
  tipo: "zip" | "github"; origen: string; sha256_entrada: string;
  archivos: { archivo: string; caracteres: number; sha256: string }[];
  total_archivos: number;
  presupuesto: { modelo: string; analisis_previstos: number; intentos_por_analisis: number;
    max_intentos_proveedor: number; plazo_cooperativo_segundos: number };
  sha256_manifiesto: string; caduca_en: string;
}
const record = (v: unknown): v is Record<string, unknown> => typeof v === "object" && v !== null && !Array.isArray(v);
const digest = (v: unknown): v is string => typeof v === "string" && /^[a-f0-9]{64}$/.test(v);
const integer = (v: unknown, min: number, max: number): v is number => Number.isInteger(v) && (v as number) >= min && (v as number) <= max;
const invalid = () => new AnalysisError("contrato", "El presupuesto no coincide con la entrada revisada. Solicita uno nuevo.");
export const projectBudgetEnabled = () => import.meta.env.VITE_PROJECT_BUDGET_ENABLED === "1";

// Las claves del contrato son ASCII; orden compatible con sort_keys=True.
function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (record(value)) return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(",")}}`;
  return JSON.stringify(value);
}
export function budgetCore(p: ProjectBudget) {
  return { tipo: p.tipo, origen: p.origen, sha256_entrada: p.sha256_entrada,
    archivos: p.archivos, total_archivos: p.total_archivos, presupuesto: p.presupuesto };
}
export async function budgetHash(p: ProjectBudget): Promise<string> {
  return sha256(canonical(budgetCore(p)));
}
async function inputHash(input: AnalysisInput): Promise<string> {
  if (input.tipo === "github") return sha256(input.url.trim());
  if (input.tipo !== "zip" || !input.fichero) throw invalid();
  const hash = await crypto.subtle.digest("SHA-256", await input.fichero.arrayBuffer());
  return Array.from(new Uint8Array(hash), b => b.toString(16).padStart(2, "0")).join("");
}
export async function validateBudget(value: unknown, input: AnalysisInput): Promise<ProjectBudget> {
  if (!record(value) || value.version !== "1" || value.estado !== "pendiente_confirmacion" ||
      typeof value.presupuesto_id !== "string" || !/^[A-Za-z0-9_-]{43}$/.test(value.presupuesto_id) ||
      value.tipo !== input.tipo || value.origen !== (input.tipo === "github" ? input.url.trim() : input.fichero?.name) ||
      !digest(value.sha256_entrada) || !digest(value.sha256_manifiesto) ||
      typeof value.caduca_en !== "string" || !Number.isFinite(Date.parse(value.caduca_en)) || Date.parse(value.caduca_en) <= Date.now() ||
      !Array.isArray(value.archivos) || value.archivos.length < 1 || value.archivos.length > 5 ||
      value.total_archivos !== value.archivos.length || !record(value.presupuesto)) throw invalid();
  const p = value.presupuesto;
  if (typeof p.modelo !== "string" || !p.modelo.trim() || p.modelo.length > 200 ||
      p.analisis_previstos !== value.total_archivos || !integer(p.intentos_por_analisis, 1, 3) ||
      !integer(p.max_intentos_proveedor, 1, (value.total_archivos as number) * p.intentos_por_analisis) ||
      !integer(p.plazo_cooperativo_segundos, 1, 150)) throw invalid();
  const names = new Set<string>();
  let total = 0;
  for (const f of value.archivos) {
    if (!record(f) || typeof f.archivo !== "string" || f.archivo.length > 512 ||
        !f.archivo.toLowerCase().endsWith(".py") || f.archivo.startsWith("/") || /[\\\0]/.test(f.archivo) ||
        f.archivo.split("/").includes("..") || names.has(f.archivo) ||
        !integer(f.caracteres, 1, 12000) || !digest(f.sha256)) throw invalid();
    names.add(f.archivo); total += f.caracteres;
  }
  if (total > 12000) throw invalid();
  const proposal = value as unknown as ProjectBudget;
  if (await inputHash(input) !== proposal.sha256_entrada || await budgetHash(proposal) !== proposal.sha256_manifiesto) throw invalid();
  return proposal;
}
async function send(path: string, body: BodyInit, signal: AbortSignal, json = true): Promise<unknown> {
  const base = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
  if (typeof location !== "undefined" && new URL(base || "/", location.origin).origin !== location.origin)
    throw new AnalysisError("conexion", "El presupuesto requiere frontend y API en el mismo origen para conservar la sesión.");
  try {
    const response = await fetch(`${base}/api/v1/proyectos${path}`, { method: "POST", body,
      headers: json ? { "Content-Type": "application/json" } : undefined,
      credentials: "same-origin", signal: AbortSignal.any([signal, AbortSignal.timeout(180000)]) });
    if (!response.ok) {
      if ([404, 409, 410].includes(response.status)) throw new AnalysisError("pendiente", "El presupuesto caducó, cambió o ya está en uso. Revisa el estado antes de iniciar otro análisis.");
      throw new AnalysisError("servidor", `No se pudo completar la solicitud (HTTP ${response.status}).`);
    }
    return await response.json();
  } catch (error) {
    if (signal.aborted || error instanceof AnalysisError) throw error;
    throw new AnalysisError("conexion", "Se interrumpió la respuesta. Si ya aprobaste, el servidor puede continuar dentro del presupuesto autorizado.");
  }
}
export async function previewProject(input: AnalysisInput, signal: AbortSignal): Promise<ProjectBudget> {
  validateInput(input);
  let body: BodyInit;
  if (input.tipo === "zip" && input.fichero) {
    const form = new FormData(); form.append("archivo", input.fichero); body = form;
  } else if (input.tipo === "github") body = JSON.stringify({ url: input.url.trim() });
  else throw invalid();
  const response = await send(`/previsualizar/${input.tipo}`, body, signal, input.tipo !== "zip");
  signal.throwIfAborted();
  return validateBudget(response, input);
}
export async function approveProject(p: ProjectBudget, input: AnalysisInput, signal: AbortSignal): Promise<AnalysisResult> {
  await validateBudget(p, input);
  signal.throwIfAborted();
  const response = await send(`/${p.presupuesto_id}/decision`, JSON.stringify({
    decision: "aprobar", confirmar: true, sha256_manifiesto: p.sha256_manifiesto }), signal);
  signal.throwIfAborted();
  if (!record(response) || response.version !== "1" || response.presupuesto_id !== p.presupuesto_id ||
      response.sha256_manifiesto !== p.sha256_manifiesto || response.estado !== "finalizado" || !record(response.resultado) ||
      !Array.isArray(response.resultado.informes) || response.resultado.informes.length !== p.total_archivos ||
      !response.resultado.informes.every((r: unknown, i: number) => record(r) && r.archivo === p.archivos[i].archivo)) throw invalid();
  return parseZipResponse(response.resultado, { ...input, url: input.url.trim() });
}
export async function rejectProject(p: ProjectBudget, signal: AbortSignal): Promise<void> {
  const response = await send(`/${p.presupuesto_id}/decision`, JSON.stringify({
    decision: "rechazar", confirmar: false, sha256_manifiesto: p.sha256_manifiesto }), signal);
  if (!record(response) || response.version !== "1" || response.presupuesto_id !== p.presupuesto_id || response.estado !== "rechazado") throw invalid();
}
