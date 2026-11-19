// Se conserva el objetivo individual v1 para integraciones existentes.
export type CorrectionRequest = {
  archivo: string;
  codigo_original: string;
  sha256_original: string;
} & (
  { objetivo: { linea: number; descripcion: string }; objetivos?: never; lineas_excluidas?: number[] } |
  { objetivo?: never; objetivos: { linea: number; descripcion: string }[]; lineas_excluidas?: number[] }
);

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
    body: JSON.stringify(body), signal: AbortSignal.any([signal, AbortSignal.timeout(35_000)]),
  });
  if (!response.ok) {
    // No mostrar el JSON de validación crudo: podría contener el código enviado.
    const payload = [422, 502].includes(response.status)
      ? await response.json().catch(() => null) : null;
    const detail = record(payload) && typeof payload.detail === "string" ? payload.detail : "";
    if (response.status === 422) {
      if (detail.startsWith("No existe una corrección concreta") || detail.startsWith("La propuesta no introduce")) {
        const cantidad = "objetivos" in body && Array.isArray(body.objetivos) ? body.objetivos.length : 1;
        throw new Error(`No se obtuvo un parche local válido para ${cantidad} hallazgo(s) seleccionado(s). Algunas correcciones necesitan cambiar más líneas de las autorizadas. Prueba seleccionarlos de uno en uno o revísalos manualmente; el original permanece intacto.`);
      }
      if (record(payload) && Array.isArray(payload.detail)) {
        const fields = payload.detail.map(item =>
          record(item) && Array.isArray(item.loc) ? String(item.loc[item.loc.length - 1]) : "")
          .filter(value => ["archivo", "codigo_original", "sha256_original", "objetivos", "objetivo",
            "linea", "descripcion", "lineas_excluidas"].includes(value));
        const field = fields[0];
        throw new Error(field
          ? `La solicitud no cumple la validación del servidor (campo ${field}). Comprueba archivo y hallazgos antes de reintentar.`
          : "La solicitud no cumple el contrato de correcciones. Vuelve a analizar el archivo antes de reintentar.");
      }
      throw new Error("No se pudo generar una corrección válida (422). No se modificó el archivo original.");
    }
    if (response.status === 409 || response.status === 410) throw new Error("La propuesta cambió o caducó. Solicita otra previsualización.");
    if (response.status === 413) throw new Error("El archivo excede el límite de la corrección selectiva. Selecciona uno más pequeño.");
    if (response.status === 429) throw new Error("Se alcanzó el límite temporal de propuestas. Reintenta más tarde.");
    if (response.status === 502 && detail.startsWith("La propuesta modifica zonas no seleccionadas.")) {
      throw new Error("Gemini intentó modificar código no seleccionado. La propuesta se bloqueó para proteger tu archivo.");
    }
    if (response.status === 503 || response.status === 504) {
      throw new Error("Gemini no respondió dentro del plazo o no está disponible. No se generó ningún archivo.");
    }
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
