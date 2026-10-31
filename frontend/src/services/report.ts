import type { AnalysisResult } from "../types/analysis";

export function createReport(result: AnalysisResult) {
  return {
    modo: result.demo ? "demostracion_sin_ia" : "backend",
    fecha: new Date().toISOString(),
    estado: result.estado ?? "analizado",
    mensaje: result.mensaje ?? null,
    archivos: result.archivos.map((file) => file.nombre),
    fuentes: result.fuentes ?? [],
    hallazgos: result.hallazgos,
  };
}
