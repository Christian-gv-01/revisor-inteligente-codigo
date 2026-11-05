import type { AgentTrace } from "../types/analysis";
import "./AgentTracePanel.css";

const labels = {
  inspeccionar_estructura: "Inspección de estructura",
  detectar_llamadas_sensibles: "Revisión de llamadas sensibles",
  revisar_consultas_sql: "Revisión de consultas SQL",
  finalizar: "Finalizar inspecciones",
};

export function AgentTracePanel({ trace }: { trace?: AgentTrace }) {
  if (!trace) return null;
  return <details className="agent-trace">
    <summary>Proceso de revisión del agente <span>{trace.pasos.length} pasos · {trace.decisiones.length} decisiones</span></summary>
    <p>{trace.modo === "degradado" ? "Revisión incompleta con evidencia conservada." : "Inspecciones del agente y revisión contextual con RAG."} Los indicadores de las herramientas requieren interpretación.</p>
    <ol>{trace.pasos.map(step => <li key={step.numero}>
      <strong>{labels[step.herramienta]}</strong>
      <small>{step.origen === "gemini" ? "Elegido por Gemini" : step.origen === "local" ? "Respaldo local" : "Inspección inicial"}</small>
      <p>{step.motivo}</p>
      {!step.sintaxis_valida && <p>No se pudo interpretar la sintaxis.</p>}
      {step.indicadores.length > 0 && <ul>{step.indicadores.map((item, i) => <li key={i}>Línea {item.linea}: {item.detalle}</li>)}</ul>}
    </li>)}</ol>
    {trace.decisiones.length > 0 && <div><strong>Decisiones registradas</strong><ul>{trace.decisiones.map(d => <li key={d.numero}>{labels[d.herramienta]} · {d.estado}: {d.motivo}</li>)}</ul></div>}
    {trace.fase_error && <p role="status">Fase incompleta: {trace.fase_error === "informe" ? "informe contextual" : "planificación"}.</p>}
  </details>;
}
