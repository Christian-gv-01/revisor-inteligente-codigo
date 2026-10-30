
import type {
  AnalysisInput,
  AnalysisResult,
  AnalysisStatus,
  Finding,
  Severity,
  SourceReference,
} from "../types/analysis";

import { SEVERITIES } from "../types/analysis";

// =========================================================
// ERRORES
// =========================================================

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

// =========================================================
// LIMITES
// =========================================================

export const MAX_CODE_LENGTH = 12_000;
export const MAX_PY_BYTES = 48_000;
export const MAX_ZIP_BYTES = 5 * 1024 * 1024;

// =========================================================
// VALIDACIONES
// =========================================================

export function validateGithub(value: string): boolean {
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

export function validateFile(
  file: File,
  kind: "python" | "zip",
): void {
  const extension = kind === "python" ? ".py" : ".zip";

  if (!file.name.toLowerCase().endsWith(extension)) {
    throw new AnalysisError(
      "entrada",
      `Selecciona un archivo ${extension}.`,
    );
  }

  if (!file.size) {
    throw new AnalysisError(
      "entrada",
      "El archivo está vacío.",
    );
  }

  if (file.size > (kind === "python" ? MAX_PY_BYTES : MAX_ZIP_BYTES)) {
    throw new AnalysisError(
      "entrada",
      kind === "python"
        ? "El archivo Python supera 48 KB. Usa un fragmento de hasta 12.000 caracteres."
        : "El ZIP supera el límite de 5 MB del backend.",
    );
  }
}

export function validateInput(input: AnalysisInput): void {
  if (input.tipo === "github") {
    if (!validateGithub(input.url)) {
      throw new AnalysisError(
        "entrada",
        "Introduce una URL como https://github.com/usuario/repositorio, sin rutas adicionales.",
      );
    }

    return;
  }

  if (input.tipo === "zip") {
    if (!input.fichero) {
      throw new AnalysisError(
        "entrada",
        "Selecciona un archivo .zip.",
      );
    }

    validateFile(input.fichero, "zip");
    return;
  }

  if (input.tipo === "python" && !input.fichero) {
    throw new AnalysisError(
      "entrada",
      "Selecciona un archivo .py.",
    );
  }

  if (
    !input.archivo.trim() ||
    input.archivo.length > 255 ||
    !input.archivo.toLowerCase().endsWith(".py")
  ) {
    throw new AnalysisError(
      "entrada",
      "El nombre debe terminar en .py y tener hasta 255 caracteres.",
    );
  }

  if (!input.codigo.trim()) {
    throw new AnalysisError(
      "entrada",
      "Pega o escribe código Python antes de analizar.",
    );
  }

  if (Array.from(input.codigo).length > MAX_CODE_LENGTH) {
    throw new AnalysisError(
      "entrada",
      "El backend admite hasta 12.000 caracteres por análisis.",
    );
  }

  if (input.codigo.includes("\0")) {
    throw new AnalysisError(
      "entrada",
      "El contenido parece binario. Usa un archivo Python de texto.",
    );
  }
}

// =========================================================
// UTILIDADES DE VALIDACIÓN
// =========================================================

function record(
  value: unknown,
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function isAnalysisStatus(
  value: unknown,
): value is AnalysisStatus {
  return value === "analizado" || value === "abstenido";
}

function invalidResponse(message: string): AnalysisError {
  return new AnalysisError("contrato", message);
}

// =========================================================
// VALIDACIÓN DE FUENTES RAG
// =========================================================

function parseSources(value: unknown): SourceReference[] {
  if (value === undefined || value === null) {
    return [];
  }

  if (!Array.isArray(value)) {
    throw invalidResponse(
      "El servidor devolvió un formato incorrecto para las fuentes RAG.",
    );
  }

  const sources = value.map((entry: unknown) => {
    if (
      !record(entry) ||
      typeof entry.id !== "string" ||
      !entry.id.trim() ||
      !["documento", "seccion", "fuente", "url"].every(
        (key) => typeof entry[key] === "string",
      ) ||
      (
        entry.distancia !== null &&
        entry.distancia !== undefined &&
        (
          typeof entry.distancia !== "number" ||
          !Number.isFinite(entry.distancia)
        )
      )
    ) {
      throw invalidResponse(
        "Una fuente RAG no contiene los metadatos esperados.",
      );
    }

    return {
      id: entry.id,
      documento: entry.documento as string,
      seccion: entry.seccion as string,
      fuente: entry.fuente as string,
      url: entry.url as string,
      distancia:
        typeof entry.distancia === "number"
          ? entry.distancia
          : null,
    };
  });

  const unique = new Map<string, SourceReference>();

  for (const source of sources) {
    const previous = unique.get(source.id);

    if (
      previous &&
      ["documento", "seccion", "fuente", "url"].some(
        (key) =>
          previous[key as keyof SourceReference] !==
          source[key as keyof SourceReference],
      )
    ) {
      throw invalidResponse(
        "Un identificador RAG corresponde a fuentes diferentes.",
      );
    }

    if (!previous) {
      unique.set(source.id, source);
    }
  }

  return Array.from(unique.values());
}

// =========================================================
// VALIDACIÓN DE HALLAZGOS
// =========================================================

function parseFindings(
  value: unknown,
  archivo: string,
): Finding[] {
  if (!Array.isArray(value)) {
    throw invalidResponse(
      "El servidor no devolvió una lista válida de hallazgos.",
    );
  }

  return value.map((entry: unknown, index: number) => {
    if (
      !record(entry) ||
      !Number.isInteger(entry.linea) ||
      (entry.linea as number) < 1 ||
      !SEVERITIES.includes(entry.severidad as Severity) ||
      ![
        "categoria",
        "titulo",
        "explicacion",
        "correccion_sugerida",
      ].every((key) => typeof entry[key] === "string")
    ) {
      throw invalidResponse(
        "Uno de los hallazgos tiene un formato incorrecto.",
      );
    }

    let referencias: string[] | undefined;

    if (entry.referencias !== undefined) {
      if (
        !Array.isArray(entry.referencias) ||
        !entry.referencias.every(
          (referencia: unknown) =>
            typeof referencia === "string" &&
            referencia.trim().length > 0,
        )
      ) {
        throw invalidResponse(
          "Un hallazgo contiene referencias RAG inválidas.",
        );
      }

      referencias = entry.referencias;
    }

    return {
      id:
        typeof entry.id === "string" && entry.id.trim()
          ? entry.id
          : `api-${index}`,
      archivo,
      linea: entry.linea as number,
      severidad: entry.severidad as Severity,
      categoria: entry.categoria as string,
      titulo: entry.titulo as string,
      explicacion: entry.explicacion as string,
      correccion_sugerida: entry.correccion_sugerida as string,
      ...(referencias !== undefined ? { referencias } : {}),
    };
  });
}

// =========================================================
// PROCESAMIENTO DE RESPUESTAS DEL BACKEND
// =========================================================

export function parseResponse(
  value: unknown,
  input: AnalysisInput,
): AnalysisResult {
  const invalid = () =>
    invalidResponse(
      "El servidor devolvió un formato inesperado. Revisa el contrato de la API.",
    );

  if (
    !record(value) ||
    !isAnalysisStatus(value.estado) ||
    value.archivo !== input.archivo ||
    !Array.isArray(value.hallazgos)
  ) {
    throw invalid();
  }

  const estado = value.estado;

  const hallazgos = parseFindings(
    value.hallazgos,
    input.archivo,
  );

  const fuentes = parseSources(value.fuentes);

  if (
    estado === "abstenido" &&
    hallazgos.length > 0
  ) {
    throw invalid();
  }

  if (
    value.mensaje !== undefined &&
    value.mensaje !== null &&
    typeof value.mensaje !== "string"
  ) {
    throw invalid();
  }

  return {
    archivos: [
      {
        nombre: input.archivo,
        codigo: input.codigo,
      },
    ],
    hallazgos: hallazgos.map((finding) => ({
      ...finding,
      fuentes: fuentes.filter((source) =>
        finding.referencias?.includes(source.id),
      ),
    })),
    ...(fuentes.length > 0 ? { fuentes } : {}),
    demo: false,
    estado,
    mensaje:
      typeof value.mensaje === "string"
        ? value.mensaje
        : null,
  };
}

// =========================================================
// PROCESAMIENTO DE RESPUESTAS ZIP Y GITHUB
// =========================================================

export function parseZipResponse(
  value: unknown,
  input: AnalysisInput,
): AnalysisResult {
  const invalid = () =>
    invalidResponse(
      "El informe del proyecto no coincide con el contrato esperado.",
    );

  if (
    !record(value) ||
    !isAnalysisStatus(value.estado) ||
    (input.tipo === "github"
      ? value.repositorio !== input.url
      : value.archivo_zip !== input.fichero?.name) ||
    !Array.isArray(value.informes) ||
    value.informes.length < 1 ||
    value.informes.length > 5 ||
    value.total_archivos !== value.informes.length
  ) {
    throw invalid();
  }

  const result: AnalysisResult = {
    archivos: [],
    hallazgos: [],
    demo: false,
    estado: "analizado",
    mensaje: null,
  };

  const fuentesUnicas = new Map<string, SourceReference>();
  const archivosVistos = new Set<string>();

  let archivosAbstenidos = 0;
  const mensajes: string[] = [];

  value.informes.forEach((report: unknown, index: number) => {
    if (
      !record(report) ||
      typeof report.archivo !== "string" ||
      !report.archivo.trim() ||
      archivosVistos.has(report.archivo)
    ) {
      throw invalid();
    }

    archivosVistos.add(report.archivo);

    const parsed = parseResponse(report, {
      ...input,
      archivo: report.archivo,
      codigo: "",
    });

    result.archivos.push({
      nombre: report.archivo,
      codigo: null,
    });

    if (parsed.estado === "abstenido") {
      archivosAbstenidos++;

      if (parsed.mensaje) {
        mensajes.push(
          `${report.archivo}: ${parsed.mensaje}`,
        );
      }
    }

    for (const fuente of parsed.fuentes ?? []) {
      fuentesUnicas.set(fuente.id, fuente);
    }

    result.hallazgos.push(
      ...parsed.hallazgos.map((finding) => ({
        ...finding,
        id: `${input.tipo === "github" ? "github" : "zip"}-${index}-${finding.id}`,
      })),
    );
  });

  if (fuentesUnicas.size > 0) {
    result.fuentes = Array.from(fuentesUnicas.values());
  }

  if (archivosAbstenidos === value.informes.length) {
    result.estado = "abstenido";

    result.mensaje =
      mensajes.join("\n") ||
      "No se encontraron fuentes suficientes para fundamentar los análisis del proyecto.";
  } else if (archivosAbstenidos > 0) {
    result.mensaje =
      mensajes.length > 0
        ? mensajes.join("\n")
        : "Algunos archivos no pudieron analizarse por falta de fuentes suficientes.";
  }

  return result;
}

// =========================================================
// COMUNICACIÓN CON EL BACKEND
// =========================================================

export async function analyzeCode(
  input: AnalysisInput,
  signal?: AbortSignal,
): Promise<AnalysisResult> {
  validateInput(input);

  const base = (
    import.meta.env.VITE_API_BASE_URL || ""
  ).replace(/\/$/, "");

  const timeout = AbortSignal.timeout(
    input.tipo === "zip" || input.tipo === "github"
      ? 180_000
      : 60_000,
  );

  const combined = signal
    ? AbortSignal.any([signal, timeout])
    : timeout;

  try {
    const upload =
      input.tipo === "python" ||
      input.tipo === "zip";

    const path =
      input.tipo === "github"
        ? "/api/v1/repositorios/github"
        : input.tipo === "zip"
          ? "/api/v1/archivos/zip"
          : input.tipo === "python"
            ? "/api/v1/archivos"
            : "/api/v1/analizar";

    const body = upload
      ? new FormData()
      : JSON.stringify(
          input.tipo === "github"
            ? { url: input.url }
            : {
                archivo: input.archivo,
                codigo: input.codigo,
              },
        );

    if (body instanceof FormData) {
      body.append(
        "archivo",
        input.tipo === "zip"
          ? input.fichero!
          : new File(
              [input.codigo],
              input.archivo,
              { type: "text/x-python" },
            ),
      );
    }

    const response = await fetch(
      `${base}${path}`,
      {
        method: "POST",
        ...(upload
          ? {}
          : {
              headers: {
                "Content-Type": "application/json",
              },
            }),
        body,
        signal: combined,
      },
    );

    if (!response.ok) {
      if (
        [400, 413, 422].includes(response.status) ||
        (input.tipo === "github" && response.status === 404)
      ) {
        throw new AnalysisError(
          "entrada",
          `El servidor rechazó la entrada (HTTP ${response.status}). Revisa el tamaño y el contenido.`,
        );
      }

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

    return input.tipo === "zip" || input.tipo === "github"
      ? parseZipResponse(data, input)
      : parseResponse(data, input);

  } catch (error) {
    if (signal?.aborted) {
      throw error;
    }

    if (error instanceof AnalysisError) {
      throw error;
    }

    if (timeout.aborted) {
      throw new AnalysisError(
        "conexion",
        `El análisis superó ${
          input.tipo === "zip" || input.tipo === "github"
            ? "180"
            : "60"
        } segundos. Comprueba el backend e inténtalo de nuevo.`,
      );
    }

    throw new AnalysisError(
      "conexion",
      "No se pudo conectar con el backend. Comprueba que esté iniciado y revisa la dirección de la API.",
    );
  }
}
