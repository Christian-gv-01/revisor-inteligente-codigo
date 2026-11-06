# Comparación de veinte casos: ruta directa y agente

Actualización del 6 de noviembre de 2026, contrastada con main `9c97ca1` tras integrar el PR #45. La primera versión del evaluador partía de `b7431c1`. Atiende la página 4
de la ficha docente: los resultados directos del PR 37 no sustituyen una medición
equivalente del agente. Este trabajo prepara el evaluador; no contiene una nueva
corrida real ni modifica el comportamiento de la aplicación.

## Qué se compara

- Los mismos veinte casos y etiquetas de `eval/preguntas_referencia.json`.
- `/api/v1/analizar` y `/api/v1/agente/analizar`, máximo tres pasos y `version_herramientas: "2"` explícita. No aceptar una respuesta v1 como medición del agente v2.
- Veinte solicitudes de análisis por ruta, más tres lecturas de salud/esquema,
  alternadas por caso: diez pares directa/agente y
  diez agente/directa. Cada par conserva exactamente el mismo archivo y código.
- Estado, TP/FP/FN, precisión, recall, F1, referencias resueltas, ubicaciones,
  latencia HTTP y espera por presupuesto por separado. La latencia se detiene al recibir la respuesta HTTP, antes de analizar JSON y calcular métricas.
- En agente: pasos por origen, decisiones, errores de herramienta, fase y terminación explícita. Los ejemplos publicados de contexto, referencias y error sirven como regresiones del contrato. Una ventana debe coincidir literalmente con el código recibido y los argumentos deben corresponder a las decisiones ejecutadas. No inferir
  número de llamadas o tokens Gemini a partir del número de solicitudes HTTP.

El emparejamiento reutiliza el criterio ya existente: categoría/título y línea
admisible, con asignación uno a uno. Las referencias se resuelven por ID dentro
del informe. Revisión humana de citas, explicaciones y parches sigue siendo
necesaria; el conjunto es propio, pequeño y no un holdout independiente.

## Errores y resultados parciales

No hay reintentos del evaluador. Se conservan respuestas parciales, 429, 503,
timeouts y errores de formato. Un HTTP200 degradado por fallo de herramienta v2 es un parcial, no un error de contrato ni un informe completo. Los cuerpos HTTP de error no se guardan.
Un parcial puede tener hallazgos útiles: se conserva su métrica observada, pero
no se cuenta como informe completo ni como caso correcto.

La tabla de comparación usa exclusivamente los casos con informe completo en
ambas rutas. El JSON informa también los resultados de cada ruta por separado,
la completitud sobre los veinte casos y los IDs excluidos de la cohorte común.
Así, una ruta con más fallos no obtiene artificialmente ventaja al compararse
solo con sus casos fáciles. Si no hay pares completos, F1 no es calculable.

No comparar Precision@3 de la ruta directa con fuentes del agente obtenidas con
otro presupuesto de recuperación. Este evaluador compara informes finales y
citas, no un ranking documental equivalente. Tampoco aísla causalmente al
planificador: las rutas difieren en orquestación, evidencia y recuperación.

## Antes de consumir Gemini

1. Incorporar y verificar los cambios acordados del producto. La rama del
   evaluador no modifica main.py, llm.py, configuración ni presentación.
2. Congelar una revisión, dataset, prompt, corpus y configuración efectiva.
   Registrar el SHA completo activo en Railway y comprobarlo otra vez al terminar.
   OpenAPI no devuelve una atestación de commit: un esquema sin cambios no prueba
   que no se haya desplegado otro código durante la evaluación.
3. Registrar modelo, temperaturas, máximos de tokens, timeouts, intentos de reintento, plazos compartidos, distancia RAG, análisis estático directo y procedencia en
   un JSON público, sin claves. Si un valor no se verificó, declararlo en
   `campos_no_verificados`; no sustituirlo silenciosamente por un default. Una corrida con campos desconocidos se identifica como exploratoria y no acredita control completo de la configuración.
4. Acordar una ventana sin cambios de despliegue ni otras corridas simultáneas.
5. Presupuestar cuarenta solicitudes HTTP. Con el agente actual, hasta ochenta
   llamadas generativas antes de reintentos internos; esto es una estimación,
   no un consumo observado ni un límite facturable garantizado. La revisión base limita cada petición directa a tres intentos reales y cada petición de agente a nueve: techo combinado conservador de 240 intentos, sujeto a los límites temporales y configuración efectivos. No confundir 40 peticiones, 80 llamadas lógicas estimadas y 240 intentos máximos con consumo observado; puede haber menos o ninguna llamada por abstención RAG.

Antes de enviar análisis, el evaluador exige que el esquema anuncie el campo v2 y rechaza el marcador de servidor fixture conocido. Esto comprueba compatibilidad, no demuestra que Gemini sea real: verificar también la procedencia del despliegue.

El cliente respeta diez unidades por ventana de 61 segundos: directa pesa uno
y agente tres. Puede hacer pausas. Su timeout no modifica el presupuesto temporal
del servidor. La duración de red se registra sin sumar las pausas del evaluador.

## Ejecución

Primero, sin red ni proveedor:

```sh
python eval/comparar_rutas.py --validar
python -m pytest eval/test_comparar_rutas.py eval/test_contrato_agente_evaluacion.py -q
```

La primera orden muestra el SHA-256 del dataset y las cuarenta solicitudes
previstas. No usar el resultado de estas pruebas como precisión de Gemini.

Preparar fuera de Git un `configuracion-publica.json` con campos permitidos:

```json
{
  "modelo": "VALOR_VERIFICADO",
  "temperatura_sintesis": "VALOR_VERIFICADO",
  "max_tokens_sintesis": "VALOR_VERIFICADO",
  "timeout_llm_segundos": "VALOR_VERIFICADO",
  "temperatura_planificador": "VALOR_VERIFICADO",
  "max_tokens_planificador": "VALOR_VERIFICADO",
  "timeout_planificador_ms": "VALOR_VERIFICADO",
  "intentos_llm": "VALOR_VERIFICADO",
  "plazo_directo_segundos": "VALOR_VERIFICADO",
  "plazo_agente_segundos": "VALOR_VERIFICADO",
  "distancia_max_rag": "VALOR_VERIFICADO",
  "estatico_directa_habilitado": "BOOLEANO_VERIFICADO",
  "corpus_sha256": "HUELLA_VERIFICADA",
  "prompt_sha256": "HUELLA_VERIFICADA",
  "fuente_verificacion": "Registro del operador sobre la revisión desplegada",
  "campos_no_verificados": []
}
```

Los marcadores son una plantilla, no valores de una corrida. Sustituirlos antes
de ejecutar; cualquier dato desconocido debe ser `null` y quedar identificado
por su nombre en `campos_no_verificados`. El evaluador rechaza marcadores,
valores numéricos inválidos y campos adicionales como claves del proveedor.
`estatico_directa_habilitado` debe ser booleano, `intentos_llm` un entero de 1 a 3, plazos compartidos como máximo 45/150 s y distancia RAG entre 0 y 2. Estos son límites de compatibilidad, no observaciones de Railway.

Para `prompt_sha256`, registrar SHA-256 de un manifiesto JSON canónico con las huellas SHA-256 de los bytes Git de `backend/app/services/llm.py`, `backend/app/services/agente.py` y `backend/app/services/evidencia.py`: claves por ruta ordenadas, sin espacios y UTF-8. Es una huella del código que construye ambos prompts y evidencia, no de un único texto dinámico. Para `corpus_sha256`, registrar los bytes del corpus ingerido y contrastar el índice efectivo; que el archivo exista en Git no prueba que el volumen activo lo haya ingerido. Especificar los criterios en `fuente_verificacion`.

```sh
python eval/comparar_rutas.py --ejecutar --base-url URL --revision-servidor SHA_COMPLETO --dataset-sha256 HUELLA_DATASET --config-publica configuracion-publica.json --output tmp/comparacion-nueva
```

Solo usar `--usar-proxy-entorno` cuando el equipo lo requiera. No desactiva TLS.
Se generan checkpoint, JSON completo, CSV y tabla Markdown en una carpeta nueva;
las corridas anteriores se conservan. No se ejecuta ni importa el código del dataset.

## Criterio de cierre

El evaluador estará preparado al aprobar sus pruebas y CI. La observación docente
solo se cierra después de ejecutar las dos rutas contra la misma versión estable,
conservar los cuarenta resultados y revisar sus límites. Si el agente empata o
empeora, documentarlo; no alterar etiquetas o seleccionar respuestas para afirmar
una mejora. Después se actualizan presentación y paquete final.

## Estado de esta actualización

El evaluador registra su propia huella, la del validador de traza y de las funciones métricas, versiones Python/httpx y SHA-256 de la configuración pública. Guarda la respuesta y los resultados tras cada petición. La matriz mantiene veinte pares aunque haya parciales o fallos; nunca completa la ruta faltante con datos de una corrida anterior.

Los tests y ejemplos son sintéticos: no aportan nuevos resultados de Gemini. No se ha ejecutado la corrida real de cuarenta análisis. La priorización final y el commit activo deben quedar acordados antes de congelarla; revisar el PDF/presentación después de los resultados, sin retocar etiquetas para favorecer al agente.

Validación local de la actualización: 40 pruebas del comparador, 10 del evaluador existente y 14 de QA aprobadas (64 en total). Se regeneraron los ejemplos con FastAPI y el orquestador actuales y se contrastaron respuesta completa, finalización anticipada y error de herramienta parcial; proveedor, RAG y estático simulados, cero llamadas IA externas. OpenAPI del main contrastado anuncia v2. Python/YAML válidos y escaneo local del directorio eval sin secretos. Estas comprobaciones no son resultados de calidad de Gemini ni validación de la versión activa en Railway.
