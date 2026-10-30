import type { AnalysisResult, Finding } from "../types/analysis";
import { getFindingSources } from "../services/sources";
import { Icon } from "./Icon";

export function EvidenceTrace({ result, selected, loading }: { result: AnalysisResult | null; selected: Finding | null; loading: boolean }) {
  const finding = selected ?? result?.hallazgos[0];
  const sources = result && finding ? getFindingSources(result, finding) : [];
  return (
    <section className="evidence-trace panel" aria-labelledby="evidence-title" aria-busy={loading}>
      <h2 id="evidence-title"><Icon name="link" size={21} />Trazabilidad del análisis</h2>
      {loading ? <p className="trace-description">Preparando los hallazgos y sus referencias…</p> : finding ? (
        <>
          <div className="trace-flow">
            <div className={`trace-finding trace-${finding.severidad}`}><Icon name="alert" size={20} /><strong>Hallazgo</strong><span>{finding.categoria} · {finding.archivo}:{finding.linea}</span></div>
            <Icon name="arrow" size={26} />
            <div className={`trace-source ${sources.length ? "resolved" : "unresolved"}`}><Icon name="file" size={20} /><strong>{sources.length === 1 ? "Fuente citada" : "Fuentes citadas"}</strong><span>{sources.length ? sources.map((source) => source.id).join(" · ") : "Sin referencia documental recibida"}</span></div>
          </div>
          <p className="trace-description">{result?.demo ? "Referencias de ejemplo de la demostración; no corresponden a una recuperación del backend." : sources.length ? "El hallazgo seleccionado conserva sus referencias documentales. Consulta su contenido en el informe." : "La ausencia de referencias impide comprobar el respaldo documental de este hallazgo."}</p>
        </>
      ) : <p className="trace-description">{result?.estado === "abstenido" ? "El sistema se abstuvo de generar hallazgos sin evidencia suficiente." : result ? "El análisis no reportó hallazgos. Las fuentes recuperadas, si existen, se conservan en el informe." : "Al analizar tu código, podrás seguir la relación entre cada hallazgo y sus fuentes."}</p>}
    </section>
  );
}
