import { useEffect, useState } from "react";
import type { ProjectBudget } from "../services/projectBudget";
import "./ProjectBudgetReview.css";

export function ProjectBudgetReview({ proposal, disabled, onApprove, onReject }: {
  proposal: ProjectBudget; disabled: boolean; onApprove: () => void; onReject: () => void;
}) {
  const [accepted, setAccepted] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);
  const b = proposal.presupuesto;
  const expired = Date.parse(proposal.caduca_en) <= now;
  return <section className="project-budget" aria-labelledby="budget-title">
    <h3 id="budget-title">Revisa el presupuesto del proyecto</h3>
    <p>Preparación completada sin consultar a Gemini. Se analizará la instantánea de estos archivos:</p>
    <ul>{proposal.archivos.map(f => <li key={f.archivo}>{f.archivo} · {f.caracteres} caracteres</li>)}</ul>
    <p>{b.analisis_previstos} análisis previstos · máximo {b.max_intentos_proveedor} intentos al proveedor, incluidos reintentos.</p>
    <p>Modelo: {b.modelo}. Plazo cooperativo: {b.plazo_cooperativo_segundos} s; algunas tareas locales pueden finalizar después.</p>
    <p>El consumo real puede ser menor. Este límite de llamadas no es una cotización monetaria. La aprobación vence a las {new Date(proposal.caduca_en).toLocaleTimeString()}.</p>
    <p>Una vez aprobado, dejar de esperar en el navegador no revoca las llamadas iniciadas.</p>
    <label><input type="checkbox" checked={accepted} disabled={disabled || expired} onChange={e => setAccepted(e.target.checked)} />
      Autorizo analizar esta instantánea dentro del presupuesto indicado.</label>
    <div className="project-budget-actions">
      <button className="primary-button" disabled={disabled || expired || !accepted} onClick={onApprove}>Aprobar presupuesto y analizar</button>
      <button className="secondary-button" disabled={disabled} onClick={onReject}>Rechazar presupuesto</button>
    </div>
    {expired && <p role="alert">El presupuesto caducó. Solicita uno nuevo.</p>}
  </section>;
}
