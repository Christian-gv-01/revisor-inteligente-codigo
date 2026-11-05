import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { parseResponse, parseZipResponse } from "../src/services/api";
import { createReport } from "../src/services/report";
import { FindingsPanel } from "../src/components/FindingsPanel";
import { EvidenceTrace } from "../src/components/EvidenceTrace";
import type { AnalysisInput } from "../src/types/analysis";

const input: AnalysisInput = {
  tipo: "codigo",
  archivo: "usuarios.py",
  codigo: "eval(input())",
  url: "",
  fichero: null,
};

const estatico = {
  archivo: "usuarios.py",
  estado: "completo",
  mensaje: null,
  herramientas: [
    { herramienta: "ruff", estado: "ok", hallazgos: 0 },
    { herramienta: "bandit", estado: "ok", hallazgos: 1 },
  ],
  hallazgos: [
    {
      herramienta: "bandit",
      regla: "B307",
      tipo: "seguridad",
      linea: 1,
      columna: null,
      severidad: "alta",
      titulo: "Posible eval inseguro",
      descripcion: "Bandit detectó una llamada potencialmente insegura.",
      confianza: "alta",
      referencia: "https://bandit.readthedocs.io/",
    },
  ],
};

const respuestaParcial = {
  archivo: "usuarios.py",
  estado: "parcial",
  hallazgos: [],
  fuentes: [],
  mensaje: "Gemini no está disponible; se presentan observaciones estáticas.",
  analisis_estatico: estatico,
};

describe("Contrato estático Ruff/Bandit y degradación honesta", () => {
  it("acepta una respuesta parcial y conserva procedencia separada", () => {
    const resultado = parseResponse(respuestaParcial, input);
    expect(resultado.estado).toBe("parcial");
    expect(resultado.hallazgos).toEqual([]);
    expect(resultado.fuentes).toEqual([]);
    expect(resultado.analisis_estatico).toHaveLength(1);
    expect(resultado.analisis_estatico?.[0].hallazgos[0]).toMatchObject({
      herramienta: "bandit",
      regla: "B307",
      linea: 1,
      confianza: "alta",
    });
  });

  it("conserva compatibilidad de informes sin análisis estático", () => {
    const resultado = parseResponse({
      archivo: "usuarios.py",
      estado: "analizado",
      hallazgos: [],
      fuentes: [],
    }, input);
    expect(resultado.analisis_estatico).toBeUndefined();
    expect(resultado.estado).toBe("analizado");
  });

  it("rechaza datos inválidos y rutas de otro archivo", () => {
    const invalido = { ...estatico, archivo: "otro.py" };
    expect(() => parseResponse({
      ...respuestaParcial,
      analisis_estatico: invalido,
    }, input)).toThrow();

    expect(() => parseResponse({
      ...respuestaParcial,
      analisis_estatico: {
        ...estatico,
        hallazgos: [{ ...estatico.hallazgos[0], linea: 0 }],
      },
    }, input)).toThrow();

    expect(() => parseResponse({
      ...respuestaParcial,
      analisis_estatico: {
        ...estatico,
        herramientas: [
          { herramienta: "bandit", estado: "ok", hallazgos: 1 },
          { herramienta: "bandit", estado: "ok", hallazgos: 1 },
        ],
      },
    }, input)).toThrow();
  });

  it("agrega informes ZIP sin perder el archivo de cada regla", () => {
    const zipInput: AnalysisInput = {
      ...input,
      tipo: "zip",
      fichero: new File(["zip-demo"], "prueba.zip"),
    };
    const parsed = parseZipResponse({
      archivo_zip: "prueba.zip",
      estado: "parcial",
      total_archivos: 2,
      informes: [
        respuestaParcial,
        {
          archivo: "src/limpio.py",
          estado: "parcial",
          hallazgos: [],
          fuentes: [],
          mensaje: "Solo análisis estático.",
          analisis_estatico: {
            ...estatico,
            archivo: "src/limpio.py",
            hallazgos: [],
            herramientas: [
              { herramienta: "ruff", estado: "ok", hallazgos: 0 },
              { herramienta: "bandit", estado: "ok", hallazgos: 0 },
            ],
          },
        },
      ],
    }, zipInput);

    expect(parsed.estado).toBe("parcial");
    expect(parsed.analisis_estatico?.map(r => r.archivo)).toEqual([
      "usuarios.py",
      "src/limpio.py",
    ]);
    expect(parsed.hallazgos).toHaveLength(0);
    expect(parsed.mensaje).toContain("usuarios.py");
    expect(parsed.mensaje).toContain("src/limpio.py");
  });

  it("exporta JSON con los motores separados de las citas IA", () => {
    const parsed = parseResponse(respuestaParcial, input);
    const json = createReport(parsed);
    expect(json.estado).toBe("parcial");
    expect(json.hallazgos).toEqual([]);
    expect(json.analisis_estatico).toHaveLength(1);
    expect(json.analisis_estatico[0].hallazgos[0].regla).toBe("B307");
  });

  it("la interfaz nunca presenta el análisis parcial como libre de problemas", () => {
    const parsed = parseResponse(respuestaParcial, input);
    const html = renderToStaticMarkup(
      <FindingsPanel result={parsed} loading={false} onSelect={() => {}} />,
    );
    expect(html).toContain("Revisión contextual incompleta");
    expect(html).toContain("Revisión estática");
    expect(html).toContain("Bandit");
    expect(html).toContain("B307");
    expect(html).not.toContain("No se encontraron hallazgos");
    const trace = renderToStaticMarkup(
      <EvidenceTrace result={parsed} selected={null} loading={false} />,
    );
    expect(trace).toContain("Gemini no completó");
    expect(trace).not.toContain("El análisis no reportó hallazgos");
  });

  it("rechaza enlaces peligrosos aunque el backend entregue una referencia", () => {
    const parsed = parseResponse({
      ...respuestaParcial,
      analisis_estatico: {
        ...estatico,
        hallazgos: [{
          ...estatico.hallazgos[0],
          referencia: "javascript:alert(1)",
        }],
      },
    }, input);
    const html = renderToStaticMarkup(
      <FindingsPanel result={parsed} loading={false} onSelect={() => {}} />,
    );
    expect(html).not.toContain('href="javascript:');
    expect(html).not.toContain("Documentación de la herramienta");
  });
});
