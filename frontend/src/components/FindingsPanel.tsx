import { useState } from "react";
import type { AnalysisResult, Finding, Severity } from "../types/analysis";
import { SEVERITIES, SEVERITY_LABELS } from "../types/analysis";
import { getFindingSources } from "../services/sources";
import { Icon } from "./Icon";
import { SourceList } from "./SourceList";

interface FindingsPanelProps {
  result: AnalysisResult | null;
  loading: boolean;
  selectedId?: string;
  onSelect: (finding: Finding) => void;
  onExport?: () => void;
}

export function FindingsPanel({ result, loading, selectedId, onSelect, onExport }: FindingsPanelProps) {
  const [filter, setFilter] = useState<Severity | "todas">("todas");
  const visible = result?.hallazgos.filter(finding => filter === "todas" || finding.severidad === filter) ?? [];
  const highest = SEVERITIES.find(severity => result?.hallazgos.some(finding => finding.severidad === severity));
  return (
    <section className="panel results-panel" aria-labelledby="results-title" aria-busy={loading}>
      <div className="panel-heading">
        <div><Icon name="file" size={23} /><h2 id="results-title">Informe de revisión</h2></div>
        {onExport ? <button className="text-button export-button" disabled={loading} onClick={onExport}><Icon name="download" size={18} />Exportar JSON</button> : <span className="count-badge">{result?.hallazgos.length ?? "—"}</span>}
      </div>
      {!loading && result && result.hallazgos.length > 0 && (
        <>
          <div className={`analysis-summary summary-${highest}`}>
            <p><Icon name="info" size={18} /><strong>{result.hallazgos.length} {result.hallazgos.length === 1 ? "hallazgo identificado" : "hallazgos identificados"}</strong></p>
            {highest && <span className={`severity severity-${highest}`}><Icon name="alert" size={14} />Severidad {SEVERITY_LABELS[highest].toLocaleLowerCase("es")}</span>}
          </div>
          <div className="filter-row">
            <label htmlFor="severity-filter">Severidad</label>
            <select id="severity-filter" value={filter} onChange={event => setFilter(event.target.value as Severity | "todas")}>
              <option value="todas">Todas las severidades</option>
              {SEVERITIES.map(severity => <option key={severity} value={severity}>{SEVERITY_LABELS[severity]}</option>)}
            </select>
          </div>
        </>
      )}
      {!loading && result?.estado !== "abstenido" && result?.mensaje && (
        <div className="analysis-notice" role="status"><strong>Análisis con observaciones</strong><p>{result.mensaje}</p></div>
      )}
      <div className="findings-content">
        {loading ? (
          <div className="empty-state"><span className="spinner large" /><h3>Revisando el código</h3><p>Estamos preparando los hallazgos y las sugerencias de corrección.</p></div>
        ) : !result ? (
          <div className="empty-state"><div className="empty-icon"><Icon name="shieldCode" size={42} /></div><span className="empty-eyebrow">REVISIÓN CON EVIDENCIA</span><h3>El informe empieza con tu código</h3><p>Pega un fragmento Python o selecciona un archivo. Aquí podrás explorar los riesgos, las correcciones y sus fuentes.</p><div className="empty-tags"><span>Archivo y línea</span><span>Corrección sugerida</span><span>Fuentes documentales</span></div></div>
        ) : result.estado === "abstenido" ? (
          <div className="empty-state"><div className="empty-icon"><Icon name="info" size={36} /></div><h3>No hay evidencia suficiente</h3><p>{result.mensaje || "El sistema no encontró información documental suficiente para fundamentar una respuesta."}</p><p>El sistema se abstuvo de generar hallazgos sin respaldo documental.</p></div>
        ) : result.hallazgos.length === 0 ? (
          <div className="empty-state"><div className="empty-icon success"><Icon name="check" size={36} /></div><h3>No se encontraron hallazgos</h3><p>{result.demo ? "Resultado de demostración. No equivale a una revisión de seguridad real." : "El análisis no reportó problemas. Esto no garantiza que el código esté libre de vulnerabilidades."}</p></div>
        ) : visible.length === 0 ? (
          <div className="empty-state"><Icon name="check" /><h3>Sin hallazgos de esta severidad</h3><button className="text-button" onClick={() => setFilter("todas")}>Ver todos los hallazgos</button></div>
        ) : visible.map(finding => {
          const sources = getFindingSources(result, finding);
          const missing = [...new Set(finding.referencias ?? [])].filter(id => !sources.some(source => source.id === id));
          const sourceCode = result.archivos.find(file => file.nombre === finding.archivo)?.codigo;
          const line = sourceCode?.split("\n")[finding.linea - 1];
          return (
            <article key={finding.id} className={`finding finding-${finding.severidad} ${selectedId === finding.id ? "selected" : ""}`}>
              <div className="finding-heading"><span className="finding-category">{finding.categoria}</span><span className={`severity severity-${finding.severidad}`}>{SEVERITY_LABELS[finding.severidad]}</span><button className="finding-title" onClick={() => onSelect(finding)}>{finding.titulo}<Icon name="arrow" size={17} /></button><button className="location-link" onClick={() => onSelect(finding)}><Icon name="file" size={14} />{finding.archivo}<span>· Línea {finding.linea}</span></button></div>
              {line !== undefined && <pre className="finding-code-line"><span>{finding.linea}</span><code>{line}</code></pre>}
              <div className="explanation"><h3><Icon name="info" size={18} />Por qué es un riesgo</h3><p>{finding.explicacion}</p></div>
              <details className="correction" open><summary><Icon name="check" size={18} />Ver corrección sugerida</summary><pre className="suggestion"><code>{finding.correccion_sugerida}</code></pre></details>
              <div className="finding-sources"><h4><Icon name="book" size={18} />Respaldo documental</h4>
                {result.demo && <p className="demo-source-note">Referencias ilustrativas de la demostración, no recuperadas por IA.</p>}
                {missing.length > 0 && <p className="source-warning">Referencias sin metadatos: {missing.join(", ")}. No se puede comprobar su origen.</p>}
                {sources.length ? <SourceList sources={sources} /> : <p>No se han recibido referencias documentales verificables para este hallazgo.</p>}
              </div>
            </article>
          );
        })}
      </div>
      {!loading && result && (result.fuentes?.length ?? 0) > 0 && (
        <details className="sources-section"><summary><Icon name="book" size={17} /><span>{result.demo ? "Referencias de la demostración" : "Fuentes de conocimiento consultadas"}</span><span className="count-badge">{result.fuentes!.length}</span></summary><p>{result.demo ? "Documentos de ejemplo para recorrer la interfaz. No se realizó recuperación RAG." : "Documentos recuperados durante el análisis. Su recuperación no implica que respalden todos los hallazgos; revisa las citas indicadas en cada uno."}</p><SourceList sources={result.fuentes!} /></details>
      )}
      <div className="panel-footnote"><Icon name="info" size={14} /><span>Selecciona un hallazgo para ubicarlo en el editor.</span></div>
    </section>
  );
}
