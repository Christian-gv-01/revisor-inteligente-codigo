# Instalación automatizada desde checkout limpio

Referencia instalada: `384ffafba3b10886751260c15a944e2b24f110ab`. Prueba del 6 de noviembre de 2026,
ejecutada con asistencia de Codex para Ronald. No es una instalación realizada
por un integrante nuevo ni un ensayo oral del equipo.

Inicio local: 2026-11-06T19:02:20.562725-05:00. Fin local: 2026-11-06T19:08:05.778310-05:00.
Preparación: **313.656 s**. Smoke: **11.624 s**.
Total de pared: **345.216 s**, incluida la pausa entre ambos.
El checkout procede de objetos Git locales, no de una nueva descarga de GitHub.

| Paso | Segundos medidos | Salida |
|---|---:|---:|
| 01-checkout | 1.081 | 0 |
| 02-venv | 14.583 | 0 |
| 03-backend | 257.225 | 0 |
| 04-frontend | 18.625 | 0 |
| 05-build | 7.764 | 0 |
| 06-ingesta | 9.36 | 0 |
| 07-pip-check | 4.724 | 0 |
| Arranque API/frontend, AST y Demo | 11.624 | 0 |

## Resultado y alcance

Venv y node_modules nuevos, dependencias instaladas según requirements/lockfile,
React compilado, índice RAG nuevo y pip check sin conflictos. API /health y
frontend respondieron 200. Previsualización AST devolvió inspección local y
tres pasos. La interfaz completó el análisis Demo y mostró Exportar JSON, sin
errores JavaScript. El navegador bloqueó conexiones fuera de localhost.
Se cerraron solo los servidores y navegador creados para esta prueba.

Archivos: [comandos y tiempos](resultado.json), [smoke](smoke.json),
[navegador Demo](demo.json), [captura](demo-checkout-limpio.png),
[compatibilidad de paquetes](07-pip-check.txt), [build](05-build.txt),
[ingesta](06-ingesta.txt) y [procedencia/hashes](resumen.json).

## Dificultades y límites reales

- El README pide Python 3.13 y Node 22; este equipo usó Python 3.12.14 y Node
  24.17.0. No se instaló otra versión del sistema ni se cambiaron dependencias.
- Se reutilizaron cachés de pip/npm y modelo de embeddings. No es un equipo vacío.
- Backend consumió 257.225 s, la mayor etapa de instalación.
- Build mantiene la advertencia de bundle mayor de 500 kB.
- Se usó directamente el Python del venv; no se requirió modificar política
  de PowerShell para activar el entorno.
- Sin clave ni llamadas a Gemini; salud y Demo no acreditan calidad generativa.
- La prueba no usó Docker, no verificó Railway ni realizó despliegues.
- El tiempo automático no cierra el requisito de instalación humana independiente
  en diez minutos. Ese registro sigue pendiente en la guía de instalación.

## Sincronización de la rama entregada

Se conservan commits anteriores y se integra `384ffaf` mediante merge `5b72b55`.
Las 40 pruebas del comparador/contrato aprobaron en el entorno existente de QA,
separado del venv recién instalado: [registro](sincronizacion-evaluador-local.txt).
El primer intento tuvo tres errores al crear temporales del sandbox; la repetición
con `--basetemp=tmp/pytest-sync-384ffaf` aprobó sin cambiar el código del evaluador.
No se ejecutó la comparación real de veinte casos.
