import type { AgentArguments, AgentStep, AgentTrace } from "../types/analysis";
import "./AgentTracePanel.css";

const labels = {
  inspeccionar_estructura: "Inspección de estructura",
  detectar_llamadas_sensibles: "Revisión de llamadas sensibles",
  revisar_consultas_sql: "Revisión de consultas SQL",
  ampliar_contexto: "Ampliar contexto",
  buscar_referencia: "Buscar referencia",
  finalizar: "Finalizar inspecciones",
};

function Arguments({ args }: { args?: AgentArguments }) {
  if (!args || Object.keys(args).length === 0) return null;
  return <p className="agent-arguments"><strong>Argumentos: </strong>{"linea" in args ? `Línea solicitada: ${args.linea}` : `Categoría: ${args.categoria}`}</p>;
}

function Result({ step }: { step: AgentStep }) {
  if (step.herramienta === "ampliar_contexto") return <div className="agent-context">
    <p>Ventana de código: líneas {step.resultado.linea_inicio}–{step.resultado.linea_fin}.</p>
    <ol aria-label="Líneas de contexto" start={step.resultado.linea_inicio}>{step.resultado.lineas.map(line => <li key={line.numero}>
      <code>{line.texto || " "}</code>{line.truncada && <small>Línea truncada a 500 caracteres</small>}
    </li>)}</ol>
  </div>;
  if (step.herramienta === "buscar_referencia") return <div className="agent-references">
    <p>Referencias recuperadas: {step.resultado.fragmentos.length}. Su recuperación no certifica pertinencia ni confirma un hallazgo.</p>
    {step.resultado.fragmentos.map(fragment => <section key={fragment.id} aria-label={`Fragmento ${fragment.id}`}>
      <strong>{fragment.id}</strong>
      <p>{fragment.documento} · {fragment.seccion} · {fragment.fuente}</p>
      <blockquote>{fragment.texto}</blockquote>
      {fragment.url && <p>Fuente documental: {fragment.url}</p>}
      {fragment.distancia !== null && <small>Distancia de recuperación: {fragment.distancia}</small>}
    </section>)}
  </div>;
  return <div>
    {!step.sintaxis_valida && <p>No se pudo interpretar la sintaxis.</p>}
    {step.herramienta === "inspeccionar_estructura" && step.sintaxis_valida && <dl className="agent-counts">{
      [["total_lineas", "Líneas"], ["funciones", "Funciones"], ["clases", "Clases"], ["importaciones", "Importaciones"]].map(([key, label]) =>
        typeof step.resultado[key] === "number" ? <div key={key}><dt>{label}</dt><dd>{String(step.resultado[key])}</dd></div> : null)
    }</dl>}
    {step.indicadores.length > 0 ? <ul>{step.indicadores.map((item, i) => <li key={i}>Línea {item.linea}: {item.detalle}</li>)}</ul> : step.herramienta !== "inspeccionar_estructura" && <p>Sin indicadores devueltos por esta herramienta.</p>}
  </div>;
}

const states = { ejecutada: "Ejecutada", finalizar: "Finalizar inspecciones", repetida: "Repetida, sin nueva ejecución", error: "No completada" };
const endings = { finalizacion_anticipada: "Finalización anticipada", max_pasos: "Límite de pasos alcanzado", herramienta_repetida: "Herramienta repetida: inspecciones detenidas" };

export function AgentTracePanel({ trace }: { trace?: AgentTrace }) {
  if (!trace) return null;
  return <details className="agent-trace">
    <summary>Proceso de revisión del agente <span>{trace.pasos.length} pasos · {trace.decisiones.length} decisiones</span></summary>
    <p>{trace.modo === "degradado" ? "Revisión incompleta con evidencia conservada." : "Inspecciones del agente y revisión contextual con RAG."} Los indicadores de las herramientas requieren interpretación.</p>
    <ol>{trace.pasos.map(step => <li key={step.numero}>
      <strong>{labels[step.herramienta]}</strong>
      <small>{step.origen === "gemini" ? "Elegido por Gemini" : step.origen === "local" ? "Respaldo local" : "Inspección inicial"}</small>
      <p>{step.motivo}</p>
      <Arguments args={step.argumentos} />
      <Result step={step} />
    </li>)}</ol>
    {trace.decisiones.length > 0 && <div><strong>Decisiones registradas</strong><ul>{trace.decisiones.map(d => <li key={d.numero}>
      {labels[d.herramienta]} · {states[d.estado]}: {d.motivo}<Arguments args={d.argumentos} />
    </li>)}</ul></div>}
    {trace.terminacion && <p role="status"><strong>{endings[trace.terminacion]}.</strong> Se detienen las inspecciones y se conserva la síntesis final con la evidencia reunida; si falla, su estado parcial queda indicado.</p>}
    {trace.fase_error && <p role="status">Fase incompleta: {trace.fase_error === "informe" ? "informe contextual" : trace.fase_error === "herramienta" ? "herramienta contextual" : "planificación"}.</p>}
  </details>;
}
