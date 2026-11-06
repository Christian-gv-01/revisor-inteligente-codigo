# Frontend de producto — pruebas locales

Fecha: 6 de noviembre de 2026. Rama local `feature/entrega4-frontend-producto`.
Código base del producto `65675e2`; documentación previa `578adee`.

Comandos ejecutados desde `frontend/`: `npm test -- --reporter=dot`, `npm run lint`
y `npm run build`. Resultado: 91 aprobadas, 17 HTTP omitidas; lint y build correctos.
Advertencia existente: bundle superior a 500 kB.

[navegador.json](navegador.json) registra ocho escenarios de Edge headless local.
Se utilizó la página `frontend/tests/correction-preview.html`, con respuestas
simuladas y conexiones externas bloqueadas. No hubo peticiones externas.

- [Previsualización de escritorio](previsualizacion-escritorio.png).
- [Previsualización móvil](previsualizacion-movil.png).
- [Flujo integrado en la página principal Demo](aplicacion-demo.png).
- [Primera corrida de siete casos del componente](navegador-componentes.json).

La prueba verificó descarga bloqueada sin consentimiento, cancelación y rechazo,
reapertura con casilla desmarcada, copia de contenido exacto bajo nombre nuevo,
respuesta alterada rechazada, cancelación durante una respuesta tardía, nueva
entrada y ausencia de desbordamiento horizontal a 390 px. Los casos agrupados
figuran con su alcance en el JSON.

No acredita aprobación real del backend, despliegue en Railway ni calidad de
Gemini. El código del ejemplo solo se mostró y descargó como texto; no se ejecutó.

## Reproducir la interacción

Ejecutor: [frontend/tests/correction-browser.mjs](../../../../frontend/tests/correction-browser.mjs).
Requiere Node y Playwright disponible en el entorno de pruebas. Si Playwright no
está instalado en el proyecto, indicar su `index.mjs` mediante
`PLAYWRIGHT_MODULE_PATH`; `CODEGUARD_BROWSER_PATH` admite un ejecutable Chromium/Edge
de pruebas. No se agregaron dependencias de runtime al producto.

Desde la raíz: `node frontend/tests/correction-browser.mjs tmp/correction-browser`.
El script inicia su propio Vite en `127.0.0.1:5178`, usa un perfil de navegador
aislado, bloquea otros hosts y cierra sus procesos al finalizar. No reutiliza una
sesión personal del navegador. No usar una URL de Railway para estos escenarios.
