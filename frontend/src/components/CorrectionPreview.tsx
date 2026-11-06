import { useEffect, useRef, useState } from "react";
import type { Finding } from "../types/analysis";
import type { CorrectionClient, CorrectionProposal } from "../services/corrections";
import { downloadCopy, sha256, validateApprovedCopy, validateProposal, validateRejection } from "../services/corrections";
import "./CorrectionPreview.css";

interface Props {
  archivo: string;
  codigo: string;
  finding: Finding;
  demo: boolean;
  partial?: boolean;
  client?: CorrectionClient;
}

export function CorrectionPreview({ archivo, codigo, finding, demo, partial, client }: Props) {
  const [proposal, setProposal] = useState<CorrectionProposal | null>(null);
  const [consent, setConsent] = useState(false);
  const [phase, setPhase] = useState<"idle" | "previewing" | "review" | "approving" | "done">("idle");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const pending = useRef<AbortController | null>(null);
  // El padre desmonta esta revisión al editar el código, cambiar archivo o hallazgo.
  useEffect(() => () => pending.current?.abort(), []);

  async function preview() {
    if (!client || phase === "previewing" || phase === "approving") return;
    pending.current?.abort();
    const controller = new AbortController();
    pending.current = controller;
    setConsent(false); setProposal(null); setMessage(""); setError(""); setPhase("previewing");
    try {
      const request = { archivo, codigo_original: codigo, sha256_original: await sha256(codigo),
        objetivo: { linea: finding.linea, descripcion: finding.correccion_sugerida } };
      if (controller.signal.aborted) return;
      const candidate = await validateProposal(await client.preview(request, controller.signal), request);
      if (controller.signal.aborted) return;
      setProposal(candidate); setPhase("review");
    } catch (cause) {
      if (controller.signal.aborted) return;
      setError(cause instanceof Error ? cause.message : "No se pudo preparar la propuesta.");
      setPhase("idle");
    }
  }

  async function approve() {
    if (!client || !proposal || !consent || phase !== "review") return;
    if (Date.parse(proposal.caduca_en) <= Date.now()) {
      setError("La propuesta caducó. Solicita otra previsualización.");
      setConsent(false); setProposal(null); setPhase("idle"); return;
    }
    pending.current?.abort();
    const controller = new AbortController();
    pending.current = controller;
    setPhase("approving"); setError("");
    try {
      const copy = await validateApprovedCopy(await client.decide(proposal, "aprobar", controller.signal), proposal);
      if (controller.signal.aborted) return;
      downloadCopy(copy);
      setConsent(false); setProposal(null); setPhase("done");
      setMessage(`Descarga solicitada: ${copy.name}. El original permanece intacto; revisa la copia antes de utilizarla.`);
    } catch (cause) {
      if (controller.signal.aborted) return;
      setConsent(false); setPhase("review");
      setError(cause instanceof Error ? cause.message : "No se pudo obtener la copia aprobada.");
    }
  }

  function cancel() {
    pending.current?.abort();
    const previous = proposal;
    const controller = new AbortController();
    pending.current = controller;
    setConsent(false); setProposal(null); setPhase("idle"); setError("");
    setMessage("Corrección cancelada. No se descargó ningún archivo y el original permanece intacto.");
    if (client && previous) {
      void client.decide(previous, "rechazar", controller.signal).then(response => validateRejection(response, previous)).catch(() => {
        if (!controller.signal.aborted) setMessage("Corrección cancelada localmente. No se descargó ningún archivo; no se pudo registrar el rechazo remoto.");
      });
    }
  }

  return <section className="correction-preview" aria-labelledby="correction-preview-title">
    <h3 id="correction-preview-title">Previsualizar una corrección</h3>
    <p>{demo ? "Demostración local del flujo de aprobación." : "Revisa una propuesta antes de autorizar la descarga."} Se genera una copia con otro nombre; no se ejecuta código ni se modifica el archivo original.</p>
    <p><strong>Hallazgo seleccionado:</strong> {finding.titulo} · {archivo}:{finding.linea}</p>
    {partial && <p className="correction-warning">El análisis es parcial. Aprobar una copia no completa la revisión ni garantiza seguridad.</p>}
    {!client && <p role="status">No hay una corrección descargable disponible para este resultado.</p>}
    {(phase === "idle" || phase === "done") && <button className="primary-button" disabled={!client} onClick={() => void preview()}>Previsualizar propuesta</button>}
    {phase === "previewing" && <p role="status">Preparando la previsualización…</p>}
    {proposal && <>
      <div className="correction-comparison">
        <div><h4>Original · {archivo}</h4><pre tabIndex={0} aria-label="Código original"><code>{codigo}</code></pre></div>
        <div><h4>Propuesta · {proposal.archivo_salida}</h4><pre tabIndex={0} aria-label="Código propuesto"><code>{proposal.codigo_propuesto}</code></pre></div>
      </div>
      {proposal.advertencias.length > 0 && <ul>{proposal.advertencias.map((warning, index) => <li key={index}>{warning}</li>)}</ul>}
      <label className="correction-consent"><input type="checkbox" checked={consent} disabled={phase === "approving"} onChange={event => setConsent(event.target.checked)} />He revisado la propuesta y autorizo generar y descargar únicamente esta copia corregida.</label>
      <button className="primary-button" disabled={!consent || phase !== "review"} onClick={() => void approve()}>{phase === "approving" ? "Confirmando…" : "Confirmar y descargar copia"}</button>
    </>}
    {(phase === "previewing" || phase === "review" || phase === "approving") && <button className="secondary-button correction-cancel" onClick={cancel}>Cancelar corrección</button>}
    {message && <p role="status">{message}</p>}
    {error && <p role="alert">{error}</p>}
  </section>;
}
