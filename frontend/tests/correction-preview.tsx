import { useState } from "react";
import { createRoot } from "react-dom/client";
import { CorrectionPreview } from "../src/components/CorrectionPreview";
import { demoCorrectionClient } from "../src/services/correctionDemo";
import type { CorrectionClient } from "../src/services/corrections";
import { SQL_EXAMPLE_CODE } from "../src/services/demo";
import "../src/styles/global.css";

export function Fixture() {
  const [revision, setRevision] = useState(0);
  const [actions, setActions] = useState<string[]>([]);
  const scenario = new URLSearchParams(location.search).get("scenario");
  const client: CorrectionClient = {
    preview: demoCorrectionClient.preview,
    async decide(proposal, decision, signal) {
      setActions(previous => [...previous, decision]);
      if (scenario === "slow" && decision === "aprobar") await new Promise(resolve => setTimeout(resolve, 700));
      const response = await demoCorrectionClient.decide(proposal, decision, signal);
      if (scenario === "changed" && decision === "aprobar") return { ...response, contenido: "print('contenido no aprobado')" };
      return response;
    },
  };
  return <main style={{ maxWidth: 1200, margin: "20px auto" }}>
    <h1>Confirmación humana · QA local</h1><p>Datos simulados. Sin llamadas a Backend, Gemini o Railway.</p>
    <CorrectionPreview key={revision} archivo="usuarios.py" codigo={SQL_EXAMPLE_CODE}
      finding={{ id: "sql", archivo: "usuarios.py", linea: 6, severidad: "alta", categoria: "SQL", titulo: "Consulta construida con entrada externa", explicacion: "Ejemplo", correccion_sugerida: "Parametrizar la consulta" }}
      demo partial client={client} />
    <button onClick={() => setRevision(previous => previous + 1)}>Cambiar entrada de prueba</button>
    <pre id="actions">{JSON.stringify(actions)}</pre>
  </main>;
}
createRoot(document.getElementById("root")!).render(<Fixture />);
