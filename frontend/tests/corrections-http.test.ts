import { beforeAll, describe, expect, it } from "vitest";
import { SQL_EXAMPLE_CODE } from "../src/services/demo";
import { sha256, validateApprovedCopy, validateProposal, validateRejection } from "../src/services/corrections";

const base = process.env.INTEGRATION_API_BASE_URL;
const suite = base ? describe : describe.skip;
const path = "/api/v1/correcciones";

// Fetch real contra FastAPI; el jar reproduce las cookies de una sesión de
// navegador en Node. Solo el proveedor externo está simulado por el runner.
function jar() {
  let cookie = "";
  return async (url: string, body: unknown) => {
    const r = await fetch(`${base}${url}`, { method: "POST", headers: {
      "Content-Type": "application/json", ...(cookie ? { Cookie: cookie } : {}),
    }, body: JSON.stringify(body) });
    const set = r.headers.get("set-cookie");
    if (set) cookie = set.split(";")[0];
    return r;
  };
}
async function preview(send = jar(), code = SQL_EXAMPLE_CODE) {
  const request = { archivo: "usuarios.py", codigo_original: code,
    sha256_original: await sha256(code), objetivo: { linea: 6, descripcion: "Parametrizar consulta" } };
  const r = await send(`${path}/previsualizar`, request);
  expect(r.status).toBe(200);
  const p = await validateProposal(await r.json(), request);
  return { send, p };
}
const decision = (p: Awaited<ReturnType<typeof preview>>["p"], d: "aprobar" | "rechazar") => ({
  decision: d, sha256_original: p.sha256_original, sha256_propuesto: p.sha256_propuesto,
});

suite("Correcciones: validadores frontend y backend reales, proveedor simulado", () => {
  beforeAll(async () => {
    const r = await fetch(`${base}/health`);
    expect(r.headers.get("X-Integration-Provider")).toBe("stub");
  });
  it("previsualiza y aprueba exactamente el contenido; repetir conserva la copia", async () => {
    const { send, p } = await preview();
    const url = `${path}/${p.propuesta_id}/decision`;
    const r = await send(url, decision(p, "aprobar"));
    expect(r.status).toBe(200);
    const raw = await r.json();
    expect((await validateApprovedCopy(raw, p)).code).toBe(p.codigo_propuesto);
    expect(await (await send(url, decision(p, "aprobar"))).json()).toEqual(raw);
  });
  it("rechaza sin contenido y bloquea aprobación posterior con 409", async () => {
    const { send, p } = await preview();
    const url = `${path}/${p.propuesta_id}/decision`;
    const r = await send(url, decision(p, "rechazar"));
    expect(r.status).toBe(200);
    const raw = await r.json(); validateRejection(raw, p);
    expect(raw).not.toHaveProperty("contenido");
    expect((await send(url, decision(p, "aprobar"))).status).toBe(409);
  });
  it("otro navegador no accede con ID y hashes; propietario conserva acceso", async () => {
    const { send, p } = await preview();
    expect((await jar()(`${path}/${p.propuesta_id}/decision`, decision(p, "aprobar"))).status).toBe(404);
    const otro = await preview();
    expect((await otro.send(`${path}/${p.propuesta_id}/decision`, decision(p, "aprobar"))).status).toBe(404);
    expect((await send(`${path}/${p.propuesta_id}/decision`, decision(p, "aprobar"))).status).toBe(200);
  });
  it("hash alterado produce conflicto sin cerrar la propuesta válida", async () => {
    const { send, p } = await preview(); const url = `${path}/${p.propuesta_id}/decision`;
    expect((await send(url, { ...decision(p, "aprobar"), sha256_propuesto: "0".repeat(64) })).status).toBe(409);
    expect((await send(url, decision(p, "aprobar"))).status).toBe(200);
  });
  it("propuesta caducada produce 410 real", async () => {
    const { send, p } = await preview();
    const r = await fetch(`${base}/__integration__/correcciones/${p.propuesta_id}/caducar`, { method: "POST" });
    expect(r.status).toBe(200);
    expect((await send(`${path}/${p.propuesta_id}/decision`, decision(p, "aprobar"))).status).toBe(410);
  });
  it("el 422 no refleja el código recibido", async () => {
    const r = await jar()(`${path}/previsualizar`, { archivo: "../caso.py", codigo_original: "MARCADOR_PRIVADO_QA", sha256_original: "0".repeat(64), objetivo: { linea: 1, descripcion: "Revisar" } });
    expect(r.status).toBe(422); expect(await r.text()).not.toContain("MARCADOR_PRIVADO_QA");
  });
  it("timeout del generador conserva un error 504 sanitizado", async () => {
    const code = SQL_EXAMPLE_CODE + "\n# INTEGRACION_ERROR";
    const r = await jar()(`${path}/previsualizar`, { archivo: "usuarios.py", codigo_original: code, sha256_original: await sha256(code), objetivo: { linea: 6, descripcion: "Revisar" } });
    expect(r.status).toBe(504); expect(await r.text()).not.toContain("INTEGRACION_ERROR");
  });
});
