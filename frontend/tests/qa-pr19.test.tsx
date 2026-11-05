import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { parseResponse } from "../src/services/api";
import { createReport } from "../src/services/report";
import { FindingsPanel } from "../src/components/FindingsPanel";
import { EvidenceTrace } from "../src/components/EvidenceTrace";
import type { AnalysisInput } from "../src/types/analysis";

const input: AnalysisInput = {
  tipo: "codigo", archivo: "muchas.py", codigo: "eval(user_input)\n".repeat(101),
  url: "", fichero: null,
};
function response(count: number) {
  const hallazgos = ["ruff", "bandit"].flatMap(herramienta =>
    Array.from({ length: count }, (_, index) => ({
      herramienta, regla: herramienta === "ruff" ? "F821" : "B307",
      tipo: herramienta === "ruff" ? "calidad" : "seguridad",
      linea: index + 1, columna: null, severidad: "baja",
      titulo: "Observación", descripcion: "Código sintético de QA",
      confianza: herramienta === "bandit" ? "alta" : null, referencia: null,
    })),
  );
  return {
    archivo: input.archivo, estado: "analizado", hallazgos: [], fuentes: [],
    analisis_estatico: {
      archivo: input.archivo, estado: "completo", hallazgos,
      herramientas: ["ruff", "bandit"].map(herramienta => ({ herramienta, estado: "ok", hallazgos: count })),
    },
  };
}

describe("Regresiones QA de PR19", () => {
  it("acepta 101 alertas de cada motor y conserva las 202 al exportar", () => {
    const result = parseResponse(response(101), input);
    expect(createReport(result).analisis_estatico[0].hallazgos).toHaveLength(202);
  });
  it("no presenta un resultado global limpio cuando Ruff/Bandit emiten alertas", () => {
    const result = parseResponse(response(1), input);
    const html = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
    expect(html).toContain("F821");
    expect(html).toContain("B307");
    expect(html).not.toContain("No se encontraron hallazgos");
    expect(html).not.toContain("El análisis no reportó problemas");
    const trace = renderToStaticMarkup(<EvidenceTrace result={result} selected={null} loading={false} />);
    expect(trace).not.toContain("El análisis no reportó hallazgos");
    expect(trace).toContain("La revisión contextual no reportó hallazgos");
  });
  it.each(["error", "timeout", "no_disponible"])("no oculta un motor incompleto: %s", estado => {
    const data = response(0);
    data.analisis_estatico.estado = "parcial";
    data.analisis_estatico.herramientas[1].estado = estado;
    const result = parseResponse(data, input);
    const html = renderToStaticMarkup(<FindingsPanel result={result} loading={false} onSelect={() => {}} />);
    expect(html).toContain(`No completado (${estado})`);
    expect(html).not.toContain("No se encontraron hallazgos");
  });
  it("mantiene un límite de 400 alertas combinadas", () => {
    expect(parseResponse(response(200), input).analisis_estatico?.[0].hallazgos).toHaveLength(400);
    expect(() => parseResponse(response(201), input)).toThrow();
  });
});
