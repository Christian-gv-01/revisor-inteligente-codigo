import type {
  AnalysisInput,
  AnalysisResult,
  Finding,
  Severity,
} from "../types/analysis";
import { SEVERITIES } from "../types/analysis";
export type ErrorKind =
  | "entrada"
  | "servidor"
  | "conexion"
  | "contrato"
  | "pendiente";
export class AnalysisError extends Error {
  kind: ErrorKind;
  constructor(kind: ErrorKind, message: string) {
    super(message);
    this.name = "AnalysisError";
    this.kind = kind;
  }
}
export const MAX_CODE_LENGTH = 12_000;
export const MAX_PY_BYTES = 48_000;
export const MAX_ZIP_BYTES = 5 * 1024 * 1024;
export function validateGithub(value: string) {
  try {
    const url = new URL(value.trim());
    return (
      url.protocol === "https:" &&
      url.hostname === "github.com" &&
      !url.username &&
      !url.password &&
      !url.port &&
      !url.search &&
      !url.hash &&
      /^\/[\w.-]+\/[\w.-]+\/?$/.test(url.pathname)
    );
  } catch {
    return false;
  }
}
export function validateFile(file: File, kind: "python" | "zip") {
  const extension = kind === "python" ? ".py" : ".zip";
  if (!file.name.toLowerCase().endsWith(extension))
    throw new AnalysisError("entrada", `Selecciona un archivo ${extension}.`);
  if (!file.size) throw new AnalysisError("entrada", "El archivo está vacío.");
  if (file.size > (kind === "python" ? MAX_PY_BYTES : MAX_ZIP_BYTES))
    throw new AnalysisError(
      "entrada",
      kind === "python"
        ? "El archivo Python supera 48 KB. Usa un fragmento de hasta 12.000 caracteres."
        : "El ZIP supera el límite de 5 MB del backend.",
    );
}
export function validateInput(input: AnalysisInput) {
  if (input.tipo === "github") {
    if (!validateGithub(input.url))
      throw new AnalysisError(
        "entrada",
        "Introduce una URL como https://github.com/usuario/repositorio, sin rutas adicionales.",
      );
    return;
  }
  if (input.tipo === "zip") {
    if (!input.fichero)
      throw new AnalysisError("entrada", "Selecciona un archivo .zip.");
    validateFile(input.fichero, "zip");
    return;
  }
  if (input.tipo === "python" && !input.fichero)
    throw new AnalysisError("entrada", "Selecciona un archivo .py.");
  if (
    !input.archivo.trim() ||
    input.archivo.length > 255 ||
    !input.archivo.toLowerCase().endsWith(".py")
  )
    throw new AnalysisError(
      "entrada",
      "El nombre debe terminar en .py y tener hasta 255 caracteres.",
    );
  if (!input.codigo.trim())
    throw new AnalysisError(
      "entrada",
      "Pega o escribe código Python antes de analizar.",
    );
  if (Array.from(input.codigo).length > MAX_CODE_LENGTH)
    throw new AnalysisError(
      "entrada",
      "El backend admite hasta 12.000 caracteres por análisis.",
    );
  if (input.codigo.includes("\0"))
    throw new AnalysisError(
      "entrada",
      "El contenido parece binario. Usa un archivo Python de texto.",
    );
}
function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
export function parseResponse(
  value: unknown,
  input: AnalysisInput,
): AnalysisResult {
  const invalid = () =>
    new AnalysisError(
      "contrato",
      "El servidor devolvió un formato inesperado. Revisa el contrato de la API.",
    );
  if (
    !record(value) ||
    value.estado !== "analizado" ||
    value.archivo !== input.archivo ||
    !Array.isArray(value.hallazgos)
  )
    throw invalid();
  const hallazgos: Finding[] = value.hallazgos.map(
    (entry: unknown, index: number) => {
      if (
        !record(entry) ||
        !Number.isInteger(entry.linea) ||
        (entry.linea as number) < 1 ||
        !SEVERITIES.includes(entry.severidad as Severity) ||
        !["categoria", "titulo", "explicacion", "correccion_sugerida"].every(
          (key) => typeof entry[key] === "string",
        )
      )
        throw invalid();
      return {
        id: `api-${index}`,
        archivo: input.archivo,
        linea: entry.linea as number,
        severidad: entry.severidad as Severity,
        categoria: entry.categoria as string,
        titulo: entry.titulo as string,
        explicacion: entry.explicacion as string,
        correccion_sugerida: entry.correccion_sugerida as string,
      };
    },
  );
  return {
    archivos: [{ nombre: input.archivo, codigo: input.codigo }],
    hallazgos,
    demo: false,
  };
}
export function parseZipResponse(
  value: unknown,
  input: AnalysisInput,
): AnalysisResult {
  const invalid = () =>
    new AnalysisError(
      "contrato",
      "El informe ZIP del servidor no coincide con el contrato esperado.",
    );
  if (
    !record(value) ||
    value.estado !== "analizado" ||
    value.archivo_zip !== input.fichero?.name ||
    !Array.isArray(value.informes) ||
    value.informes.length < 1 ||
    value.informes.length > 5 ||
    value.total_archivos !== value.informes.length
  )
    throw invalid();
  const result: AnalysisResult = { archivos: [], hallazgos: [], demo: false };
  const seen = new Set<string>();
  value.informes.forEach((report: unknown, index: number) => {
    if (
      !record(report) ||
      typeof report.archivo !== "string" ||
      !report.archivo ||
      seen.has(report.archivo)
    )
      throw invalid();
    seen.add(report.archivo);
    const parsed = parseResponse(report, {
      ...input,
      archivo: report.archivo,
      codigo: "",
    });
    // La API actual no devuelve el contenido del ZIP. No inventamos código fuente.
    result.archivos.push({ nombre: report.archivo, codigo: null });
    result.hallazgos.push(
      ...parsed.hallazgos.map((f) => ({ ...f, id: `zip-${index}-${f.id}` })),
    );
  });
  return result;
}
export async function analyzeCode(
  input: AnalysisInput,
  signal?: AbortSignal,
): Promise<AnalysisResult> {
  validateInput(input);
  if (input.tipo === "github")
    throw new AnalysisError(
      "pendiente",
      "El backend aún no ofrece descarga de repositorios. Utiliza Código, Archivo .py o Proyecto .zip.",
    );
  const base = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
  const timeout = AbortSignal.timeout(input.tipo === "zip" ? 180_000 : 60_000);
  const combined = signal ? AbortSignal.any([signal, timeout]) : timeout;
  try {
    const upload = input.tipo === "python" || input.tipo === "zip";
    const path =
      input.tipo === "zip"
        ? "/api/v1/archivos/zip"
        : input.tipo === "python"
          ? "/api/v1/archivos"
          : "/api/v1/analizar";
    const body = upload
      ? new FormData()
      : JSON.stringify({ archivo: input.archivo, codigo: input.codigo });
    if (body instanceof FormData) {
      // Para Python enviamos la versión visible en el editor, incluidas las ediciones.
      body.append(
        "archivo",
        input.tipo === "zip"
          ? input.fichero!
          : new File([input.codigo], input.archivo, { type: "text/x-python" }),
      );
    }
    const response = await fetch(`${base}${path}`, {
      method: "POST",
      ...(upload ? {} : { headers: { "Content-Type": "application/json" } }),
      body,
      signal: combined,
    });
    if (!response.ok) {
      if ([400, 413, 422].includes(response.status))
        throw new AnalysisError(
          "entrada",
          `El servidor rechazó la entrada (HTTP ${response.status}). Revisa el tamaño y el contenido.`,
        );
      throw new AnalysisError(
        "servidor",
        `El servidor no pudo completar el análisis (HTTP ${response.status}). Inténtalo de nuevo.`,
      );
    }
    let data: unknown;
    try {
      data = await response.json();
    } catch {
      throw new AnalysisError(
        "contrato",
        "La respuesta del servidor no contiene JSON válido.",
      );
    }
    return input.tipo === "zip"
      ? parseZipResponse(data, input)
      : parseResponse(data, input);
  } catch (error) {
    if (signal?.aborted) throw error;
    if (error instanceof AnalysisError) throw error;
    if (timeout.aborted)
      throw new AnalysisError(
        "conexion",
        `El análisis superó ${input.tipo === "zip" ? "180" : "60"} segundos. Comprueba el backend e inténtalo de nuevo.`,
      );
    throw new AnalysisError(
      "conexion",
      "No se pudo conectar con el backend. Comprueba que esté iniciado y revisa la dirección de la API.",
    );
  }
}
