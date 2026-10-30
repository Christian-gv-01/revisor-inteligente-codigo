import { useState } from "react";
import { FindingsPanel } from "../src/components/FindingsPanel";
import { parseResponse } from "../src/services/api";

const sources = [
  { id: "seguridad_python-002", documento: "seguridad_python.md", fuente: "OWASP SQL Injection Prevention Cheat Sheet", seccion: "Regla 2: Prevenir inyección SQL", url: "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html", distancia: 0.391 },
  { id: "seguridad_python-004", documento: "seguridad_python.md", fuente: "OWASP Injection Prevention Cheat Sheet", seccion: "Regla 4: Prevención general de inyecciones", url: "https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html", distancia: 0.593 },
];

export function Preview() {
  const [scenario, setScenario] = useState("fuentes");
  const [narrow, setNarrow] = useState(false);
  const result = parseResponse({
    archivo: "ejemplo.py", estado: scenario === "abstencion" ? "abstenido" : "analizado",
    mensaje: scenario === "abstencion" ? "No se encontraron fuentes suficientes para fundamentar una respuesta." : scenario === "parcial" ? "otro.py: El análisis de este archivo se abstuvo por falta de fuentes." : null,
    fuentes: scenario === "sin-fuentes" ? [] : sources,
    hallazgos: scenario === "abstencion" ? [] : [{
      linea: 3, severidad: "alta", categoria: "Inyección SQL", titulo: "Consulta SQL construida mediante concatenación",
      explicacion: "La entrada del usuario se incorpora a la consulta SQL y puede modificar su estructura.",
      correccion_sugerida: 'cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre,))',
      referencias: scenario === "referencia-ausente" ? ["referencia-no-recibida"] : [sources[0].id],
    }],
  }, { tipo: "codigo", archivo: "ejemplo.py", codigo: "# Ejemplo de presentación", url: "", fichero: null });
  return (
    <main style={{ padding: "24px 16px", maxWidth: narrow ? 390 : 900, margin: "0 auto" }}>
      <p style={{ color: "#73551e", lineHeight: 1.7, marginBottom: 16 }}><strong>VALIDACIÓN VISUAL · DATOS SIMULADOS</strong><br />Componente real del frontend. Esta página no ejecuta Gemini ni acredita la calidad de sus respuestas.</p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 20 }}>
        <label>Escenario <select value={scenario} onChange={e => setScenario(e.target.value)}>
          <option value="fuentes">Fuentes y citas</option><option value="sin-fuentes">Sin fuentes</option>
          <option value="referencia-ausente">Referencia ausente</option><option value="abstencion">Abstención</option><option value="parcial">ZIP parcial</option>
        </select></label>
        <label><input type="checkbox" checked={narrow} onChange={e => setNarrow(e.target.checked)} /> Contenedor de 390 px</label>
      </div>
      <FindingsPanel result={result} loading={false} onSelect={() => {}} />
    </main>
  );
}
