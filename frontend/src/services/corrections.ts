// Contrato propuesto v1. La API permanece deshabilitada hasta acordarlo con Backend.
export interface CorrectionRequest {
  archivo: string;
  codigo_original: string;
  sha256_original: string;
  objetivo: { linea: number; descripcion: string };
}

export interface CorrectionProposal {
  version: "1";
  propuesta_id: string;
  estado: "pendiente_confirmacion";
  accion: "descargar_copia";
  archivo_original: string;
  archivo_salida: string;
  sha256_original: string;
  sha256_propuesto: string;
  codigo_propuesto: string;
  caduca_en: string;
  advertencias: string[];
}

export interface CorrectionClient {
  preview: (request: CorrectionRequest, signal: AbortSignal) => Promise<unknown>;
  decide: (proposal: CorrectionProposal, decision: "aprobar" | "rechazar", signal: AbortSignal) => Promise<unknown>;
}

const MAX_CODE = 12_000;
const safeFilename = (value: unknown): value is string =>
  typeof value === "string" && /^[a-zA-Z0-9_-][a-zA-Z0-9_.-]{0,115}\.py$/.test(value) && !value.includes("..");
const record = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

export async function sha256(text: string): Promise<string> {
  const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(hash), byte => byte.toString(16).padStart(2, "0")).join("");
}

export async function validateProposal(value: unknown, request: CorrectionRequest): Promise<CorrectionProposal> {
  if (!record(value) || value.version !== "1" || value.estado !== "pendiente_confirmacion" ||
      value.accion !== "descargar_copia" || typeof value.propuesta_id !== "string" ||
      !/^[a-zA-Z0-9_-]{6,128}$/.test(value.propuesta_id) ||
      value.archivo_original !== request.archivo || !safeFilename(value.archivo_salida) ||
      value.archivo_salida === request.archivo.split(/[\\/]/).pop() ||
      value.sha256_original !== request.sha256_original ||
      typeof value.codigo_propuesto !== "string" || !value.codigo_propuesto.trim() ||
      value.codigo_propuesto.includes("\0") || value.codigo_propuesto.length > MAX_CODE ||
      value.codigo_propuesto === request.codigo_original ||
      typeof value.caduca_en !== "string" || !Number.isFinite(Date.parse(value.caduca_en)) ||
      Date.parse(value.caduca_en) <= Date.now() ||
      !Array.isArray(value.advertencias) || value.advertencias.length > 10 ||
      !value.advertencias.every(item => typeof item === "string" && item.length <= 500)) {
    throw new Error("No se pudo verificar la propuesta. Solicita una nueva previsualización.");
  }
  if (await sha256(request.codigo_original) !== request.sha256_original ||
      await sha256(value.codigo_propuesto) !== value.sha256_propuesto) {
    throw new Error("La propuesta no coincide con el contenido revisado. No se generó ningún archivo.");
  }
  return value as unknown as CorrectionProposal;
}

export async function validateApprovedCopy(value: unknown, proposal: CorrectionProposal): Promise<{ name: string; code: string }> {
  if (!record(value) || value.version !== "1" || value.propuesta_id !== proposal.propuesta_id ||
      value.estado !== "aprobada" || value.archivo_salida !== proposal.archivo_salida ||
      !safeFilename(value.archivo_salida) || value.contenido !== proposal.codigo_propuesto ||
      value.sha256_contenido !== proposal.sha256_propuesto ||
      value.tipo_contenido !== "text/x-python; charset=utf-8" ||
      await sha256(value.contenido as string) !== proposal.sha256_propuesto) {
    throw new Error("La respuesta no coincide con la copia aprobada. Se canceló la descarga.");
  }
  return { name: value.archivo_salida, code: value.contenido as string };
}

export function validateRejection(value: unknown, proposal: CorrectionProposal): void {
  if (!record(value) || value.version !== "1" || value.propuesta_id !== proposal.propuesta_id || value.estado !== "rechazada") {
    throw new Error("No se pudo verificar el rechazo remoto.");
  }
}

export function downloadCopy(copy: { name: string; code: string }): void {
  const url = URL.createObjectURL(new Blob([copy.code], { type: "text/x-python;charset=utf-8" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = copy.name;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function send(path: string, body: unknown, signal: AbortSignal): Promise<unknown> {
  const base = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
  const response = await fetch(`${base}${path}`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body), signal: AbortSignal.any([signal, AbortSignal.timeout(60_000)]),
  });
  if (!response.ok) {
    if (response.status === 409 || response.status === 410) throw new Error("La propuesta cambió o caducó. Solicita otra previsualización.");
    throw new Error("No se pudo completar la operación. No se descargó ningún archivo.");
  }
  return response.json();
}

// Sin esta habilitación explícita no se contacta con endpoints todavía propuestos.
export function configuredCorrectionClient(): CorrectionClient | undefined {
  if (import.meta.env.VITE_CORRECTIONS_API_ENABLED !== "1") return undefined;
  return {
    preview: (request, signal) => send("/api/v1/correcciones/previsualizar", request, signal),
    decide: (proposal, decision, signal) => send(`/api/v1/correcciones/${encodeURIComponent(proposal.propuesta_id)}/decision`, {
      decision, sha256_original: proposal.sha256_original, sha256_propuesto: proposal.sha256_propuesto,
    }, signal),
  };
}
