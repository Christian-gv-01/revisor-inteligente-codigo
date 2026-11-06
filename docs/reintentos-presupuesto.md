# Reintentos del proveedor, plazo compartido y reserva de propuestas

Fecha: 6 de noviembre de 2026. Base: `2cb3e82`, integración autorizada del PR #40.
Rama: `codex/reintentos-presupuesto`. Los PR #39/#41 y la política de severidad
quedan fuera de este bloque. Se conservan rutas, cuerpos JSON y estados públicos.

## 429 y consumo

El limitador HTTP propio conserva pesos, ventana, 429 y Retry-After. Rechaza
antes de Gemini y no se reintenta desde el servidor. La cuota SQLite llena
también conserva su 429 previo a generación.

Un 429 de Gemini admite reintento, junto con 502/503/504. Por defecto hay dos
intentos totales por llamada lógica, incluido el inicial; LLM_RETRY_ATTEMPTS
permite 1..3. Espera exponencial desde 0,6 s hasta 2 s, o más si lo exige un
Retry-After válido (segundos o fecha HTTP). Si esa espera no cabe en el plazo,
se finaliza sin otra llamada ni espera innecesaria. No se acorta la espera del
proveedor para encajar. El agotamiento de intentos por 429 termina como 503;
el agotamiento del plazo termina como 504 o conserva el respaldo parcial existente.

Los timeouts de E/S no se reintentan para evitar duplicar trabajo de estado
incierto; tampoco autenticación/entrada inválida. El SDK usa attempts=1 en el
cliente y en cada llamada. Solo la aplicación controla los reintentos.

## Plazo compartido

El middleware crea un reloj monotónico por solicitud que se propaga a hilos,
decisiones del agente, síntesis y archivos del proyecto. No se reinicia por fase
ni archivo. Cada intento real consume una unidad antes del transporte, incluso
si falla. Máximos por solicitud: tres intentos individual, nueve agente y quince
proyecto. Son cotas de llamadas, no cuotas de tokens.

| Variable | Defecto y máximo | Timeout cliente |
|---|---:|---:|
| ANALYSIS_TOTAL_SECONDS: fragmento, .py, propuesta | 45 s | 60 s |
| AGENT_TOTAL_SECONDS | 150 s | 180 s |
| PROJECT_TOTAL_SECONDS: ZIP/GitHub | 150 s | 180 s |

Valores positivos inferiores reducen el plazo; inválidos usan el defecto y
superiores se acotan al máximo. LLM_TIMEOUT_SECONDS y AGENT_TIMEOUT_MS siguen
limitando cada transporte, además del restante. Las correcciones tienen un
timeout cliente de 60 s combinado con su cancelación previa.

RAG comprueba el plazo antes/después, incluso sin fuentes; GitHub ajusta timeout
y comprueba durante el cuerpo; Ruff/Bandit ajustan su espera y recolectan al hijo.
Respuestas generativas tardías no se publican como completas. Se conservan
respaldo estático, trazas y liberación de concurrencia cuando termina el trabajo.

El plazo es **cooperativo**. HTTPX aplica timeout de E/S; una fase de CPU,
almacenamiento o transporte que no coopere puede sobrepasar el plazo, pero su
resultado tardío se rechaza. No se abandona el hilo ni se libera concurrencia
mientras sigue trabajando. Un límite estricto a nivel de proceso necesita otro
aislamiento; las pruebas no certifican latencia máxima de Railway.

## Reserva SQLite antes de generar

BEGIN IMMEDIATE cuenta filas físicas de propuestas más reservas para el cupo
global; por sesión cuenta propuestas vigentes más reservas. Conserva la
recuperación de espacio de tombstones. Confirma y cierra la conexión antes de
Gemini; otros procesos observan el cupo ocupado sin esperar esa generación.

La tabla de reservas solo guarda hashes y caducidad, sin código ni credenciales.
Sus 180 s superan el máximo de solicitud de 150 s. Tras caída del proceso, la
purga o una nueva reserva recupera cupos vencidos. Finalizar consume una reserva
propia vigente e inserta la propuesta en la misma transacción. Una generación
antigua no ocupa una reserva posterior: devuelve 504. El TTL de cinco minutos
de la propuesta comienza al publicarse.

Errores de generación, validación o almacenamiento liberan de mejor esfuerzo;
si SQLite impide liberar, se conserva el error original y la reserva caduca.
Cancelar/fallar no reembolsa llamadas ya iniciadas. SQLite coordina procesos con
el mismo archivo; el limitador HTTP y la concurrencia general siguen siendo por
proceso, por lo que réplicas independientes requieren coordinación adicional.

## Base y verificación

Se comprobaron seis workflows de main en success y el deployment Railway
7611418000, asociado a `2cb3e82`, en success. Salud pública 200 no identifica SHA.
Ver [registro de la base](evidencias/semana-4/reintentos-presupuesto-20261106/main-validado.json).

Se prueban reloj/sueño simulados, SDK real con transporte simulado, SQLite real,
hilos y un proceso hijo. La revisión independiente detectó el retorno temprano
de abstención tras RAG sin comprobar el plazo; su regresión se corrigió.
Resultados: [evidencias del bloque](evidencias/semana-4/reintentos-presupuesto-20261106/README.md).
Se entrega otro PR en borrador, sin integración ni despliegue de este bloque.
