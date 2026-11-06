import type { CorrectionClient, CorrectionProposal, CorrectionRequest } from "./corrections";
import { sha256 } from "./corrections";
import { SQL_EXAMPLE_CODE } from "./demo";

// Ejemplo completo y fijo para probar la interacción; nunca transforma sugerencias libres.
const correctedExample = SQL_EXAMPLE_CODE
  .replace('consulta = "SELECT * FROM usuarios WHERE nombre = \'" + nombre + "\'"', 'consulta = "SELECT * FROM usuarios WHERE nombre = ?"')
  .replace("cursor.execute(consulta)", "cursor.execute(consulta, (nombre,))");

export const demoCorrectionAvailable = (code: string): boolean => code === SQL_EXAMPLE_CODE;

export const demoCorrectionClient: CorrectionClient = {
  async preview(request: CorrectionRequest, signal: AbortSignal) {
    if (signal.aborted) throw new DOMException("Cancelado", "AbortError");
    if (!demoCorrectionAvailable(request.codigo_original)) throw new Error("Esta demostración solo incluye la corrección del ejemplo SQL inicial.");
    const stem = request.archivo.replace(/\.py$/i, "").replace(/[^a-zA-Z0-9_-]/g, "_").slice(0, 70) || "ejemplo";
    return {
      version: "1", propuesta_id: `demo-${crypto.randomUUID()}`,
      estado: "pendiente_confirmacion", accion: "descargar_copia",
      archivo_original: request.archivo, archivo_salida: `${stem}.corregido.py`,
      sha256_original: request.sha256_original,
      sha256_propuesto: await sha256(correctedExample), codigo_propuesto: correctedExample,
      caduca_en: new Date(Date.now() + 5 * 60_000).toISOString(),
      advertencias: ["Ejemplo local ilustrativo. No se consultó Gemini ni se ejecutó el código."],
    };
  },
  async decide(proposal: CorrectionProposal, decision, signal) {
    if (signal.aborted) throw new DOMException("Cancelado", "AbortError");
    if (decision === "rechazar") return { version: "1", propuesta_id: proposal.propuesta_id, estado: "rechazada" };
    return {
      version: "1", propuesta_id: proposal.propuesta_id, estado: "aprobada",
      archivo_salida: proposal.archivo_salida, contenido: proposal.codigo_propuesto,
      sha256_contenido: proposal.sha256_propuesto, tipo_contenido: "text/x-python; charset=utf-8",
    };
  },
};
