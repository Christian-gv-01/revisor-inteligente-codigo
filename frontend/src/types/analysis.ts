
export type Severity = "critica" | "alta" | "media" | "baja";

export type InputKind = "codigo" | "python" | "zip" | "github";

export type Mode = "demo" | "api";

export type Scenario = "hallazgos" | "vacio" | "servidor" | "conexion";

export type AnalysisStatus = "analizado" | "abstenido" | "parcial";

// =========================================================
// HALLAZGOS
// =========================================================

export interface Finding {
  id: string;
  archivo: string;
  linea: number;
  severidad: Severity;
  categoria: string;
  titulo: string;
  explicacion: string;
  correccion_sugerida: string;

  // IDs exactos de los fragmentos RAG
  // que respaldan el hallazgo.
  referencias?: string[];
  // Fuentes resueltas dentro del informe del archivo, antes de combinar un ZIP.
  fuentes?: SourceReference[];
}

// =========================================================
// ARCHIVOS ANALIZADOS
// =========================================================

export interface SourceFile {
  nombre: string;
  codigo: string | null;
}

// =========================================================
// FUENTES DOCUMENTALES RAG
// =========================================================

export interface SourceReference {
  // Identificador exacto del fragmento ChromaDB.
  id: string;

  documento: string;
  seccion: string;
  fuente: string;
  url: string;

  // Distancia semántica de recuperación.
  distancia: number | null;
}

// =========================================================
// INFORME ESTÁTICO INDEPENDIENTE DE LAS CITAS RAG
// =========================================================

export type StaticTool = "ruff" | "bandit";
export type StaticToolStatus = "ok" | "no_disponible" | "timeout" | "error";
export type StaticAnalysisStatus = "completo" | "parcial" | "no_disponible";

export interface StaticFinding {
  herramienta: StaticTool;
  regla: string;
  tipo: "seguridad" | "calidad";
  linea: number;
  columna: number | null;
  severidad: Severity;
  titulo: string;
  descripcion: string;
  confianza: "alta" | "media" | "baja" | null;
  referencia: string | null;
}

export interface StaticToolExecution {
  herramienta: StaticTool;
  estado: StaticToolStatus;
  hallazgos: number;
}

export interface StaticAnalysis {
  archivo: string;
  estado: StaticAnalysisStatus;
  hallazgos: StaticFinding[];
  herramientas: StaticToolExecution[];
  mensaje: string | null;
}

// =========================================================
// RESULTADO DEL ANÁLISIS
// =========================================================

export interface AnalysisResult {
  archivos: SourceFile[];
  hallazgos: Finding[];
  fuentes?: SourceReference[];
  // Uno por archivo; separado de los hallazgos que requieren citas RAG.
  analisis_estatico?: StaticAnalysis[];

  // Indica si se utilizó el modo demostración.
  demo: boolean;

  // Estado devuelto por el backend.
  estado?: AnalysisStatus;

  // Explicación de la abstención, si corresponde.
  mensaje?: string | null;
}

// =========================================================
// DATOS DE ENTRADA
// =========================================================

export interface AnalysisInput {
  tipo: InputKind;
  archivo: string;
  codigo: string;
  url: string;
  fichero: File | null;
}

// =========================================================
// SEVERIDADES
// =========================================================

export const SEVERITIES: Severity[] = [
  "critica",
  "alta",
  "media",
  "baja",
];

export const SEVERITY_LABELS: Record<Severity, string> = {
  critica: "Crítica",
  alta: "Alta",
  media: "Media",
  baja: "Baja",
};
