import { useState } from "react";
import type { AnalysisResult, Finding, Severity } from "../types/analysis";
import { SEVERITIES, SEVERITY_LABELS } from "../types/analysis";
import { Icon } from "./Icon";
export function FindingsPanel({
  result,
  loading,
  selectedId,
  onSelect,
}: {
  result: AnalysisResult | null;
  loading: boolean;
  selectedId?: string;
  onSelect: (finding: Finding) => void;
}) {
  const [filter, setFilter] = useState<Severity | "todas">("todas");
  const visible =
    result?.hallazgos.filter(
      (f) => filter === "todas" || f.severidad === filter,
    ) ?? [];
  return (
    <section
      className="panel results-panel"
      aria-labelledby="results-title"
      aria-busy={loading}
    >
      <div className="panel-heading">
        <div>
          <span className="step-number">02</span>
          <h2 id="results-title">Resultados del análisis</h2>
        </div>
        <span className="count-badge">{result?.hallazgos.length ?? "—"}</span>
      </div>
      {result && result.hallazgos.length > 0 && (
        <div className="filter-row">
          <label htmlFor="severity-filter">Severidad</label>
          <select
            id="severity-filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value as Severity | "todas")}
          >
            <option value="todas">Todas las severidades</option>
            {SEVERITIES.map((s) => (
              <option key={s} value={s}>
                {SEVERITY_LABELS[s]}
              </option>
            ))}
          </select>
        </div>
      )}
      <div className="findings-content">
        {loading ? (
          <div className="empty-state">
            <span className="spinner large" />
            <h3>Revisando el código</h3>
            <p>
              Estamos preparando los hallazgos y las sugerencias de corrección.
            </p>
          </div>
        ) : !result ? (
          <div className="empty-state">
            <div className="empty-icon">
              <Icon name="shield" size={34} />
            </div>
            <h3>Tu próxima revisión empieza aquí</h3>
            <p>
              Introduce código Python y ejecuta un análisis para explorar sus
              posibles riesgos.
            </p>
            <div className="empty-tags">
              <span>Archivo y línea</span>
              <span>Severidad</span>
              <span>Corrección</span>
            </div>
          </div>
        ) : result.hallazgos.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon success">
              <Icon name="check" size={34} />
            </div>
            <h3>No se encontraron hallazgos</h3>
            <p>
              {result.demo
                ? "Resultado de demostración. No equivale a una revisión de seguridad real."
                : "El análisis no reportó problemas. Esto no garantiza que el código esté libre de vulnerabilidades."}
            </p>
          </div>
        ) : visible.length === 0 ? (
          <div className="empty-state">
            <Icon name="check" />
            <h3>Sin hallazgos de esta severidad</h3>
            <button className="text-button" onClick={() => setFilter("todas")}>
              Ver todos los hallazgos
            </button>
          </div>
        ) : (
          visible.map((f) => (
            <article
              key={f.id}
              className={`finding ${selectedId === f.id ? "selected" : ""}`}
            >
              <div className="finding-top">
                <span className={`severity severity-${f.severidad}`}>
                  {SEVERITY_LABELS[f.severidad]}
                </span>
                <span>{f.categoria}</span>
              </div>
              <button className="finding-title" onClick={() => onSelect(f)}>
                {f.titulo}
                <Icon name="arrow" size={17} />
              </button>
              <button className="location-link" onClick={() => onSelect(f)}>
                <Icon name="file" size={13} />
                {f.archivo} <span>· Línea {f.linea}</span>
              </button>
              <p>{f.explicacion}</p>
              <details>
                <summary>Ver corrección sugerida</summary>
                <p className="suggestion">{f.correccion_sugerida}</p>
              </details>
            </article>
          ))
        )}
      </div>
      <div className="panel-footnote">
        <Icon name="info" size={15} />
        <span>Selecciona un hallazgo para ubicarlo en el editor.</span>
      </div>
    </section>
  );
}
