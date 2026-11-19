import { useState } from "react";
import { createRoot } from "react-dom/client";
import { CorrectionPreview } from "../src/components/CorrectionPreview";
import { demoCorrectionClient } from "../src/services/correctionDemo";
import type { CorrectionClient, CorrectionRequest } from "../src/services/corrections";
import { SQL_EXAMPLE_CODE } from "../src/services/demo";
import "../src/styles/global.css";

export function Fixture() {
  const [revision, setRevision] = useState(0);
  const [actions, setActions] = useState<string[]>([]);
  const [lastRequest, setLastRequest] = useState<CorrectionRequest | null>(null);
  const scenario = new URLSearchParams(location.search).get("scenario");
  const client: CorrectionClient = {
    async preview(request, signal) {
      setLastRequest(request);
      return demoCorrectionClient.preview(request, signal);
    },
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
      findings={[
        { id: "sql", archivo: "usuarios.py", linea: 6, severidad: "alta", categoria: "SQL", titulo: "Consulta construida con entrada externa", explicacion: "Ejemplo", correccion_sugerida: "Parametrizar la consulta" },
        { id: "extra", archivo: "usuarios.py", linea: 9, severidad: "media", categoria: "Código", titulo: "Problema no seleccionado", explicacion: "Ejemplo", correccion_sugerida: "Revisar" },
      ]}
      demo partial client={client} />
    <button onClick={() => setRevision(previous => previous + 1)}>Cambiar entrada de prueba</button>
    <pre id="actions">{JSON.stringify(actions)}</pre>
    {/* Este registro pertenece al fixture, no a CODEGUARD. Su JSON
        no debe crear un scroll horizontal falso en las pruebas móviles. */}
    <pre id="last-request" style={{ maxWidth: "100%", whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>
      {JSON.stringify(lastRequest)}
    </pre>
  </main>;
}
createRoot(document.getElementById("root")!).render(<Fixture />);
