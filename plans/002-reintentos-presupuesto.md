# Reintentos 429, plazo compartido y reserva de propuestas

Base: `2cb3e823e53be73b2546338c69eb4d498ee00233`, integración autorizada
exclusivamente del PR #40. Rama nueva: `codex/reintentos-presupuesto`.
Los PR #39/#41 y la política severidad × confianza quedan fuera del alcance.

## Requisitos y diseño

Conservar rutas, cuerpos JSON, estados públicos y pesos del limitador propio.
Un 429 del limitador HTTP sigue rechazando antes del proveedor, con Retry-After.
Un 429 de Gemini admite reintento acotado y termina como 503 si agota intentos;
un plazo agotado termina como 504 o conserva el resultado parcial existente.

Un presupuesto monotónico compartido por solicitud cuenta cada intento real a
Gemini. Incluye esperas y llamadas sucesivas del agente/proyecto, sin reiniciar
el reloj por archivo. Límites máximos: 45 s por análisis directo/propuesta,
150 s por agente/proyecto, por debajo de los 60/180 s actuales del navegador.
Un intento usa min(timeout configurado, tiempo restante). Se desactivan los
reintentos internos del SDK (attempts=1) para evitar multiplicación de llamadas.
La política de aplicación permite dos intentos por llamada lógica (configurable
1..3), espera exponencial desde 0,6 s y Retry-After numérico/fecha válidos. Nunca
acortar una espera del proveedor para encajar: si no cabe, finalizar sin otra llamada.
Una respuesta tardía no se publica como éxito. No se promete interrumpir código
Python sin cooperación: se comprueba el plazo en límites de fases y se acotan
transportes/subprocesos; la concurrencia permanece reservada hasta terminar el trabajo.

Reservar cupo global y por sesión en SQLite antes de generar. Contar propuestas
vigentes y generaciones reservadas en una transacción BEGIN IMMEDIATE corta;
no mantener bloqueos durante Gemini. Reservas sin código, con ID impredecible y
caducidad, recuperables tras caída del proceso. Finalizar con consumo atómico de
la reserva e inserción de propuesta; liberar al fallar, y rechazar una finalización
tardía de una reserva vencida. Mantener decisiones, hashes, TTL e idempotencia.

## Tareas y verificación

- [x] Reproducir los defectos con regresiones antes del código productivo.
- [x] Presupuesto/contexto/reintento común; pruebas con reloj y sueño simulados,
  429→éxito, agotamiento, Retry-After, espera creciente, errores no reintentables,
  plazo entre etapas e intentos del SDK sin duplicación.
- [x] Reserva atómica de cupo; pruebas concurrentes de último cupo, cupo lleno
  sin generar, fallo/validación/almacenamiento y recuperación de reservas vencidas.
- [x] Integrar en síntesis, planificador, correcciones y middleware sin tocar
  priorización. Probar aislamiento entre solicitudes, propagación a hilos y
  liberación de concurrencia tras error; mantener fallback estático/traza.
- [x] Acotar fases GitHub/estático por el plazo restante y documentar límites
  cooperativos. No ampliar las confirmaciones ZIP/GitHub en este bloque.
- [x] Ejecutar backend/QA/eval, frontend lint/build/tests e integración HTTP
  con/sin estático; revisar independientemente y registrar evidencias.
- [x] Publicar otro PR en borrador, sin fusionarlo ni iniciar despliegue.

Comandos: `backend/.venv/Scripts/python.exe -m pytest` desde raíz usando
`backend/tests` con cwd backend; `-m pytest qa eval -q` desde raíz;
`npm test`, `npm run lint`, `npm run build` desde frontend;
`eval/run_integration.py --static-analysis --output tmp/reintentos-http-estatico`
y variante sin estático en carpeta nueva. No llamadas reales a IA en estas pruebas.

## Registro

PR40 integrado con SHA esperado; seis workflows push de main comprobados success.
Railway deployment 7611418000 corresponde al mismo SHA; inicialmente in_progress.
Salud pública 200 no identifica por sí sola el SHA desplegado. Registrar su estado
final por separado y no atribuir la versión nueva al /health genérico.

Estado final de la base: Railway success a las 21:40:30 UTC del 6 de noviembre,
según registro del deployment GitHub; seis workflows push success. Reserva
implementada con pruebas primero y revisión independiente sin bloqueos. Revisión
general aprobada tras corregir plazo en el retorno RAG sin fuentes. Validación
local final: 364 backend, 23 QA/eval y una omisión; frontend91; HTTP24/24 y19/19.
La primera CI detectó dependencia accidental del motor estático en HTTPX/SDK.
Se corrigió con excepción estándar e importación diferida de Google; regresión
en proceso nuevo primero fallida y después aprobada. Revisión independiente
del ajuste: 63 pruebas focalizadas aprobadas. PR de entrega: #42 en borrador.
