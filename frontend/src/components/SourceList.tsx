import type { SourceReference } from "../types/analysis";
import { safeSourceUrl } from "../services/sources";

export function SourceList({ sources }: { sources: SourceReference[] }) {
  return (
    <ul className="sources-list">
      {sources.map((source) => {
        const title = source.fuente || source.documento || "Fuente documental";
        const url = safeSourceUrl(source.url);
        return (
          <li className="source-card" key={source.id}>
            <strong className="source-title">{title}</strong>
            {source.seccion && <span className="source-section">{source.seccion}</span>}
            <span className="source-id">Referencia: <code>{source.id}</code></span>
            {url ? (
              <a className="source-link" href={url} target="_blank" rel="noopener noreferrer"
                aria-label={`Consultar ${title}: ${source.seccion || source.id} (abre otra pestaña)`}>
                Consultar fuente <span aria-hidden="true">↗</span>
              </a>
            ) : <span className="source-unavailable">Enlace no disponible</span>}
          </li>
        );
      })}
    </ul>
  );
}
