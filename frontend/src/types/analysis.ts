
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
  fragmento_codigo?: string;
  linea_reportada_modelo?: number;

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
  traza_agente?: AgentTrace;

  // Indica si se utilizó el modo demostración.
  demo: boolean;

  // Estado devuelto por el backend.
  estado?: AnalysisStatus;

  // Explicación de la abstención, si corresponde.
  mensaje?: string | null;
}

export type AstAgentTool = "inspeccionar_estructura" | "detectar_llamadas_sensibles" | "revisar_consultas_sql";
export type AgentTool = AstAgentTool | "ampliar_contexto" | "buscar_referencia";
export type ReferenceCategory = "ejecucion_codigo" | "inyeccion_sql" | "inyeccion_comandos" | "inyeccion" | "credenciales" | "rutas" | "deserializacion";
export type AgentArguments = { linea: number } | { categoria: ReferenceCategory } | Record<string, never>;
export interface ContextResult {
  linea_objetivo: number; linea_inicio: number; linea_fin: number;
  lineas: { numero: number; texto: string; truncada: boolean }[];
}
export interface ReferenceResult {
  categoria: ReferenceCategory;
  fragmentos: (SourceReference & { area: "seguridad"; texto: string })[];
}
interface AgentStepBase {
  numero: number; motivo: string; origen: "automatico" | "gemini" | "local";
}
export type AgentStep =
  | (AgentStepBase & { herramienta: AstAgentTool; argumentos?: Record<string, never>; sintaxis_valida: boolean; indicadores: { linea: number; detalle: string }[]; resultado: Record<string, unknown> })
  | (AgentStepBase & { herramienta: "ampliar_contexto"; argumentos: { linea: number }; resultado: ContextResult })
  | (AgentStepBase & { herramienta: "buscar_referencia"; argumentos: { categoria: ReferenceCategory }; resultado: ReferenceResult });
export interface AgentTrace {
  archivo: string;
  modo: "gemini_real" | "degradado";
  max_pasos: number;
  fase_error: "planificacion" | "informe" | "herramienta" | null;
  version_herramientas?: "2";
  terminacion?: "finalizacion_anticipada" | "max_pasos" | "herramienta_repetida";
  pasos: AgentStep[];
  decisiones: {
    numero: number;
    herramienta: AgentTool | "finalizar";
    motivo: string;
    estado: "ejecutada" | "finalizar" | "repetida" | "error";
    argumentos?: AgentArguments;
  }[];
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

// Orden de revisión derivado de la severidad, no una evaluación de impacto nueva.
export const REVIEW_PRIORITY: Record<Severity, number> = {
  critica: 1,
  alta: 2,
  media: 3,
  baja: 4,
};

