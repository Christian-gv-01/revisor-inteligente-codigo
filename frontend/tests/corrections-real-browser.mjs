import path from 'node:path';
import { pathToFileURL } from 'node:url';
import fs from 'node:fs/promises';
import { spawn } from 'node:child_process';
import assert from 'node:assert/strict';

const { chromium } = await import(process.env.PLAYWRIGHT_MODULE_PATH ? pathToFileURL(process.env.PLAYWRIGHT_MODULE_PATH).href : 'playwright');
const api = process.env.CODEGUARD_DEV_API_TARGET;
assert(api && new URL(api).hostname === '127.0.0.1', 'Solo servidor fixture en loopback');
assert.equal((await fetch(`${api}/health`)).headers.get('X-Integration-Provider'), 'stub');
const out = process.argv[2]; await fs.mkdir(out, { recursive: true });
const origin = 'http://127.0.0.1:5186';
const server = spawn(process.execPath, ['node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '5186', '--strictPort'], {
  cwd: path.resolve('frontend'), env: { ...process.env, VITE_CORRECTIONS_API_ENABLED: '1', VITE_API_BASE_URL: '' }, stdio: 'ignore',
});
let browser;
const cases = [];
try {
  for (let n = 0; n < 80; n++) {
    try { if ((await fetch(origin)).ok) break; } catch { /* inicio */ }
    await new Promise(r => setTimeout(r, 100));
  }
  browser = await chromium.launch({ headless: true, executablePath: process.env.CODEGUARD_BROWSER_PATH });
  const context = await browser.newContext({ acceptDownloads: true, viewport: { width: 1440, height: 1000 } });
  const external = []; const errors = [];
  await context.route('**/*', route => {
    const u = new URL(route.request().url());
    if (u.hostname === '127.0.0.1') return route.continue();
    external.push(u.origin); return route.abort();
  });
  const page = await context.newPage(); const downloads = [];
  page.on('download', d => downloads.push(d)); page.on('pageerror', e => errors.push(e.message));
  const open = async () => {
    await page.goto(origin);
    await page.getByRole('button', { name: 'API real', exact: true }).click();
    await page.getByRole('button', { name: 'Analizar código', exact: true }).click();
    await page.getByRole('button', { name: 'Previsualizar propuesta', exact: true }).waitFor();
  };
  const preview = async () => {
    const response = page.waitForResponse(r => r.url().endsWith('/correcciones/previsualizar') && r.request().method() === 'POST');
    await page.getByRole('button', { name: 'Previsualizar propuesta', exact: true }).click();
    const r = await response; assert.equal(r.status(), 200); const p = await r.json();
    await page.getByLabel('Código propuesto', { exact: true }).waitFor();
    return p;
  };
  const decide = (p, d) => page.request.post(`${origin}/api/v1/correcciones/${p.propuesta_id}/decision`, {
    data: { decision: d, sha256_original: p.sha256_original, sha256_propuesto: p.sha256_propuesto },
  });
  await open(); const p = await preview();
  assert(await page.getByRole('button', { name: 'Confirmar y descargar copia', exact: true }).isDisabled());
  assert.equal(downloads.length, 0);
  await page.getByRole('checkbox').check();
  const downloadEvent = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Confirmar y descargar copia', exact: true }).click();
  const downloaded = await downloadEvent;
  assert.equal(await fs.readFile(await downloaded.path(), 'utf8'), p.codigo_propuesto);
  assert.equal(downloaded.suggestedFilename(), p.archivo_salida);
  cases.push({ caso: 'Previsualización y aprobación reales; contenido exacto; cookie same-origin', aprobado: true });

  await open(); const cancelProposal = await preview();
  const rejection = page.waitForResponse(r => r.url().includes(cancelProposal.propuesta_id) && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Cancelar corrección', exact: true }).click();
  assert.equal((await rejection).status(), 200); assert.equal(downloads.length, 1);
  cases.push({ caso: 'Rechazo real sin descarga', aprobado: true });

  await open(); const expired = await preview();
  assert.equal((await fetch(`${api}/__integration__/correcciones/${expired.propuesta_id}/caducar`, { method: 'POST' })).status, 200);
  await page.getByRole('checkbox').check();
  const expiry = page.waitForResponse(r => r.url().includes(expired.propuesta_id));
  await page.getByRole('button', { name: 'Confirmar y descargar copia', exact: true }).click();
  assert.equal((await expiry).status(), 410);
  await page.getByRole('alert').filter({ hasText: 'caducó' }).waitFor(); assert.equal(downloads.length, 1);
  cases.push({ caso: 'Caducidad 410 del backend real sin descarga', aprobado: true });

  await open(); const conflict = await preview();
  assert.equal((await decide(conflict, 'rechazar')).status(), 200);
  await page.getByRole('checkbox').check();
  const conflicting = page.waitForResponse(r => r.url().includes(conflict.propuesta_id));
  await page.getByRole('button', { name: 'Confirmar y descargar copia', exact: true }).click();
  assert.equal((await conflicting).status(), 409); assert.equal(downloads.length, 1);
  cases.push({ caso: 'Decisión contraria 409 desde la interfaz', aprobado: true });

  let notifyApproval = () => {};
  const reachedBackend = () => new Promise(resolve => { notifyApproval = resolve; });
  const delayApproval = async route => {
    if (route.request().postDataJSON().decision !== 'aprobar') return route.continue();
    try {
      const r = await route.fetch();
      assert.equal(r.status(), 200); notifyApproval();
      await new Promise(resolve => setTimeout(resolve, 700));
      await route.fulfill({ response: r });
    } catch { /* cliente canceló */ }
  };
  await page.route('**/correcciones/*/decision', delayApproval);
  await open(); await preview(); await page.getByRole('checkbox').check();
  const firstReached = reachedBackend();
  await page.getByRole('button', { name: 'Confirmar y descargar copia', exact: true }).click();
  await firstReached;
  await page.getByRole('button', { name: 'Cancelar corrección', exact: true }).click();
  await page.waitForTimeout(1000); assert.equal(downloads.length, 1);
  cases.push({ caso: 'Cancelar ante una respuesta tardía del backend impide descargar', aprobado: true });

  await open(); await preview(); await page.getByRole('checkbox').check();
  const secondReached = reachedBackend();
  await page.getByRole('button', { name: 'Confirmar y descargar copia', exact: true }).click();
  await secondReached;
  await page.getByRole('button', { name: 'Cargar ejemplo', exact: true }).click();
  await page.waitForTimeout(1000); assert.equal(downloads.length, 1);
  cases.push({ caso: 'Cambiar entrada descarta consentimiento y aprobación anterior', aprobado: true });
  await page.unroute('**/correcciones/*/decision', delayApproval);

  await open(); await preview();
  assert(!(await page.getByRole('checkbox').isChecked()));
  await page.screenshot({ path: path.join(out, 'confirmacion-http-escritorio.png'), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({ path: path.join(out, 'confirmacion-http-movil.png'), fullPage: true });
  cases.push({ caso: 'Original y propuesta reales en móvil sin desbordamiento', aprobado: true });
  assert.deepEqual(errors, []); assert.deepEqual(external, []);
  await fs.writeFile(path.join(out, 'navegador-confirmacion-http.json'), JSON.stringify({
    fecha_utc: new Date().toISOString(), casos: cases, errores: errors,
    proveedor_ia: 'simulado', backend: 'FastAPI y SQLite reales en loopback',
    navegador: 'Chromium headless', codigo_ejecutado: false, original_sobrescrito: false,
    nota: 'Se retuvieron respuestas reales para probar cancelación; no se sustituyeron cuerpos HTTP.',
  }, null, 2));
  console.log(JSON.stringify({ aprobadas: cases.length }));
} finally { await browser?.close(); server.kill(); }
