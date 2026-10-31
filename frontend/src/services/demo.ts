import type {
  AnalysisInput,
  AnalysisResult,
  Finding,
  Scenario,
  SourceReference,
} from "../types/analysis";
import { AnalysisError, validateInput } from "./api";
export const SQL_EXAMPLE_CODE = `import sqlite3

conexion = sqlite3.connect("usuarios.db")
cursor = conexion.cursor()
nombre = input("Nombre de usuario: ")
consulta = "SELECT * FROM usuarios WHERE nombre = '" + nombre + "'"
cursor.execute(consulta)

print(cursor.fetchall())`;

// Metadatos ilustrativos de las reglas locales. La demo no consulta ChromaDB.
const demoSources: Record<string, SourceReference> = {
  "seguridad_python-001": { id: "seguridad_python-001", documento: "seguridad_python.md", seccion: "Regla 1: Evitar eval con entradas no confiables", fuente: "MITRE CWE-94 · Code Injection", url: "https://cwe.mitre.org/data/definitions/94.html", distancia: null },
  "seguridad_python-002": { id: "seguridad_python-002", documento: "seguridad_python.md", seccion: "Regla 2: Prevenir inyección SQL", fuente: "OWASP · SQL Injection Prevention", url: "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html", distancia: null },
  "seguridad_python-003": { id: "seguridad_python-003", documento: "seguridad_python.md", seccion: "Regla 3: Prevenir inyección de comandos del sistema", fuente: "OWASP · OS Command Injection Defense", url: "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html", distancia: null },
};
export const EXAMPLE_CODE = `import sqlite3
import subprocess


def buscar_usuario(nombre):
    conexion = sqlite3.connect("usuarios.db")
    consulta = f"SELECT * FROM usuarios WHERE nombre = '{nombre}'"
    return conexion.execute(consulta).fetchall()


def ejecutar_tarea(comando):
    return subprocess.run(comando, shell=True)


def calcular_expresion(expresion):
    return eval(expresion)
`;
const rules = [
  {
    pattern: /\beval\s*\(/,
    sourceId: "seguridad_python-001",
    severidad: "critica",
    categoria: "Ejecución de código",
    titulo: "Evaluación de una expresión externa",
    explicacion:
      "Si la expresión proviene de un usuario, eval puede ejecutar instrucciones arbitrarias con los permisos de la aplicación.",
    correccion_sugerida:
      "Evita eval. Para datos literales, utiliza ast.literal_eval y valida los tipos permitidos; para operaciones, define una lista explícita de funciones.",
  },
  {
    pattern: /shell\s*=\s*True/,
    sourceId: "seguridad_python-003",
    severidad: "alta",
    categoria: "Inyección de comandos",
    titulo: "Ejecución de comandos con shell=True",
    explicacion:
      "Una cadena controlada por el usuario puede interpretarse como instrucciones adicionales del sistema.",
    correccion_sugerida:
      "Pasa los argumentos como una lista y utiliza shell=False. Valida el comando y los argumentos permitidos.",
  },
  {
    pattern: /(?:f["'].*\bSELECT\b|\bSELECT\b.*\+\s*\w+)/i,
    sourceId: "seguridad_python-002",
    severidad: "alta",
    categoria: "Inyección SQL",
    titulo: "Entrada de usuario dentro de una consulta",
    explicacion:
      "Insertar texto del usuario en una consulta puede alterar su estructura y permitir acceso no autorizado a datos.",
    correccion_sugerida:
      'conexion.execute(\n    "SELECT * FROM usuarios WHERE nombre = ?",\n    (nombre,)\n)',
  },
] as const;
export function demoResult(
  input: AnalysisInput,
  scenario: Scenario,
): AnalysisResult {
  if (scenario === "servidor")
    throw new AnalysisError(
      "servidor",
      "Error del servidor simulado (HTTP 503). Cambia el escenario para volver a intentar.",
    );
  if (scenario === "conexion")
    throw new AnalysisError(
      "conexion",
      "Error de conexión simulado. Cambia el escenario para volver a intentar.",
    );
  const project = input.tipo === "zip" || input.tipo === "github";
  const archivos = project
    ? [
        { nombre: "demo/usuarios.py", codigo: EXAMPLE_CODE },
        {
          nombre: "demo/saludo.py",
          codigo: 'def saludar(nombre):\n    return f"Hola, {nombre}"\n',
        },
      ]
    : [{ nombre: input.archivo, codigo: input.codigo }];
  const hallazgos: Finding[] = [];
  if (scenario !== "vacio") {
    for (const archivo of archivos)
      archivo.codigo.split("\n").forEach((line, index) => {
        for (const rule of rules)
          if (rule.pattern.test(line))
            hallazgos.push({
              id: `demo-${hallazgos.length}`,
              archivo: archivo.nombre,
              linea: index + 1,
              severidad: rule.severidad,
              categoria: rule.categoria,
              titulo: rule.titulo,
              explicacion: rule.explicacion,
              correccion_sugerida: rule.correccion_sugerida,
              referencias: [rule.sourceId],
              fuentes: [demoSources[rule.sourceId]],
            });
      });
  }
  const ids = new Set(hallazgos.flatMap(finding => finding.referencias ?? []));
  return { archivos, hallazgos, demo: true, estado: "analizado", fuentes: [...ids].map(id => demoSources[id]) };
}
export async function analyzeDemo(
  input: AnalysisInput,
  scenario: Scenario,
  signal: AbortSignal,
): Promise<AnalysisResult> {
  validateInput(input);
  await new Promise<void>((resolve, reject) => {
    signal.throwIfAborted();
    const abort = () => {
      clearTimeout(timer);
      reject(new DOMException("Cancelado", "AbortError"));
    };
    const timer = setTimeout(() => {
      signal.removeEventListener("abort", abort);
      resolve();
    }, 1000);
    signal.addEventListener("abort", abort, { once: true });
  });
  return demoResult(input, scenario);
}
