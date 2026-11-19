import { useEffect, useRef, useState } from "react";
import type { Finding } from "../types/analysis";
import type { CorrectionClient, CorrectionProposal } from "../services/corrections";
import { downloadCopy, sha256, validateApprovedCopy, validateProposal, validateRejection } from "../services/corrections";
import "./CorrectionPreview.css";

interface Props {
  archivo: string;
  codigo: string;
  finding: Finding;
  findings?: Finding[];
  demo: boolean;
  partial?: boolean;
  client?: CorrectionClient;
}

export function CorrectionPreview({ archivo, codigo, finding, findings, demo, partial, client }: Props) {
  const [proposal, setProposal] = useState<CorrectionProposal | null>(null);
  // Solo el hallazgo abierto queda marcado inicialmente.
  const [selectedIds, setSelectedIds] = useState<string[]>([finding.id]);
  const [consent, setConsent] = useState(false);
  const [phase, setPhase] = useState<"idle" | "previewing" | "review" | "approving" | "done">("idle");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const pending = useRef<AbortController | null>(null);
  const disponibles = (findings ?? [finding]).filter(item => item.archivo === archivo)
    .filter((item, index, list) => list.findIndex(other => other.id === item.id) === index);
  const seleccionados = disponibles.filter(item => selectedIds.includes(item.id));
  const lineasSeleccionadas = new Set(seleccionados.map(item => item.linea));
  const excluidas = [...new Set(disponibles.filter(item => !lineasSeleccionadas.has(item.linea))
    .map(item => item.linea))];
  // El análisis puede contener sugerencias vacías o líneas no localizables:
  // se usa la descripción visible como alternativa y se valida antes de llamar a la API.
  const totalLineas = codigo.replace(/\r\n?/g, "\n").replace(/\n$/, "").split("\n").length;
  const objetivosValidos = seleccionados.every(item => Number.isInteger(item.linea) &&
    item.linea >= 1 && item.linea <= totalLineas);

  // El padre desmonta esta revisión al editar el código, cambiar archivo o hallazgo.
  useEffect(() => () => pending.current?.abort(), []);

  async function preview() {
    if (!client || !seleccionados.length || !objetivosValidos ||
        phase === "previewing" || phase === "approving" || proposal ||
        (pending.current && !pending.current.signal.aborted)) return;
    const controller = new AbortController();
    pending.current = controller;
    setConsent(false); setProposal(null); setMessage(""); setError(""); setPhase("previewing");
    try {
      const request = { archivo, codigo_original: codigo, sha256_original: await sha256(codigo),
        objetivos: seleccionados.map(item => ({
          linea: item.linea,
          descripcion: (item.correccion_sugerida?.trim() || item.explicacion?.trim() ||
            item.titulo?.trim() || "Revisar el problema seleccionado").slice(0, 1000),
        })),
        lineas_excluidas: excluidas };
      if (controller.signal.aborted) return;
      const candidate = await validateProposal(await client.preview(request, controller.signal), request);
      if (controller.signal.aborted) return;
      setProposal(candidate); setPhase("review");
    } catch (cause) {
      if (controller.signal.aborted) return;
      setError(cause instanceof Error ? cause.message : "No se pudo preparar la propuesta.");
      setPhase("idle");
    } finally {
      if (pending.current === controller) pending.current = null;
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
    {!demo && <p>La propuesta se conserva temporalmente mientras decides y caduca a los cinco minutos. La revisión humana sigue siendo necesaria antes de usar la copia.</p>}
    <fieldset className="correction-targets" disabled={phase === "previewing" || phase === "approving" || !!proposal}>
      <legend>Selecciona qué hallazgos quieres corregir</legend>
      <p>Solo se solicitará una corrección para los hallazgos marcados. Los demás deben mantenerse sin cambios.</p>
      {disponibles.map(item => <label className="correction-target" key={item.id}>
        <input type="checkbox" aria-label={`Corregir ${item.titulo}, línea ${item.linea}`}
          checked={selectedIds.includes(item.id)}
          disabled={!selectedIds.includes(item.id) && selectedIds.length >= 10}
          onChange={event => {
            const checked = event.target.checked;
            setSelectedIds(previous => checked
              ? [...previous, item.id]
              : previous.filter(id => id !== item.id));
            setConsent(false);
            setMessage("");
            setError("");
          }} />
        <span><strong>{item.titulo}</strong> · línea {item.linea} · {item.severidad}</span>
      </label>)}
      <p className="correction-selection-count">{seleccionados.length} seleccionado(s) de {disponibles.length}. Máximo 10 por solicitud. Si la IA intenta modificar otras zonas, la propuesta será rechazada.</p>
    </fieldset>
    {!objetivosValidos && <p role="alert">Hay hallazgos cuya línea no existe en el archivo actual. Analiza nuevamente antes de corregir.</p>}
    {proposal && <p role="status">Selección bloqueada mientras revisas esta propuesta. Cancélala para cambiar hallazgos.</p>}
    {partial && <p className="correction-warning">El análisis es parcial. Aprobar una copia no completa la revisión ni garantiza seguridad.</p>}
    {!client && <p role="status">No hay una corrección descargable disponible para este resultado.</p>}
    {(phase === "idle" || phase === "done") && <button className="primary-button" disabled={!client || seleccionados.length === 0 || !objetivosValidos} onClick={() => void preview()}>Previsualizar propuesta para {seleccionados.length} hallazgo(s)</button>}
    {phase === "previewing" && <p role="status">Preparando una corrección localizada con Gemini. Puedes cancelar sin modificar el original.</p>}
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

