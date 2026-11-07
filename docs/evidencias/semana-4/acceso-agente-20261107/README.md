# Acceso al agente desde el frontend

Ronald Yépez · 7 de noviembre de 2026. Base integrada PR #48:
`467d00e0d56a98cd758f382a5c713737eb490845`.
Rama independiente: `feature/frontend-acceso-agente`.

## Observación y ajuste

La pantalla principal ya llama a `/api/v1/agente/analizar` con herramientas v2
para código y `.py` en modo API real. Esa conexión no se implementa nuevamente.
Faltaba descubrir el laboratorio `/agente/demo` desde la interfaz: había que
conocer o compartir su URL. Además, Vite solo reenviaba `/api`, por lo que abrir
`/agente/demo` en su origen local podía mostrar React en vez del laboratorio.

Se añade un bloque visible que explica el agente integrado y abre el laboratorio
en otra pestaña, conservando el editor. El enlace usa `VITE_API_BASE_URL` si está
configurada; con base vacía conserva el mismo origen. Vite reenvía `/agente` al
mismo backend que `/api`. Abrir el enlace no transmite código ni inicia análisis.

El laboratorio continúa siendo una pantalla independiente servida por Backend,
no un componente React embebido. ZIP/GitHub conservan revisión por archivo, fuera
del agente v2. Esta propuesta cubre acceso y explicación del recorrido; cualquier
petición adicional de unificar pantallas requiere acordar su alcance con Christian.

## Comprobaciones

- `npm test`: **133 aprobadas y 24 omitidas** por falta de configuración HTTP.
  No se contabilizan las omitidas como aprobadas.
- `npm run lint`: aprobado.
- `npm run build`: aprobado, con advertencia preexistente de bundle >500 kB.
- Navegador Edge headless, Vite y FastAPI locales: **4 comprobaciones aprobadas**,
  sin errores JavaScript. Véase [resultado estructurado](navegador.json).
- [Escritorio 1440 px](acceso-escritorio.png) y [móvil 390 px](acceso-movil.png)
  inspeccionados visualmente. Acceso visible y sin desbordamiento horizontal móvil.

El navegador comprobó abrir el laboratorio real mediante proxy sin iniciar
análisis, ejecutar AST contra FastAPI real, enviar la solicitud v2 y mostrar
su traza en React, y presentar el acceso en móvil. La respuesta de análisis v2
se simuló con el contrato publicado; **no se llamó a Gemini**. Solo AST consultó
el backend real. No se validó Railway ni se realizaron despliegues o cambios de flags.

## Reproducir el navegador

Iniciar Backend en `127.0.0.1:8000` y Vite en `127.0.0.1:5173`, con base API vacía
y sin activar flags. Desde la raíz del repositorio, con Playwright disponible:

```powershell
node frontend/tests/agent-access-browser.mjs http://127.0.0.1:5173 tmp/acceso-agente
```

Si Playwright no está en node_modules, `PLAYWRIGHT_MODULE_PATH` admite la ruta
absoluta de su módulo. `CODEGUARD_BROWSER_PATH` permite indicar el ejecutable del
navegador. Son variables opcionales de pruebas, sin secretos ni cambios al producto.
El script bloquea conexiones fuera de localhost e intercepta el análisis con el
fixture del contrato. Cerrar los servidores propios al terminar.

El commit probado se identifica en el PR de esta rama. La base anterior identifica
el punto de partida, no una versión ya desplegada de este ajuste.
