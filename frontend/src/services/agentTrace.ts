import type { AgentArguments, AgentStep, AgentTool, AgentTrace, AnalysisInput, AstAgentTool, ContextResult, ReferenceCategory, ReferenceResult } from "../types/analysis";

const astTools: AstAgentTool[] = ["inspeccionar_estructura", "detectar_llamadas_sensibles", "revisar_consultas_sql"];
const categories: ReferenceCategory[] = ["ejecucion_codigo", "inyeccion_sql", "inyeccion_comandos", "inyeccion", "credenciales", "rutas"];
const tools: AgentTool[] = [...astTools, "ampliar_contexto", "buscar_referencia"];
function fail(): never { throw new Error("Traza del agente inválida"); }
function record(v: unknown): v is Record<string, unknown> { return typeof v === "object" && v !== null && !Array.isArray(v); }
function object(v: unknown): Record<string, unknown> { return record(v) ? v : fail(); }
function integer(v: unknown, min: number, max: number): v is number { return Number.isInteger(v) && (v as number) >= min && (v as number) <= max; }
function text(v: unknown, min: number, max: number): v is string { return typeof v === "string" && Array.from(v).length >= min && Array.from(v).length <= max; }
function keys(v: Record<string, unknown>, allowed: string[]) { if (Object.keys(v).some(k => !allowed.includes(k))) fail(); }

function argumentsFor(tool: string, value: unknown): AgentArguments {
  const args = object(value === undefined ? {} : value);
  if (tool === "ampliar_contexto") {
    keys(args, ["linea"]);
    if (!integer(args.linea, 1, 12000)) fail();
    return { linea: args.linea };
  }
  if (tool === "buscar_referencia") {
    keys(args, ["categoria"]);
    if (!categories.includes(args.categoria as ReferenceCategory)) fail();
    return { categoria: args.categoria as ReferenceCategory };
  }
  keys(args, []);
  return {};
}
function signature(tool: string, args?: AgentArguments) { return `${tool}:${JSON.stringify(args ?? {})}`; }

function contextResult(value: unknown, target: number, lines: string[]): ContextResult {
  const r = object(value);
  keys(r, ["linea_objetivo", "linea_inicio", "linea_fin", "lineas"]);
  const start = Math.max(1, target - 3), end = Math.min(lines.length, target + 3);
  if (target > lines.length || r.linea_objetivo !== target || r.linea_inicio !== start || r.linea_fin !== end ||
      !Array.isArray(r.lineas) || r.lineas.length !== end - start + 1 || r.lineas.length > 7) fail();
  const window = r.lineas.map((value: unknown, i: number) => {
    const line = object(value), number = start + i;
    keys(line, ["numero", "texto", "truncada"]);
    const literal = Array.from(lines[number - 1]);
    if (line.numero !== number || line.texto !== literal.slice(0, 500).join("") || line.truncada !== (literal.length > 500)) fail();
    return { numero: number, texto: line.texto as string, truncada: line.truncada as boolean };
  });
  return { linea_objetivo: target, linea_inicio: start, linea_fin: end, lineas: window };
}

function safeCorpusUrl(value: string): boolean {
  if (value === "") return true;
  if (Array.from(value).some(c => c.charCodeAt(0) <= 32 || c.charCodeAt(0) === 127 || c === "\\")) return false;
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password && !url.port &&
      ["cwe.mitre.org", "cheatsheetseries.owasp.org", "owasp.org", "www.owasp.org"].includes(url.hostname);
  } catch { return false; }
}

function referenceResult(value: unknown, category: ReferenceCategory): ReferenceResult {
  const r = object(value);
  keys(r, ["categoria", "fragmentos"]);
  if (r.categoria !== category || !Array.isArray(r.fragmentos) || r.fragmentos.length > 2) fail();
  const seen = new Set<string>();
  const fragments = r.fragmentos.map((value: unknown) => {
    const f = object(value);
    keys(f, ["area", "id", "texto", "documento", "seccion", "fuente", "url", "distancia"]);
    if (f.area !== "seguridad" || !text(f.id, 1, 160) || !f.id.trim() || seen.has(f.id) || !text(f.texto, 1, 2000) ||
        !["documento", "seccion", "fuente"].every(k => text(f[k], 0, 300)) || !text(f.url, 0, 2048) || !safeCorpusUrl(f.url) ||
        (f.distancia !== null && (typeof f.distancia !== "number" || !Number.isFinite(f.distancia)))) fail();
    seen.add(f.id);
    return { area: "seguridad" as const, id: f.id, texto: f.texto, documento: f.documento as string,
      seccion: f.seccion as string, fuente: f.fuente as string, url: f.url, distancia: f.distancia as number | null };
  });
  return { categoria: category, fragmentos: fragments };
}

/** Valida la traza de ambas versiones antes de mostrarla o exportarla. */
export function parseAgentTrace(value: unknown, input: AnalysisInput): AgentTrace {
  const v = object(value), v2 = v.version_herramientas === "2";
  if ((v.version_herramientas !== undefined && !v2) || v.archivo !== input.archivo ||
      !["gemini_real", "degradado"].includes(v.modo as string) || !integer(v.max_pasos, 1, 3) ||
      !Array.isArray(v.pasos) || v.pasos.length < 1 || v.pasos.length > v.max_pasos ||
      !Array.isArray(v.decisiones) || v.decisiones.length > Math.min(2, v.max_pasos - 1) ||
      ![null, "planificacion", "informe", ...(v2 ? ["herramienta"] : [])].includes(v.fase_error as string | null) ||
      !record(v.informe) || (v.modo === "degradado" && v.informe.estado !== "parcial") ||
      (v.modo === "gemini_real" && v.fase_error !== null)) fail();
  if (v.terminacion !== undefined && (!v2 || !["finalizacion_anticipada", "max_pasos", "herramienta_repetida"].includes(v.terminacion as string))) fail();
  // Python splitlines también reconoce separadores de control y Unicode.
  // eslint-disable-next-line no-control-regex
  const lines = input.codigo.split(/\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]/);
  if (lines.at(-1) === "") lines.pop();
  const seen = new Set<string>();
  const steps: AgentStep[] = v.pasos.map((value: unknown, index: number): AgentStep => {
    const s = object(value), tool = s.herramienta as AgentTool;
    if (s.numero !== index + 1 || !(v2 ? tools : astTools).includes(tool as AstAgentTool) ||
        !text(s.motivo, 1, 500) || !["automatico", "gemini", "local"].includes(s.origen as string) ||
        (index === 0 && tool !== "inspeccionar_estructura")) fail();
    const args = argumentsFor(tool, s.argumentos), key = signature(tool, args);
    if (seen.has(key)) fail();
    seen.add(key);
    const common = { numero: index + 1, motivo: s.motivo, origen: s.origen as AgentStep["origen"] };
    if (tool === "ampliar_contexto") {
      if (s.origen !== "gemini" || !("linea" in args)) fail();
      const linea = args.linea as number;
      return { ...common, herramienta: tool, argumentos: { linea }, resultado: contextResult(s.resultado, linea, lines) };
    }
    if (tool === "buscar_referencia") {
      if (s.origen !== "gemini" || !("categoria" in args)) fail();
      const categoria = args.categoria as ReferenceCategory;
      return { ...common, herramienta: tool, argumentos: { categoria }, resultado: referenceResult(s.resultado, categoria) };
    }
    const r = object(s.resultado);
    if (typeof r.sintaxis_valida !== "boolean") fail();
    const indicators = r.indicadores ?? [];
    if (!Array.isArray(indicators) || indicators.length > 20) fail();
    const parsed = indicators.map((value: unknown) => {
      const item = object(value), detail = item.llamada ?? item.patron;
      if (!integer(item.linea, 1, lines.length) || !text(detail, 1, 160)) fail();
      return { linea: item.linea, detalle: detail };
    });
    return { ...common, herramienta: tool, ...(s.argumentos !== undefined ? { argumentos: {} } : {}),
      sintaxis_valida: r.sintaxis_valida, indicadores: parsed, resultado: r };
  });
  const executed = steps.filter(s => s.origen === "gemini");
  const decisionCount = v.decisiones.length;
  let cursor = 0;
  const visited = new Set([signature(steps[0].herramienta, steps[0].argumentos)]);
  const decisions: AgentTrace["decisiones"] = v.decisiones.map((value: unknown, index: number) => {
    const d = object(value), tool = d.herramienta as AgentTool | "finalizar", state = d.estado as AgentTrace["decisiones"][number]["estado"];
    if (d.numero !== index + 1 || ![...(v2 ? tools : astTools), "finalizar"].includes(tool) || !text(d.motivo, 1, 240) ||
        !["ejecutada", "finalizar", "repetida", ...(v2 ? ["error"] : [])].includes(state)) fail();
    const args = argumentsFor(tool, d.argumentos), key = signature(tool, args);
    if (state === "ejecutada") {
      const step = executed[cursor++];
      if (tool === "finalizar" || !step || key !== signature(step.herramienta, step.argumentos) || step.motivo !== d.motivo || visited.has(key)) fail();
      visited.add(key);
    } else {
      if (index !== decisionCount - 1) fail();
      if (state === "finalizar" && tool !== "finalizar") fail();
      if (state === "repetida" && (!visited.has(key) || tool === "finalizar")) fail();
      if (state === "error" && (v.modo !== "degradado" || v.fase_error !== "herramienta" || tool === "finalizar")) fail();
    }
    return { numero: index + 1, herramienta: tool, motivo: d.motivo, estado: state,
      ...(d.argumentos !== undefined ? { argumentos: args } : {}) };
  });
  if (cursor !== executed.length) fail();
  const last = decisions.at(-1);
  if ((v.terminacion === "finalizacion_anticipada" && last?.estado !== "finalizar") ||
      (v.terminacion === "herramienta_repetida" && last?.estado !== "repetida") ||
      (v.terminacion === "max_pasos" && (steps.length !== v.max_pasos || (last && last.estado !== "ejecutada"))) ||
      (v2 && v.modo === "gemini_real" && !v.terminacion) ||
      (v2 && last?.estado === "finalizar" && v.terminacion !== "finalizacion_anticipada") ||
      (v2 && last?.estado === "repetida" && v.terminacion !== "herramienta_repetida")) fail();
  return { archivo: input.archivo, modo: v.modo as AgentTrace["modo"], max_pasos: v.max_pasos,
    fase_error: v.fase_error as AgentTrace["fase_error"], pasos: steps, decisiones: decisions,
    ...(v2 ? { version_herramientas: "2" } : {}),
    ...(v.terminacion ? { terminacion: v.terminacion as AgentTrace["terminacion"] } : {}) };
}
