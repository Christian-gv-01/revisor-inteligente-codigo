import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import assert from 'node:assert/strict';

// Ejecutar desde la raíz con Vite y FastAPI locales ya iniciados.
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE_PATH
  ? pathToFileURL(process.env.PLAYWRIGHT_MODULE_PATH).href : 'playwright');
const [origin, folder] = process.argv.slice(2);
assert(origin && new URL(origin).hostname === '127.0.0.1', 'Solo localhost');
assert(folder, 'Indicar carpeta de evidencias');
await fs.mkdir(folder, { recursive: true });
const request = JSON.parse(await fs.readFile('docs/contrato-agente-v2/01-solicitud-contexto-y-referencia.json', 'utf8'));
const response = JSON.parse(await fs.readFile('docs/contrato-agente-v2/04-respuesta-contexto-y-referencia.json', 'utf8'));
const browser = await chromium.launch({ headless: true, executablePath: process.env.CODEGUARD_BROWSER_PATH });
const errors = [], posts = [], cases = [];
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  await context.route('**/*', async route => {
    const req = route.request(), url = new URL(req.url());
    if (url.hostname !== '127.0.0.1') return route.abort();
    if (req.method() === 'POST') {
      posts.push(url.pathname);
      if (url.pathname === '/api/v1/agente/analizar') {
        assert.deepEqual(req.postDataJSON(), request);
        return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(response) });
      }
      if (url.pathname !== '/api/v1/agente/previsualizar') return route.abort();
    }
    return route.continue();
  });
  context.on('page', page => page.on('pageerror', error => errors.push(error.message)));
  const page = await context.newPage();
  await page.goto(origin);
  const link = page.getByRole('link', { name: 'Abrir laboratorio del agente (nueva pestaña)', exact: true });
  assert.equal(await link.getAttribute('href'), '/agente/demo');
  await page.screenshot({ path: path.join(folder, 'acceso-escritorio.png') });
  const popupPromise = page.waitForEvent('popup');
  await link.click();
  const lab = await popupPromise;
  await lab.locator('#run').waitFor();
  assert.equal(new URL(lab.url()).pathname, '/agente/demo');
  assert.equal(posts.length, 0, 'Abrir la pantalla no inicia análisis');
  assert.equal(await page.getByRole('button', { name: 'Demo', exact: true }).getAttribute('aria-pressed'), 'true');
  cases.push('Enlace abre el laboratorio real mediante proxy, conserva editor y no inicia análisis');
  await lab.locator('#mode').selectOption('local');
  await lab.locator('#code').fill('x = 1\nprint(x)\n');
  const astResponse = lab.waitForResponse(r => r.url().endsWith('/api/v1/agente/previsualizar'));
  await lab.locator('#run').click();
  const ast = await astResponse;
  assert.equal(ast.status(), 200);
  assert.equal((await ast.json()).modo, 'inspeccion_local');
  await lab.locator('#output').waitFor({ state: 'visible' });
  cases.push('Laboratorio ejecuta inspección AST contra FastAPI real, sin Gemini');
  await lab.close();
  await page.getByRole('button', { name: 'API real', exact: true }).click();
  await page.getByRole('button', { name: 'Agente', exact: true }).click();
  await page.getByRole('button', { name: 'Archivo .py', exact: true }).click();
  await page.locator('input[type=file]').setInputFiles({ name: request.archivo, mimeType: 'text/x-python', buffer: Buffer.from(request.codigo) });
  await page.getByRole('button', { name: 'Analizar código', exact: true }).click();
  await page.locator('.agent-trace summary').click();
  await page.getByText('Ampliar contexto', { exact: true }).first().waitFor();
  cases.push('Revisor envía solicitud v2 y muestra traza del contrato simulado');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(origin);
  await link.waitFor();
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({ path: path.join(folder, 'acceso-movil.png') });
  cases.push('Acceso visible en móvil de 390 px sin desbordamiento horizontal');
  assert.equal(errors.length, 0);
  await fs.writeFile(path.join(folder, 'navegador.json'), JSON.stringify({ resultado: 'aprobado', casos: cases, errores_javascript: errors, peticiones_post: posts, gemini_real: false, alcance: 'Laboratorio y AST reales; respuesta del análisis principal simulada con fixture publicado' }, null, 2));
  console.log(JSON.stringify({ resultado: 'aprobado', casos: cases.length }));
} finally { await browser.close(); }
