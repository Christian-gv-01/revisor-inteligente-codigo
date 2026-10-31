import { afterEach, describe, expect, it, vi } from "vitest";
import {
  analyzeCode,
  parseResponse,
  parseZipResponse,
  validateFile,
  validateGithub,
  validateInput,
} from "../src/services/api";
import { analyzeDemo, demoResult, EXAMPLE_CODE } from "../src/services/demo";
import type { AnalysisInput } from "../src/types/analysis";

const input: AnalysisInput = {
  tipo: "codigo",
  archivo: "ejemplo.py",
  codigo: EXAMPLE_CODE,
  url: "",
  fichero: null,
};
const validResponse = {
  archivo: "ejemplo.py",
  estado: "analizado",
  hallazgos: [
    {
      linea: 7,
      severidad: "alta",
      categoria: "SQL",
      titulo: "Consulta",
      explicacion: "Riesgo",
      correccion_sugerida: "Usa parámetros",
    },
  ],
};
afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("Validación de entradas", () => {
  it.each(["https://github.com/user/repo", "https://github.com/user/repo.git"])(
    "acepta %s",
    (url) => expect(validateGithub(url)).toBe(true),
  );
  it.each([
    "http://github.com/user/repo",
    "https://github.com.evil.test/user/repo",
    "https://github.com/user/repo/tree/main",
    "https://u:p@github.com/user/repo",
    "https://github.com/user/repo?token=secret",
    "texto",
  ])("rechaza %s", (url) => expect(validateGithub(url)).toBe(false));
  it("rechaza código vacío, demasiado largo o binario", () => {
    for (const codigo of ["", " ", "a".repeat(12001), "\0test"])
      expect(() => validateInput({ ...input, codigo })).toThrow();
  });
  it("permite el límite exacto", () =>
    expect(() =>
      validateInput({ ...input, codigo: "a".repeat(12000) }),
    ).not.toThrow());
  it("rechaza nombres inválidos y archivos no elegidos", () => {
    expect(() => validateInput({ ...input, archivo: "test.txt" })).toThrow();
    expect(() => validateInput({ ...input, tipo: "python" })).toThrow();
    expect(() => validateInput({ ...input, tipo: "zip" })).toThrow();
  });
  it("valida extensión, archivo vacío y tamaño", () => {
    expect(() =>
      validateFile(new File(["x"], "script.py"), "python"),
    ).not.toThrow();
    expect(() =>
      validateFile(new File(["x"], "script.txt"), "python"),
    ).toThrow();
    expect(() => validateFile(new File([], "script.py"), "python")).toThrow();
    expect(() =>
      validateFile(new File(["x".repeat(48001)], "script.py"), "python"),
    ).toThrow();
  });
});
describe("Contrato y servicio HTTP", () => {
  it("normaliza los hallazgos del backend y mantiene el código original", () => {
    const result = parseResponse(validResponse, input);
    expect(result.demo).toBe(false);
    expect(result.hallazgos[0]).toMatchObject({
      archivo: "ejemplo.py",
      linea: 7,
      severidad: "alta",
    });
    expect(result.archivos[0].codigo).toBe(EXAMPLE_CODE);
  });
  it("acepta un informe sin hallazgos", () =>
    expect(
      parseResponse({ ...validResponse, hallazgos: [] }, input).hallazgos,
    ).toEqual([]));
  it.each([
    null,
    {},
    { ...validResponse, archivo: "otro.py" },
    {
      ...validResponse,
      hallazgos: [{ ...validResponse.hallazgos[0], linea: 0 }],
    },
    {
      ...validResponse,
      hallazgos: [{ ...validResponse.hallazgos[0], severidad: "desconocida" }],
    },
  ])("rechaza respuestas incompatibles", (response) =>
    expect(() => parseResponse(response, input)).toThrow(),
  );
  it("envía solo archivo y codigo al endpoint acordado", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify(validResponse)));
    vi.stubGlobal("fetch", fetch);
    await analyzeCode(input);
    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/analizar",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ archivo: input.archivo, codigo: input.codigo }),
      }),
    );
  });
  it.each([
    [422, "entrada"],
    [503, "servidor"],
    [429, "servidor"],
  ])("clasifica HTTP %s", async (status, kind) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("{}", { status: Number(status) })),
    );
    await expect(analyzeCode(input)).rejects.toMatchObject({ kind });
  });
  it("distingue error de red de error de servidor", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("Failed to fetch")),
    );
    await expect(analyzeCode(input)).rejects.toMatchObject({
      kind: "conexion",
    });
  });
  it("rechaza JSON inválido sin presentarlo como resultado vacío", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("<html>Error</html>")),
    );
    await expect(analyzeCode(input)).rejects.toMatchObject({
      kind: "contrato",
    });
  });  


  it("analiza un repositorio GitHub y conserva la abstención", async () => {
  const url = "https://github.com/test/repo";

  const respuesta = {
    repositorio: url,
    estado: "analizado",
    total_archivos: 1,
    informes: [
      {
        archivo: "hello_world.py",
        estado: "abstenido",
        hallazgos: [],
        fuentes: [],
        mensaje: "No hay evidencia documental suficiente.",
      },
    ],
  };

  const fetchMock = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(respuesta), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );

  vi.stubGlobal("fetch", fetchMock);

  const resultado = await analyzeCode({
    ...input,
    tipo: "github",
    url,
  });

  expect(fetchMock).toHaveBeenCalledWith(
    "/api/v1/repositorios/github",
    expect.objectContaining({
      method: "POST",
      body: JSON.stringify({ url }),
    }),
  );

  expect(resultado.estado).toBe("abstenido");
  expect(resultado.archivos).toEqual([
    { nombre: "hello_world.py", codigo: null },
  ]);
  expect(resultado.hallazgos).toEqual([]);
});

  it("expone la cancelación al consumidor", async () => {
    const controller = new AbortController();
    controller.abort();
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(controller.signal.reason));
    await expect(analyzeCode(input, controller.signal)).rejects.toMatchObject({
      name: "AbortError",
    });
  });
});
describe("Demostración explícita", () => {
  it("vincula los tres ejemplos con las líneas correctas", () => {
    const result = demoResult(input, "hallazgos");
    expect(result.demo).toBe(true);
    expect(result.hallazgos.map((f) => f.linea)).toEqual([7, 12, 16]);
  });
  it("no asigna hallazgos fijos a código diferente", () =>
    expect(
      demoResult({ ...input, codigo: 'print("Hola")' }, "hallazgos").hallazgos,
    ).toEqual([]));
  it("permite probar el estado sin hallazgos", () =>
    expect(demoResult(input, "vacio").hallazgos).toEqual([]));
  it("usa archivos ficticios identificables para proyectos", () =>
    expect(
      demoResult({ ...input, tipo: "github" }, "hallazgos").archivos.map(
        (f) => f.nombre,
      ),
    ).toEqual(["demo/usuarios.py", "demo/saludo.py"]));
  it("simula errores identificados", () => {
    expect(() => demoResult(input, "servidor")).toThrow("simulado");
    expect(() => demoResult(input, "conexion")).toThrow("simulado");
  });
  it("cancela una simulación en curso", async () => {
    vi.useFakeTimers();
    const controller = new AbortController();
    const pending = analyzeDemo(input, "hallazgos", controller.signal);
    controller.abort();
    await expect(pending).rejects.toMatchObject({ name: "AbortError" });
  });
});

describe("Carga multipart y respuesta ZIP", () => {
  const file = new File(["PK"], "proyecto.zip");
  const zipInput: AnalysisInput = { ...input, tipo: "zip", fichero: file };
  const response = {
    archivo_zip: "proyecto.zip",
    estado: "analizado",
    total_archivos: 2,
    informes: [
      validResponse,
      { ...validResponse, archivo: "otro.py", hallazgos: [] },
    ],
  };
  it("envía el Python editado al endpoint de archivos", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify(validResponse)));
    vi.stubGlobal("fetch", fetch);
    await analyzeCode({
      ...input,
      tipo: "python",
      fichero: new File(["original"], "ejemplo.py"),
    });
    const [url, options] = fetch.mock.calls[0];
    expect(url).toBe("/api/v1/archivos");
    expect(options.headers).toBeUndefined();
    expect(await options.body.get("archivo").text()).toBe(input.codigo);
  });
  it("envía ZIP como archivo sin descomprimir en el navegador", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify(response)));
    vi.stubGlobal("fetch", fetch);
    const result = await analyzeCode(zipInput);
    expect(fetch.mock.calls[0][0]).toBe("/api/v1/archivos/zip");
    expect(fetch.mock.calls[0][1].body.get("archivo").name).toBe(
      "proyecto.zip",
    );
    expect(result.archivos).toEqual([
      { nombre: "ejemplo.py", codigo: null },
      { nombre: "otro.py", codigo: null },
    ]);
    expect(result.hallazgos[0].archivo).toBe("ejemplo.py");
  });
  it("rechaza totales inconsistentes, duplicados y nombre de ZIP incorrecto", () => {
    expect(() =>
      parseZipResponse({ ...response, total_archivos: 3 }, zipInput),
    ).toThrow();
    expect(() =>
      parseZipResponse(
        { ...response, informes: [validResponse, validResponse] },
        zipInput,
      ),
    ).toThrow();
    expect(() =>
      parseZipResponse({ ...response, archivo_zip: "otro.zip" }, zipInput),
    ).toThrow();
  });
  it("produce identificadores únicos entre archivos", () => {
    const result = parseZipResponse(
      {
        ...response,
        informes: [validResponse, { ...validResponse, archivo: "otro.py" }],
      },
      zipInput,
    );
    expect(new Set(result.hallazgos.map((f) => f.id)).size).toBe(2);
  });
  it("rechaza ZIP mayores de 5 MiB", () => {
    expect(() =>
      validateFile(
        new File([new Uint8Array(5 * 1024 * 1024 + 1)], "proyecto.zip"),
        "zip",
      ),
    ).toThrow();
  });
});
