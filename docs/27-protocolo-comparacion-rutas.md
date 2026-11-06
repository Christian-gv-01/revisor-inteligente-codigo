# Comparación de veinte casos: ruta directa y agente

Preparación del 6 de noviembre de 2026, sobre main `b7431c1`. Atiende la página 4
de la ficha docente: los resultados directos del PR 37 no sustituyen una medición
equivalente del agente. Este trabajo prepara el evaluador; no contiene una nueva
corrida real ni modifica el comportamiento de la aplicación.

## Qué se compara

- Los mismos veinte casos y etiquetas de `eval/preguntas_referencia.json`.
- `/api/v1/analizar` y `/api/v1/agente/analizar`, máximo tres pasos.
- Veinte solicitudes de análisis por ruta, más tres lecturas de salud/esquema,
  alternadas por caso: diez pares directa/agente y
  diez agente/directa. Cada par conserva exactamente el mismo archivo y código.
- Estado, TP/FP/FN, precisión, recall, F1, referencias resueltas, ubicaciones,
  latencia HTTP y espera por presupuesto por separado.
- En agente: pasos, decisiones y finalización temprana explícita. No inferir
  número de llamadas o tokens Gemini a partir del número de solicitudes HTTP.

El emparejamiento reutiliza el criterio ya existente: categoría/título y línea
admisible, con asignación uno a uno. Las referencias se resuelven por ID dentro
del informe. Revisión humana de citas, explicaciones y parches sigue siendo
necesaria; el conjunto es propio, pequeño y no un holdout independiente.

## Errores y resultados parciales

No hay reintentos del evaluador. Se conservan respuestas parciales, 429, 503,
timeouts y errores de formato. Los cuerpos HTTP de error no se guardan.
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
3. Registrar modelo, temperaturas, máximos de tokens, timeouts y procedencia en
   un JSON público, sin claves. Si un valor no se verificó, declararlo en
   `campos_no_verificados`; no sustituirlo silenciosamente por un default.
4. Acordar una ventana sin cambios de despliegue ni otras corridas simultáneas.
5. Presupuestar cuarenta solicitudes HTTP. Con el agente actual, hasta ochenta
   llamadas generativas antes de reintentos internos; esto es una estimación,
   no un consumo observado ni un límite facturable garantizado.

El cliente respeta diez unidades por ventana de 61 segundos: directa pesa uno
y agente tres. Puede hacer pausas. Su timeout no modifica el presupuesto temporal
del servidor. La duración de red se registra sin sumar las pausas del evaluador.

## Ejecución

Primero, sin red ni proveedor:

```sh
python eval/comparar_rutas.py --validar
python -m pytest eval/test_comparar_rutas.py -q
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
