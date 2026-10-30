
import { useState } from "react";

import type {
  AnalysisResult,
  Finding,
  Severity,
  SourceReference,
} from "../types/analysis";

import {
  SEVERITIES,
  SEVERITY_LABELS,
} from "../types/analysis";

import { Icon } from "./Icon";
import { SourceList } from "./SourceList";

interface FindingsPanelProps {
  result: AnalysisResult | null;
  loading: boolean;
  selectedId?: string;
  onSelect: (finding: Finding) => void;
}

export function FindingsPanel({
  result,
  loading,
  selectedId,
  onSelect,
}: FindingsPanelProps) {
  const [filter, setFilter] = useState<Severity | "todas">("todas");

  const visible =
    result?.hallazgos.filter(
      (finding) =>
        filter === "todas" || finding.severidad === filter,
    ) ?? [];

  // =======================================================
  // FUENTES ASOCIADAS A CADA HALLAZGO
  // =======================================================

  const obtenerFuentes = (
    finding: Finding,
  ): SourceReference[] => {
    if (finding.fuentes) return finding.fuentes;
    if (!result?.fuentes || !finding.referencias) {
      return [];
    }

    const ids = new Set(finding.referencias);

    return result.fuentes.filter((source) =>
      ids.has(source.id),
    );
  };

  return (
    <section
      className="panel results-panel"
      aria-labelledby="results-title"
      aria-busy={loading}
    >
      {/* ================================================= */}
      {/* ENCABEZADO */}
      {/* ================================================= */}

      <div className="panel-heading">
        <div>
          <span className="step-number">02</span>
          <h2 id="results-title">Resultados del análisis</h2>
        </div>

        <span className="count-badge">
          {result?.hallazgos.length ?? "—"}
        </span>
      </div>

      {/* ================================================= */}
      {/* FILTRO DE SEVERIDAD */}
      {/* ================================================= */}

      {result && result.hallazgos.length > 0 && (
        <div className="filter-row">
          <label htmlFor="severity-filter">
            Severidad
          </label>

          <select
            id="severity-filter"
            value={filter}
            onChange={(event) =>
              setFilter(
                event.target.value as Severity | "todas",
              )
            }
          >
            <option value="todas">
              Todas las severidades
            </option>

            {SEVERITIES.map((severity) => (
              <option key={severity} value={severity}>
                {SEVERITY_LABELS[severity]}
              </option>
            ))}
          </select>
        </div>
      )}

      {!loading && result?.estado !== "abstenido" && result?.mensaje && (
        <div className="analysis-notice" role="status">
          <strong>Análisis con observaciones</strong>
          <p>{result.mensaje}</p>
        </div>
      )}
      <div className="findings-content">

        {/* ================================================= */}
        {/* CARGANDO */}
        {/* ================================================= */}

        {loading ? (
          <div className="empty-state">
            <span className="spinner large" />

            <h3>Revisando el código</h3>

            <p>
              Estamos preparando los hallazgos y las
              sugerencias de corrección.
            </p>
          </div>

        /* ================================================= */
        /* SIN RESULTADOS */
        /* ================================================= */

        ) : !result ? (
          <div className="empty-state">
            <div className="empty-icon">
              <Icon name="shield" size={34} />
            </div>

            <h3>Tu próxima revisión empieza aquí</h3>

            <p>
              Introduce código Python y ejecuta un análisis
              para explorar sus posibles riesgos.
            </p>

            <div className="empty-tags">
              <span>Archivo y línea</span>
              <span>Severidad</span>
              <span>Corrección</span>
            </div>
          </div>

        /* ================================================= */
        /* ABSTENCIÓN RAG */
        /* ================================================= */

        ) : result.estado === "abstenido" ? (
          <div className="empty-state">
            <div className="empty-icon">
              <Icon name="info" size={34} />
            </div>

            <h3>No hay evidencia suficiente</h3>

            <p>
              {result.mensaje ||
                "El sistema no encontró información documental suficiente para fundamentar una respuesta."}
            </p>

            <p>
              El sistema se abstuvo de generar hallazgos
              sin respaldo documental.
            </p>
          </div>

        /* ================================================= */
        /* SIN HALLAZGOS */
        /* ================================================= */

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

        /* ================================================= */
        /* FILTRO SIN COINCIDENCIAS */
        /* ================================================= */

        ) : visible.length === 0 ? (
          <div className="empty-state">
            <Icon name="check" />

            <h3>Sin hallazgos de esta severidad</h3>

            <button
              className="text-button"
              onClick={() => setFilter("todas")}
            >
              Ver todos los hallazgos
            </button>
          </div>

        /* ================================================= */
        /* LISTA DE HALLAZGOS */
        /* ================================================= */

        ) : (
          visible.map((finding) => {
            const fuentes = obtenerFuentes(finding);
            const missing = [...new Set(finding.referencias ?? [])].filter(
              (id) => !fuentes.some((source) => source.id === id),
            );

            return (
              <article
                key={finding.id}
                className={`finding ${
                  selectedId === finding.id ? "selected" : ""
                }`}
              >
                <div className="finding-top">
                  <span
                    className={`severity severity-${finding.severidad}`}
                  >
                    {SEVERITY_LABELS[finding.severidad]}
                  </span>

                  <span>{finding.categoria}</span>
                </div>

                <button
                  className="finding-title"
                  onClick={() => onSelect(finding)}
                >
                  {finding.titulo}

                  <Icon name="arrow" size={17} />
                </button>

                <button
                  className="location-link"
                  onClick={() => onSelect(finding)}
                >
                  <Icon name="file" size={13} />

                  {finding.archivo}

                  <span> · Línea {finding.linea}</span>
                </button>

                <p>{finding.explicacion}</p>

                <details>
                  <summary>
                    Ver corrección sugerida
                  </summary>

                  <p className="suggestion">
                    {finding.correccion_sugerida}
                  </p>
                </details>

                {/* FUENTES ESPECÍFICAS DEL HALLAZGO */}

                <div className="finding-sources">
                  <h4>
                    Referencias citadas en este hallazgo
                  </h4>

                  {missing.length > 0 && (
                    <p className="source-warning">Referencias sin metadatos: {missing.join(", ")}. No se puede comprobar su origen.</p>
                  )}
                  {fuentes.length > 0 ? (
                    <SourceList sources={fuentes} />
                  ) : (
                    <p>
                      No se han recibido referencias
                      documentales verificables para este
                      hallazgo.
                    </p>
                  )}
                </div>
              </article>
            );
          })
        )}
      </div>

      {/* ================================================= */}
      {/* FUENTES GENERALES RECUPERADAS */}
      {/* ================================================= */}

      {!loading && result && (result.fuentes?.length ?? 0) > 0 && (
        <section
          className="sources-section"
          aria-labelledby="sources-title"
        >
          <h3 id="sources-title">
            Fuentes de conocimiento consultadas
          </h3>

          <p>
            Documentos recuperados durante el análisis. Su recuperación
            no implica que respalden todos los hallazgos; revisa las citas
            indicadas en cada uno.
          </p>

          <SourceList sources={result.fuentes!} />
        </section>
      )}

      {/* ================================================= */}
      {/* PIE */}
      {/* ================================================= */}

      <div className="panel-footnote">
        <Icon name="info" size={15} />

        <span>
          Selecciona un hallazgo para ubicarlo en el editor.
        </span>
      </div>
    </section>
  );
}
