import { afterEach, expect, it, vi } from "vitest";
import { configuredCorrectionClient, sha256, validateApprovedCopy, validateProposal, validateRejection } from "../src/services/corrections";
import { demoCorrectionClient } from "../src/services/correctionDemo";
import { SQL_EXAMPLE_CODE } from "../src/services/demo";

const signal = () => new AbortController().signal;
async function fixture() {
  const request = { archivo: "usuarios.py", codigo_original: SQL_EXAMPLE_CODE,
    sha256_original: await sha256(SQL_EXAMPLE_CODE), objetivo: { linea: 6, descripcion: "Parametrizar consulta" } };
  const raw = await demoCorrectionClient.preview(request, signal());
  const proposal = await validateProposal(raw, request);
  return { request, proposal };
}
afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

it("no habilita peticiones de corrección real por defecto", () => {
  vi.stubEnv("VITE_CORRECTIONS_API_ENABLED", "0");
  const fetcher = vi.fn(); vi.stubGlobal("fetch", fetcher);
  expect(configuredCorrectionClient()).toBeUndefined();
  expect(fetcher).not.toHaveBeenCalled();
});
it("valida una copia diferente y conserva el original completo", async () => {
  const { request, proposal } = await fixture();
  expect(proposal.codigo_propuesto).toContain("cursor.execute(consulta, (nombre,))");
  expect(request.codigo_original).toBe(SQL_EXAMPLE_CODE);
  const approved = await demoCorrectionClient.decide(proposal, "aprobar", signal());
  expect(await validateApprovedCopy(approved, proposal)).toEqual({ name: "usuarios.corregido.py", code: proposal.codigo_propuesto });
});
it.each(["../salida.py", "/tmp/salida.py", "C:\\salida.py", "usuarios.py", "salida.html"])("rechaza nombre de salida no seguro o igual al original: %s", async archivo_salida => {
  const { request, proposal } = await fixture();
  await expect(validateProposal({ ...proposal, archivo_salida }, request)).rejects.toThrow();
});
it("rechaza propuestas vinculadas a otro archivo, hash o contenido original", async () => {
  const { request, proposal } = await fixture();
  await expect(validateProposal({ ...proposal, archivo_original: "otro.py" }, request)).rejects.toThrow();
  await expect(validateProposal({ ...proposal, sha256_original: "0".repeat(64) }, request)).rejects.toThrow();
  await expect(validateProposal(proposal, { ...request, codigo_original: "print('otro')" })).rejects.toThrow();
});
it("rechaza caducidad, modificación de la propuesta y contenido idéntico al original", async () => {
  const { request, proposal } = await fixture();
  await expect(validateProposal({ ...proposal, caduca_en: "2020-01-01T00:00:00Z" }, request)).rejects.toThrow();
  await expect(validateProposal({ ...proposal, codigo_propuesto: "print('sustituido')" }, request)).rejects.toThrow();
  await expect(validateProposal({ ...proposal, codigo_propuesto: request.codigo_original }, request)).rejects.toThrow();
});
it("no descarga una respuesta que cambió después de aprobar la vista previa", async () => {
  const { proposal } = await fixture();
  const approved = await demoCorrectionClient.decide(proposal, "aprobar", signal()) as Record<string, unknown>;
  for (const change of [{ contenido: "print('distinto')" }, { archivo_salida: "otra.py" }, { propuesta_id: "otra-id" }, { sha256_contenido: "0".repeat(64) }, { estado: "rechazada" }]) {
    await expect(validateApprovedCopy({ ...approved, ...change }, proposal)).rejects.toThrow();
  }
});
it("rechazar solo devuelve un estado y no un archivo", async () => {
  const { proposal } = await fixture();
  const response = await demoCorrectionClient.decide(proposal, "rechazar", signal());
  expect(response).toEqual({ version: "1", propuesta_id: proposal.propuesta_id, estado: "rechazada" });
  expect(() => validateRejection(response, proposal)).not.toThrow();
  expect(() => validateRejection({ version: "1", propuesta_id: "otra-propuesta", estado: "rechazada" }, proposal)).toThrow();
  expect(() => validateRejection({ version: "1", propuesta_id: proposal.propuesta_id, estado: "aprobada" }, proposal)).toThrow();
});


it("explica el HTTP 422 sin revelar datos del código enviado", async () => {
  vi.stubEnv("VITE_CORRECTIONS_API_ENABLED", "1");
  const original = "token_interno = 'PRIVADO'";
  const request = { archivo: "example.py", codigo_original: original,
    sha256_original: await sha256(original),
    objetivos: [{ linea: 1, descripcion: "Corregir" }] };
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
    new Response(JSON.stringify({ detail: [
      { loc: ["body", "objetivos", 0, "descripcion"], input: original,
        type: "string_too_short" },
    ] }), { status: 422, headers: { "Content-Type": "application/json" } })
  ));
  const client = configuredCorrectionClient();
  expect(client).toBeDefined();
  await expect(client!.preview(request, signal())).rejects.toThrow("campo descripcion");
  const err = await client!.preview(request, signal()).catch(e => String(e.message));
  expect(err).not.toContain("PRIVADO");
});

it("diferencia un 422 por abstención del proveedor y un timeout", async () => {
  vi.stubEnv("VITE_CORRECTIONS_API_ENABLED", "1");
  const original = "return eval(x)";
  const request = { archivo: "example.py", codigo_original: original,
    sha256_original: await sha256(original),
    objetivos: [{ linea: 1, descripcion: "Corregir" }] };
  const send = vi.fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({
      detail: "No existe una corrección concreta y sustentable para este hallazgo.",
    }), { status: 422, headers: { "Content-Type": "application/json" } }))
    .mockResolvedValueOnce(new Response("{}", { status: 504 }));
  vi.stubGlobal("fetch", send);
  const client = configuredCorrectionClient()!;
  await expect(client.preview(request, signal())).rejects.toThrow("No se obtuvo un parche local válido para 1 hallazgo(s)");
  await expect(client.preview(request, signal())).rejects.toThrow("no respondió dentro del plazo");
});


it("explica el rechazo de tres objetivos sin dar a entender que se corrigieron", async () => {
  vi.stubEnv("VITE_CORRECTIONS_API_ENABLED", "1");
  const code = "x = 1\ny = 2\nz = 3";
  const request = {
    archivo: "example.py", codigo_original: code, sha256_original: await sha256(code),
    objetivos: [1, 2, 3].map(linea => ({ linea, descripcion: "Revisar" })),
  };
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(
    JSON.stringify({ detail: "No existe una corrección concreta y sustentable para este hallazgo." }),
    { status: 422, headers: { "Content-Type": "application/json" } },
  )));
  await expect(configuredCorrectionClient()!.preview(request, signal()))
    .rejects.toThrow("3 hallazgo(s) seleccionado(s)");
});
