import path from 'node:path';
import { pathToFileURL } from 'node:url';
import fs from 'node:fs/promises';
import { spawn } from 'node:child_process';
import assert from 'node:assert/strict';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE_PATH ? pathToFileURL(process.env.PLAYWRIGHT_MODULE_PATH).href : 'playwright');
const api = process.env.CODEGUARD_DEV_API_TARGET;
assert(api && new URL(api).hostname === '127.0.0.1', 'Solo servidor fixture en loopback');
assert.equal((await (await fetch(`${api}/__budget_fixture__/status`)).json()).proveedor, 'simulado');
const folder = process.argv[2];
const origin = 'http://127.0.0.1:5192';
const server = spawn(process.execPath, ['node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '5192', '--strictPort'], {
  cwd: path.resolve('frontend'), env: { ...process.env, VITE_PROJECT_BUDGET_ENABLED: '1', VITE_API_BASE_URL: '' }, stdio: 'ignore',
});
let browser;
const cases = [];
try {
  for (let n = 0; n < 80; n++) {
    try { if ((await fetch(origin)).ok) break; } catch { /* inicio local */ }
    await new Promise(r => setTimeout(r, 100));
  }
  browser = await chromium.launch({ headless: true, executablePath: process.env.CODEGUARD_BROWSER_PATH });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1080 } });
  await context.route('**/*', route => new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort());
  const page = await context.newPage();
  const calls = async () => (await (await fetch(`${api}/__budget_fixture__/status`)).json()).llamadas;
  await page.goto(origin);
  await page.getByRole('button', { name: 'API real', exact: true }).click();
  await page.getByRole('button', { name: 'GitHub', exact: true }).click();
  await page.getByLabel('Repositorio público de GitHub').fill('https://github.com/qa-fixture/proyecto');
  const preview = async kind => {
    const response = page.waitForResponse(r => r.url().endsWith(`/proyectos/previsualizar/${kind}`));
    await page.getByRole('button', { name: 'Revisar presupuesto', exact: true }).click();
    const r = await response; assert.equal(r.status(), 200);
    await page.getByRole('heading', { name: 'Revisa el presupuesto del proyecto' }).waitFor();
    const proposal = await r.json();
    const panel = page.locator('.project-budget');
    assert.equal(await panel.locator('li').count(), proposal.total_archivos);
    for (const file of proposal.archivos) {
      await panel.getByText(`${file.archivo} · ${file.caracteres} caracteres`, { exact: true }).waitFor();
    }
    const b = proposal.presupuesto;
    await panel.getByText(`${b.analisis_previstos} análisis previstos · máximo ${b.max_intentos_proveedor} intentos al proveedor, incluidos reintentos.`, { exact: true }).waitFor();
    assert((await panel.textContent()).includes(`Plazo cooperativo: ${b.plazo_cooperativo_segundos} s`));
    assert(!(await consent().isChecked()));
    assert(await approve().isDisabled());
    return proposal;
  };
  const approve = () => page.getByRole('button', { name: 'Aprobar presupuesto y analizar', exact: true });
  const consent = () => page.getByRole('checkbox', { name: 'Autorizo analizar esta instantánea dentro del presupuesto indicado.' });
  await preview('github');
  assert(await approve().isDisabled()); assert.equal(await calls(), 0);
  cases.push({ caso: 'Previsualización real sin Gemini y consentimiento desmarcado', aprobado: true });
  await page.screenshot({ path: `${folder}/presupuesto-escritorio.png`, fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  assert(await page.locator('.project-budget').evaluate(el => el.scrollWidth <= el.clientWidth + 1));
  await page.screenshot({ path: `${folder}/presupuesto-movil.png`, fullPage: true });
  cases.push({ caso: 'Presupuesto legible sin desbordamiento en móvil', aprobado: true });
  await page.setViewportSize({ width: 1440, height: 1080 });
  const rejection = page.waitForResponse(r => r.url().includes('/proyectos/') && r.url().endsWith('/decision'));
  await page.getByRole('button', { name: 'Rechazar presupuesto', exact: true }).click();
  assert.equal((await rejection).status(), 200); assert.equal(await calls(), 0);
  await page.locator('.project-budget').waitFor({ state: 'detached' });
  cases.push({ caso: 'Rechazo desde interfaz sin consumo', aprobado: true });
  const p = await preview('github');
  await consent().check();
  const approved = page.waitForResponse(r => r.url().includes(p.presupuesto_id));
  await approve().click(); assert.equal((await approved).status(), 200);
  await page.locator('.project-budget').waitFor({ state: 'detached' });
  const afterApproval = await calls(); assert(afterApproval > 0);
  cases.push({ caso: 'Aprobación real con RAG y Ruff/Bandit reales; Gemini simulado', aprobado: true });
  const body = { decision: 'aprobar', confirmar: true, sha256_manifiesto: p.sha256_manifiesto };
  assert.equal((await page.request.post(`${origin}/api/v1/proyectos/${p.presupuesto_id}/decision`, { data: body })).status(), 200);
  assert.equal(await calls(), afterApproval);
  cases.push({ caso: 'Repetición HTTP idempotente sin llamadas adicionales', aprobado: true });
  await preview('github');
  await consent().check();
  await page.getByLabel('Repositorio público de GitHub').fill('https://github.com/qa-fixture/parcial');
  await page.locator('.project-budget').waitFor({ state: 'detached' });
  assert.equal(await calls(), afterApproval);
  cases.push({ caso: 'Cambiar entrada invalida consentimiento sin analizar', aprobado: true });
  await page.getByLabel('Repositorio público de GitHub').fill('https://github.com/qa-fixture/proyecto');
  const expired = await preview('github');
  assert.equal((await fetch(`${api}/__budget_fixture__/${expired.presupuesto_id}/caducar`, { method: 'POST' })).status, 200);
  await consent().check();
  const expiry = page.waitForResponse(r => r.url().includes(expired.presupuesto_id));
  await approve().click(); assert.equal((await expiry).status(), 410);
  await page.getByRole('alert').filter({ hasText: 'caducó' }).waitFor();
  await page.getByRole('alert').getByText('Solicitud no completada', { exact: true }).waitFor();
  assert.equal(await page.getByRole('alert').getByText('Integración pendiente', { exact: true }).count(), 0);
  assert.equal(await calls(), afterApproval);
  cases.push({ caso: 'Caducidad del servidor 410 sin consumo adicional', aprobado: true });
  await page.getByRole('button', { name: 'Proyecto .zip', exact: true }).click();
  await page.getByLabel('Seleccionar archivo ZIP').setInputFiles(path.join(folder, 'caso.zip'));
  const zip = await preview('zip'); assert.equal(zip.total_archivos, 2);
  assert.equal(await calls(), afterApproval); await consent().check();
  const zipResult = page.waitForResponse(r => r.url().includes(zip.presupuesto_id));
  await approve().click(); assert.equal((await zipResult).status(), 200);
  await page.locator('.project-budget').waitFor({ state: 'detached' });
  assert.equal(await calls(), afterApproval + 2);
  cases.push({ caso: 'ZIP de dos archivos: ambas consultas solo después de aprobar', aprobado: true });
  const afterZip = await calls();
  // Nueva sesión aislada para respetar el cupo de propuestas de cada sesión.
  await context.clearCookies();
  await preview('zip');
  const zipRejection = page.waitForResponse(r => r.url().includes('/proyectos/') && r.url().endsWith('/decision'));
  await page.getByRole('button', { name: 'Rechazar presupuesto', exact: true }).click();
  assert.equal((await zipRejection).status(), 200);
  await page.locator('.project-budget').waitFor({ state: 'detached' });
  assert.equal(await calls(), afterZip);
  cases.push({ caso: 'Rechazo ZIP desde interfaz sin consumo adicional', aprobado: true });
  const expiredZip = await preview('zip');
  assert.equal((await fetch(`${api}/__budget_fixture__/${expiredZip.presupuesto_id}/caducar`, { method: 'POST' })).status, 200);
  await consent().check();
  const expiredZipResult = page.waitForResponse(r => r.url().includes(expiredZip.presupuesto_id));
  await approve().click();
  assert.equal((await expiredZipResult).status(), 410);
  await page.getByRole('alert').filter({ hasText: 'caducó' }).waitFor();
  assert.equal(await calls(), afterZip);
  cases.push({ caso: 'ZIP caducado devuelve 410 desde interfaz sin ejecutar', aprobado: true });
  await page.screenshot({ path: `${folder}/presupuesto-zip-caducado.png`, fullPage: true });
  // Presupuesto anterior con entrada modificada no se reutiliza.
  const tampered = await preview('zip');
  assert.equal((await page.request.post(`${origin}/api/v1/proyectos/${tampered.presupuesto_id}/decision`, {
    data: { decision: 'aprobar', confirmar: true, sha256_manifiesto: '0'.repeat(64) },
  })).status(), 409);
  assert.equal(await calls(), afterZip);
  cases.push({ caso: 'Manifiesto alterado rechazado con 409', aprobado: true });
  // Reloj del navegador: comprobar también el bloqueo visual al vencer la propuesta.
  await page.clock.install();
  await page.clock.fastForward(Math.max(0, Date.parse(tampered.caduca_en) - Date.now()) + 1500);
  await page.getByRole('alert').filter({ hasText: 'El presupuesto caducó' }).waitFor();
  assert(await approve().isDisabled()); assert(await consent().isDisabled());
  assert.equal(await calls(), afterZip);
  cases.push({ caso: 'Vencimiento visible bloquea consentimiento y aprobación sin ejecutar', aprobado: true });
  console.log(JSON.stringify({ estado: 'aprobado', casos: cases.length }));
} catch (error) {
  cases.push({ caso: String(error), aprobado: false });
  throw error;
} finally {
  await fs.writeFile(`${folder}/navegador-presupuesto.json`, JSON.stringify({ proveedor: 'simulado', github: 'simulado', backend: 'real', sqlite: 'real', rag: 'real', casos: cases }, null, 2));
  await browser?.close(); server.kill();
}
