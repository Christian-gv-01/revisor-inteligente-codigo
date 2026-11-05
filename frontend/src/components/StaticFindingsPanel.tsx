import type { StaticAnalysis } from "../types/analysis";
import { SEVERITY_LABELS } from "../types/analysis";
import "./StaticFindingsPanel.css";

interface Props {
  informes?: StaticAnalysis[];
}

function enlaceExterno(url: string | null): string | null {
  if (!url) return null;
  try {
    const enlace = new URL(url);
    return enlace.protocol === "https:" || enlace.protocol === "http:"
      ? enlace.href
      : null;
  } catch {
    return null;
  }
}

export function StaticFindingsPanel({ informes }: Props) {
  if (!informes?.length) return null;

  const total = informes.reduce((n, informe) => n + informe.hallazgos.length, 0);
  const incompletos = informes.filter((informe) => informe.estado !== "completo").length;

  return (
    <section className="static-report" aria-label="Revisión estática Ruff y Bandit">
      <header className="static-report-header">
        <div>
          <h3>Revisión estática · Ruff y Bandit</h3>
          <p>
            {total} {total === 1 ? "observación" : "observaciones"} de herramientas,
            independiente de Gemini y de las citas RAG.
          </p>
        </div>
        {incompletos > 0 && (
          <span className="static-report-warning">
            {incompletos} {incompletos === 1 ? "archivo incompleto" : "archivos incompletos"}
          </span>
        )}
      </header>

      <p className="static-report-disclaimer">
        Una advertencia estática es un indicador que debe verificarse;
        no demuestra por sí sola una vulnerabilidad explotable.
      </p>

      {informes.map((informe) => (
        <div className="static-report-file" key={informe.archivo}>
          <h4>{informe.archivo}</h4>
          <div className="static-report-tools">
            {informe.herramientas.map((herramienta) => (
              <span key={herramienta.herramienta} className="static-tool-state">
                <strong>{herramienta.herramienta === "ruff" ? "Ruff" : "Bandit"}</strong>
                <span>{herramienta.estado === "ok"
                  ? `Completado · ${herramienta.hallazgos}`
                  : `No completado (${herramienta.estado})`}</span>
              </span>
            ))}
          </div>

          {informe.mensaje && <p className="static-report-message">{informe.mensaje}</p>}

          {informe.hallazgos.length === 0 ? (
            <p className="static-report-empty">
              {informe.estado === "completo"
                ? "Los analizadores no emitieron observaciones para este archivo. Esto no garantiza que sea seguro."
                : "No hay observaciones disponibles; uno o más analizadores no completaron la revisión."}
            </p>
          ) : informe.hallazgos.map((hallazgo, indice) => {
            const enlace = enlaceExterno(hallazgo.referencia);
            return (
              <article className="static-report-finding" key={`${informe.archivo}-${hallazgo.herramienta}-${hallazgo.regla}-${hallazgo.linea}-${indice}`}>
                <div className="static-report-finding-title">
                  <strong>{hallazgo.herramienta.toUpperCase()} · {hallazgo.regla}</strong>
                  <span className={`severity severity-${hallazgo.severidad}`}>
                    {SEVERITY_LABELS[hallazgo.severidad]}
                  </span>
                </div>
                <p><strong>{hallazgo.titulo}</strong></p>
                <p className="static-report-location">
                  {informe.archivo} · Línea {hallazgo.linea}
                  {hallazgo.columna !== null ? `, columna ${hallazgo.columna}` : ""}
                </p>
                <p>{hallazgo.descripcion}</p>
                <div className="static-report-meta">
                  <span>{hallazgo.tipo === "seguridad" ? "Patrón de seguridad" : "Calidad del código"}</span>
                  {hallazgo.confianza && <span>Confianza: {hallazgo.confianza}</span>}
                  {enlace && (
                    <a href={enlace} target="_blank" rel="noopener noreferrer">
                      Documentación de la herramienta
                    </a>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      ))}
    </section>
  );
}
