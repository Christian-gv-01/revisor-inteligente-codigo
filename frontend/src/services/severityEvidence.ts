import type { Finding, Severity, SeverityInheritance } from "../types/analysis";
import { SEVERITIES } from "../types/analysis";

function fail(): never { throw new Error("Herencia de severidad inválida"); }
function object(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function id(value: unknown): value is string { return typeof value === "string" && /^estatica-[0-9a-f]{64}$/.test(value); }

/** Conserva la auditoría declarada por la API; no certifica la semántica de una regla. */
export function parseSeverityEvidence(entry: Record<string, unknown>): Pick<Finding, "reglas_evidencia" | "severidad_original_modelo" | "herencia_severidad"> {
  const ids = entry.reglas_evidencia ?? [], rows = entry.herencia_severidad ?? [];
  if (!Array.isArray(ids) || ids.length > 40 || !ids.every(id) || new Set(ids).size !== ids.length ||
      !Array.isArray(rows) || rows.length > 40) fail();
  if (!ids.length && !rows.length && entry.severidad_original_modelo == null) return {};
  if (!ids.length || ids.length !== rows.length || !SEVERITIES.includes(entry.severidad_original_modelo as Severity)) fail();
  const seen = new Set<string>();
  const trace: SeverityInheritance[] = rows.map(value => {
    if (!object(value) || !id(value.id) || !ids.includes(value.id) || seen.has(value.id) ||
        !["ruff", "bandit"].includes(value.herramienta as string) || typeof value.regla !== "string" ||
        !value.regla.trim() || value.regla.length > 40 || value.linea !== entry.linea ||
        (value.columna !== null && (!Number.isInteger(value.columna) || (value.columna as number) < 1)) ||
        !SEVERITIES.includes(value.severidad_original as Severity) || !SEVERITIES.includes(value.severidad_derivada as Severity) ||
        ![null, "alta", "media", "baja"].includes(value.confianza as string | null)) fail();
    seen.add(value.id);
    return { id: value.id, herramienta: value.herramienta as "ruff" | "bandit", regla: value.regla,
      linea: value.linea as number, columna: value.columna as number | null,
      severidad_original: value.severidad_original as Severity, confianza: value.confianza as SeverityInheritance["confianza"],
      severidad_derivada: value.severidad_derivada as Severity };
  });
  const original = entry.severidad_original_modelo as Severity;
  const expected = [original, ...trace.map(r => r.severidad_derivada)].sort((a, b) => SEVERITIES.indexOf(a) - SEVERITIES.indexOf(b))[0];
  if (entry.severidad !== expected) fail();
  return { reglas_evidencia: ids, severidad_original_modelo: original, herencia_severidad: trace };
}
