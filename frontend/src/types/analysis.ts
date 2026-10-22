export type Severity = "critica" | "alta" | "media" | "baja";
export type InputKind = "codigo" | "python" | "zip" | "github";
export type Mode = "demo" | "api";
export type Scenario = "hallazgos" | "vacio" | "servidor" | "conexion";
export interface Finding {
  id: string;
  archivo: string;
  linea: number;
  severidad: Severity;
  categoria: string;
  titulo: string;
  explicacion: string;
  correccion_sugerida: string;
}
export interface SourceFile {
  nombre: string;
  codigo: string | null;
}
export interface AnalysisResult {
  archivos: SourceFile[];
  hallazgos: Finding[];
  demo: boolean;
}
export interface AnalysisInput {
  tipo: InputKind;
  archivo: string;
  codigo: string;
  url: string;
  fichero: File | null;
}
export const SEVERITIES: Severity[] = ["critica", "alta", "media", "baja"];
export const SEVERITY_LABELS: Record<Severity, string> = {
  critica: "Crítica",
  alta: "Alta",
  media: "Media",
  baja: "Baja",
};
