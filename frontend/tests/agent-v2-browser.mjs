import path from 'node:path';
import { pathToFileURL } from 'node:url';
import fs from 'node:fs/promises';
import { spawn } from 'node:child_process';
import assert from 'node:assert/strict';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE_PATH ? pathToFileURL(process.env.PLAYWRIGHT_MODULE_PATH).href : 'playwright');
const api = process.env.CODEGUARD_DEV_API_TARGET;
assert(api && new URL(api).hostname === '127.0.0.1', 'Solo servidor fixture en loopback');
const status = async () => (await fetch(`${api}/__agent_v2_fixture__/status`)).json();
assert.equal((await status()).proveedor, 'simulado');
const folder = process.argv[2], origin = 'http://127.0.0.1:5193';
const server = spawn(process.execPath, ['node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '5193', '--strictPort'], {
  cwd: path.resolve('frontend'), env: { ...process.env, VITE_PROJECT_BUDGET_ENABLED: '0', VITE_API_BASE_URL: '' }, stdio: 'ignore',
});
let browser;
const cases = [], errors = [], external = [];
try {
  for (let n = 0; n < 80; n++) {
    try { if ((await fetch(origin)).ok) break; } catch { /* inicio */ }
    await new Promise(r => setTimeout(r, 100));
  }
  browser = await chromium.launch({ headless: true, executablePath: process.env.CODEGUARD_BROWSER_PATH });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1080 } });
  await context.route('**/*', route => {
    if (new URL(route.request().url()).hostname === '127.0.0.1') return route.continue();
    external.push(route.request().url()); return route.abort();
  });
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  const run = async marker => {
    await page.goto(origin);
    await page.getByRole('button', { name: 'API real', exact: true }).click();
    await page.getByRole('button', { name: 'Archivo .py', exact: true }).click();
    const code = `nombre=input()\ncursor.execute("SELECT * FROM usuarios WHERE nombre = '" + nombre + "'")\n# ${marker}\n`;
    await page.locator('input[type=file]').setInputFiles({ name: 'muestra.py', mimeType: 'text/x-python', buffer: Buffer.from(code) });
    const response = page.waitForResponse(r => r.url().endsWith('/agente/analizar') && r.request().method() === 'POST');
    await page.getByRole('button', { name: 'Analizar código', exact: true }).click();
    const wire = await response;
    assert.equal(wire.status(), 200);
    assert.equal(wire.request().postDataJSON().version_herramientas, '2');
    const data = await wire.json();
    await fs.writeFile(`${folder}/${marker}.json`, JSON.stringify(data, null, 2));
    await page.locator('.agent-trace summary').click();
    return data;
  };
  const full = await run('V2_FULL');
  assert.equal(full.terminacion, 'max_pasos');
  await page.locator('.agent-trace').getByText('Línea solicitada: 2', { exact: false }).first().waitFor();
  await page.locator('.agent-references').getByText('seguridad_python-002', { exact: true }).waitFor();
  assert.equal(await page.locator('.agent-context code').count(), 3);
  assert.equal(await page.locator('.agent-references a').count(), 0);
  await page.screenshot({ path: `${folder}/agente-v2-escritorio.png`, fullPage: true });
  const propagated = await status();
  assert(propagated.propagacion.includes('contexto_en_siguiente_decision'));
  assert(propagated.propagacion.includes('contexto_y_referencias_en_sintesis'));
  cases.push({ caso: 'Herramientas, argumentos, resultados y propagación real a decisión/síntesis', aprobado: true });
  await page.setViewportSize({ width: 390, height: 844 });
  assert(await page.locator('.agent-trace').evaluate(el => el.scrollWidth <= el.clientWidth + 1));
  await page.screenshot({ path: `${folder}/agente-v2-movil.png`, fullPage: true });
  cases.push({ caso: 'Traza legible sin desbordamiento móvil', aprobado: true });
  await page.setViewportSize({ width: 1440, height: 1080 });
  const beforeEarly = await status(), early = await run('V2_EARLY'), afterEarly = await status();
  assert.equal(early.terminacion, 'finalizacion_anticipada'); assert.equal(early.pasos.length, 1);
  assert.equal(afterEarly.planes - beforeEarly.planes, 1); assert.equal(afterEarly.sintesis - beforeEarly.sintesis, 1);
  await page.getByRole('status').filter({ hasText: 'Finalización anticipada' }).waitFor();
  cases.push({ caso: 'Finalización anticipada: un paso, una decisión y una síntesis', aprobado: true });
  const repeated = await run('V2_REPEAT');
  assert.equal(repeated.terminacion, 'herramienta_repetida'); assert.equal(repeated.pasos.length, 2);
  await page.getByRole('status').filter({ hasText: 'Herramienta repetida' }).waitFor();
  cases.push({ caso: 'Repetición exacta detiene inspecciones sin consumir otro paso', aprobado: true });
  const failed = await run('V2_ERROR');
  assert.equal(failed.fase_error, 'herramienta'); assert.equal(failed.modo, 'degradado');
  await page.locator('.agent-trace').getByText('No completada', { exact: false }).waitFor();
  assert.equal(await page.locator('.agent-context').count(), 0);
  cases.push({ caso: 'Error contextual conserva decisión y respaldo local, sin resultado inventado', aprobado: true });
  // El proxy /agente pertenece al PR #50. Este candidato independiente
  // comprueba el laboratorio servido por la API, además del React vía Vite.
  await page.goto(`${api}/agente/demo`);
  await page.locator('#filename').fill('cuatro.py');
  await page.locator('#code').fill('nombre=input()\ncursor.execute("SELECT * FROM usuarios WHERE nombre = " + nombre)\n# V2_FOUR\n');
  await page.locator('#steps').selectOption('4');
  const fourthWire = page.waitForResponse(r => r.url().endsWith('/api/v1/agente/analizar'));
  await page.locator('#run').click();
  const fourthResponse = await fourthWire;
  assert.equal(fourthResponse.status(), 200);
  const fourth = await fourthResponse.json();
  const usage = JSON.parse((await fourthResponse.allHeaders())['x-codeguard-consumo-ia']);
  assert.equal(fourth.pasos.length, 4); assert.equal(fourth.decisiones.length, 3);
  assert.equal(usage.intentos, 4); assert.equal(usage.tokens_totales, 48);
  assert((await status()).propagacion.includes('cuarto_paso_en_sintesis'));
  await page.getByText('PASO 4 · ELEGIDO POR GEMINI', { exact: true }).waitFor();
  await fs.writeFile(`${folder}/V2_FOUR.json`, JSON.stringify({ respuesta: fourth, consumo_simulado: usage }, null, 2));
  cases.push({ caso: 'Laboratorio v2: cuarto paso llega a síntesis y agrega uso SDK simulado', aprobado: true });
  assert.deepEqual(errors, []); assert.deepEqual(external, []);
  cases.push({ caso: 'Sin errores del navegador ni solicitudes externas', aprobado: true });
  console.log(JSON.stringify({ estado: 'aprobado', casos: cases.length }));
} catch (error) {
  cases.push({ caso: String(error), aprobado: false }); throw error;
} finally {
  await fs.writeFile(`${folder}/navegador-agente-v2.json`, JSON.stringify({ proveedor: 'simulado', backend: 'real', rag: 'real', analisis_estatico: 'real', casos: cases }, null, 2));
  await browser?.close(); server.kill();
}
