# Presupuesto y aprobación de análisis ZIP/GitHub (candidato v1)

Estado: integrado mediante PR #45 en `9c97ca1c8797bad5bdfdf227dba119b7839d32c7`,
desactivado por defecto. No acredita activación pública ni cierre académico.
Base inicial: `605d142ff8f643d755689e257c649e0a9e79a8ea`.
Véase la [revisión frontend y trazabilidad](29-revision-frontend-agente-presupuesto.md).

## Finalidad

Presentar archivos y máximo de intentos reales al proveedor (incluidos reintentos) antes de consumir Gemini. Aprobar permite analizar exclusivamente la instantánea preparada. Es independiente de autorizar la descarga de una copia corregida.

No se estiman dólares ni tokens: un intento no tiene precio fijo y el consumo real puede ser menor, por abstención RAG o fallo del proveedor. El plazo es cooperativo: verifica tiempo entre fases y antes/después de llamadas; no interrumpe forzosamente tareas locales en curso.

## Contrato v1

| Ruta POST | Entrada | Efecto |
|---|---|---|
| `/api/v1/proyectos/previsualizar/zip` | Multipart `archivo` | Valida ZIP y guarda instantánea; cero llamadas a Gemini |
| `/api/v1/proyectos/previsualizar/github` | JSON `url` | Lector GitHub seguro, guarda contenidos; GitHub sí se consulta, Gemini no |
| `/api/v1/proyectos/{presupuesto_id}/decision` | JSON `decision`, `confirmar`, `sha256_manifiesto` | Aprueba análisis o rechaza sin consumir |

La aprobación requiere `decision: "aprobar"`, `confirmar: true` (booleano estricto) y el hash recibido. Rechazar exige `decision: "rechazar"`, `confirmar: false`. Campos adicionales se rechazan. Los identificadores y hashes proceden de la previsualización del servidor; no son valores inventados.

Previsualización: `version: "1"`, `presupuesto_id`, `estado: "pendiente_confirmacion"`, `tipo`, `origen`, `sha256_entrada`, `archivos`, `total_archivos`, `presupuesto`, `sha256_manifiesto`, `caduca_en` ISO UTC. Cada archivo: `archivo`, `caracteres`, `sha256`. Presupuesto: `modelo`, `analisis_previstos`, `intentos_por_analisis`, `max_intentos_proveedor`, `plazo_cooperativo_segundos`. No devuelve el código completo.

Aprobación finalizada: `version`, `presupuesto_id`, `sha256_manifiesto`, `estado: "finalizado"`, `resultado`. Este último conserva el contrato ZIP/GitHub: `archivo_zip` o `repositorio`, `estado`, `total_archivos`, `informes`. La interfaz comprueba identidad, hash, nombres y cantidad antes de normalizar el informe.

Rechazo: `version`, `presupuesto_id`, `estado: "rechazado"`. No genera informe ni consulta Gemini.

## Integridad y autorización

- Cookie aleatoria HttpOnly, SameSite=Strict; Secure con la configuración HTTPS de producción, alcance `/api/v1/proyectos`. Solo se guarda su hash.
- Frontend y API en el mismo origen, o mediante el proxy Vite. No se habilita CORS con credenciales.
- SHA-256 de entrada: bytes del ZIP o URL recortada UTF-8. Cada contenido UTF-8 tiene hash propio. GitHub autoriza los contenidos recuperados: al aprobar no se descarga otra vez una rama mutable.
- Hash del JSON canónico del núcleo `{tipo, origen, sha256_entrada, archivos, total_archivos, presupuesto}`: claves ordenadas, sin espacios y Unicode sin escapar. Los archivos mantienen su orden.
- El hash detecta cambios; la autorización depende también de sesión y estado del servidor. Modificar JSON no permite fijar otro presupuesto.
- Cambiar modelo, intentos o plazo exige revisar una nueva propuesta.
- Casilla inicialmente desmarcada. Cambiar entrada o modo elimina el consentimiento y solicita rechazo de la propuesta pendiente. Si esa notificación falla, no se envía aprobación y la propuesta caduca en servidor.
- Después de aprobar, «Dejar de esperar» solo interrumpe al navegador; el servidor puede continuar dentro de lo autorizado. No promete revocar llamadas ya iniciadas.

## Límites y persistencia

Lectores existentes: hasta cinco Python y 12.000 caracteres combinados; ZIP hasta 5 MB, rutas seguras, UTF-8, sin binarios. Estimación: `min(archivos × intentos configurados, 15)`, hasta tres intentos por archivo y plazo máximo 150 s reducible por configuración.

SQLite junto a la base de correcciones: `presupuestos.sqlite3`, permisos 0600 y `secure_delete`. Contiene código temporal en texto en el volumen; se elimina lógicamente al finalizar/rechazar/fallar o purgar. No equivale a borrado garantizado en respaldos del almacenamiento.

Pendiente: 300 s. Reserva de ejecución: 240 s; vencida, no publica resultado ni permite reutilizar autorización. Resultado idempotente: 300 s después de terminar. Máximo 100 registros globales y cinco por sesión, incluidos finalizados/rechazados hasta caducar. Purga al crear y cada 60 s cuando está activo. Transacciones cortas, sin red ni análisis dentro de ellas.

| Situación | Respuesta |
|---|---|
| Función desactivada | Nuevas rutas 404; anteriores conservadas |
| Otra sesión o inexistente | 404 |
| Caducada antes de purgar | 410 |
| Hash/configuración cambiados; decisión contraria; ya en curso | 409 |
| Consentimiento inválido o campos extra | 422 |
| Cupo temporal agotado | 429 |
| Ruta anterior con proyecto válido y función activa | 428: requiere presupuesto |
| Repetir aprobación finalizada | Mismo resultado, sin generar otra vez |
| Repetir rechazo | Idempotente, sin consumo |
| Fallo tras reservar | Autorización consumida; repetir no regenera |

Concurrencia y limitador ponderado global siguen siendo por proceso; SQLite protege la exclusividad de cada autorización. Revisar límites compartidos antes de múltiples réplicas.

## Activación coordinada

Predeterminados: `PROJECT_BUDGET_ENABLED=0`, `VITE_PROJECT_BUDGET_ENABLED=0`. En integración activar ambos a `1`, reiniciar backend y reconstruir frontend. Vite lee variables al arrancar/build: cambiarlas después no modifica el bundle. El Dockerfile actual no activa el flag en su fase de compilación; la activación pública necesita configurar y revisar ese build explícitamente, además del runtime.

Backend activo: proyectos válidos enviados a rutas anteriores reciben 428 antes de Gemini. Frontend activo/backend apagado: recibe 404 y no elude la aprobación usando una ruta anterior. No activar un solo lado. Demo conserva simulación local.

## Verificación

- Backend: `cd backend` y `python -m pytest tests/test_presupuesto_proyectos.py -q`. FastAPI/SQLite reales, analizador sustituido, sin red.
- Frontend: `cd frontend` y `npm test`, `npm run lint`, `npm run build`. Contrato y render inicial, no equivalen a prueba interactiva.
- Navegador: desde raíz con dependencias y corpus ingerido, `python qa/run_project_budget_browser.py --output tmp/http-presupuesto`. Requiere Playwright aislado y `PLAYWRIGHT_MODULE_PATH` a su `index.mjs`, más Chromium. Gemini y GitHub simulados; FastAPI, SQLite, RAG y Ruff/Bandit reales.
- CI ejecuta el navegador y adjunta JSON, capturas y logs en el artefacto de integración. Comprobar resultados antes de declarar aprobada la integración visual. No se adjuntan bases SQLite ni ZIP temporales.

Registro histórico del candidato inicial: 383 backend y 100 frontend aprobadas;
24 HTTP omitidas sin servidor. Otras 24 QA/evaluador aprobaron. Lint/build correctos.
Chromium no estuvo disponible en aquella corrida. La posterior
[evidencia integrada](evidencias/semana-4/integracion-agente-presupuesto-20261106/README.md)
registra nueve escenarios de navegador del presupuesto aprobados. Ninguna de
estas pruebas evalúa Gemini real. Persiste la advertencia de tamaño del bundle.

Compatibilidad HTTP local adicional: 24/24 escenarios con análisis estático aprobados, RAG y Ruff/Bandit reales; proveedor Gemini y API GitHub simulados. Se conservan informes y logs en `tmp/http-presupuesto-compat-estatico-2/` (temporales locales, no producción).
