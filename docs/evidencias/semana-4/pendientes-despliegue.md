# Dependencias para cerrar QA público

Actualización: 5 de noviembre de 2026, America/Bogota.

## Estado vigente

- La rama QA está publicada y el PR #12 está abierto en borrador. La autenticación Git ya se resolvió con la cuenta confirmada por el usuario.
- Railway tiene URL HTTPS pública: https://revisor-inteligente-codigo-production.up.railway.app . La primera matriz pública obtuvo 24/26; conservar `pruebas-publicas.json` como evidencia de esa ejecución.
- Falta verificar en producción la corrección de los errores 422 y el análisis real que devolvió 502. Los resultados de una repetición se guardan por separado; no se reemplaza la evidencia anterior.
- El responsable indicó que no puede reiniciar el servicio. No se dispone en esta sesión de una herramienta de administración de Railway. Falta evidencia del evento de reinicio, volumen y recuperación sin reingesta.
- El estado actual, la revisión de los aportes de Frontend y las evidencias posteriores se detallan en `../../12-cierre-qa-entrega4.md`.

Las secciones históricas siguientes explican los bloqueos iniciales; no describen el estado vigente de autenticación ni de disponibilidad de la URL.

## Confirmación inicial del equipo — histórico del 4 de noviembre

El usuario compartió el reporte del responsable de Frontend y Evaluación. Ese reporte indica que sigue pendiente definir la plataforma, obtener la URL pública del backend y comprobar la integración en producción. No se dispone de una URL confirmada en esta revisión.

Las métricas RAG comunicadas por ese integrante pertenecen a su ejecución. No reemplazan ni se mezclan con las evidencias históricas o las pruebas locales de esta rama.

## Información necesaria del responsable de despliegue

- URL HTTPS de la aplicación/API y revisión Git desplegada.
- Plataforma y servicio que ejecutan el contenedor.
- Volumen persistente montado en `/data` y `CHROMA_PATH=/data/chroma`.
- Gemini configurado en el servidor, sin compartir la clave con QA.
- Coordinación del reinicio del contenedor y evidencia del evento.

Con esos datos, QA ejecuta los escenarios públicos, captura las citas previas, solicita el reinicio al responsable y compara las citas posteriores. El frontend realiza sus propias verificaciones de interfaz y exportación.

## Comprobaciones iniciales — histórico

- Se intentó publicar la rama con autenticación no interactiva. Git indicó que no podía obtener el usuario de GitHub; la publicación continúa sin confirmar.
- Se inició Docker Desktop para intentar la construcción. El motor terminó durante el arranque; `docker compose build` no pudo conectarse al motor Linux.
- WSL 2 está configurado y la distribución `docker-desktop` aparece detenida.
- El log de Docker identifica un fallo al inicializar el gestor de inferencia sobre el socket local `dockerInference`: el sistema no puede acceder al archivo. La causa raíz no se ha establecido. No se borraron datos ni se restableció Docker.

Por lo tanto, no se generaron resultados de build Docker, reinicio ni pruebas públicas en esta continuación.

## Alcance de la verificación de citas

El script de citas demuestra que siguen disponibles referencias tras el reinicio coordinado. Por sí solo, encontrar los mismos IDs no demuestra que el volumen se conservó: la ingesta podría reconstruirlos. La evidencia debe incluir el volumen, el evento de reinicio y el log de recuperación del índice sin nueva ingesta. Para una prueba fuerte de persistencia, conviene además verificar una marca única que el arranque no regenere.
