import type {
  AnalysisInput,
  AnalysisResult,
  Finding,
  Scenario,
} from "../types/analysis";
import { AnalysisError, validateInput } from "./api";
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
    severidad: "alta",
    categoria: "Inyección de comandos",
    titulo: "Ejecución de comandos con shell=True",
    explicacion:
      "Una cadena controlada por el usuario puede interpretarse como instrucciones adicionales del sistema.",
    correccion_sugerida:
      "Pasa los argumentos como una lista y utiliza shell=False. Valida el comando y los argumentos permitidos.",
  },
  {
    pattern: /f["'].*\bSELECT\b/i,
    severidad: "alta",
    categoria: "Inyección SQL",
    titulo: "Consulta SQL construida con interpolación",
    explicacion:
      "Insertar texto del usuario en una consulta puede alterar su estructura y permitir acceso no autorizado a datos.",
    correccion_sugerida:
      'Utiliza parámetros: conexion.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre,)).',
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
            });
      });
  }
  return { archivos, hallazgos, demo: true };
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
