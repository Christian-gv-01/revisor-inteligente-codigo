# Agente v2: cuatro pasos, contexto y consumo medible

Base: `467d00e0d56a98cd758f382a5c713737eb490845` (PR #48).
Trabajo aislado: no cambia priorización, severidad, presentación, flags ni producción.

## Diferencias detectadas y cambios

| Requisito docente | Base revisada | Ajuste |
|---|---|---|
| Máximo de cuatro pasos | Contratos, decisiones y clientes limitaban a tres | v2 admite cuatro pasos y tres decisiones; v1 y valor predeterminado conservan tres |
| Contexto ±6 líneas | Ventana ±3, máximo siete líneas | Hasta trece líneas literales, con truncado individual de 500 caracteres |
| Referencia de deserialización | Categoría no disponible | `deserializacion` añadida a la lista cerrada y a su consulta local fija |
| Evidencia de todas las herramientas | El constructor usaba solo `pasos[:3]` | Conserva el cuarto paso y hasta tres resultados contextuales |
| Medir consumo | Logs de síntesis, sin agregado del planificador | Contadores por solicitud de todas las invocaciones SDK, incluyendo reintentos |
| Evaluar las herramientas v2 | A/B inicial por defecto v1 y solo nombre de herramienta | CLI del A/B por defecto v2; registra argumentos y cambios de herramienta o argumentos |

Los límites temporales y de consumo no aumentan: agente hasta 150 segundos cooperativos y nueve intentos de proveedor por solicitud. Cuatro pasos no significan cuatro procesos de Ruff/Bandit: estos se ejecutan una vez y la inspección inicial permanece obligatoria. Una decisión `finalizar` sigue pasando a la síntesis; no equivale a cero llamadas a Gemini.

La petición React conserva su máximo explícito de tres pasos para coordinar la integración con el PR #50. Su parser admite cuatro en v2 y conserva compatibilidad con ventanas literales antiguas de ±3. El laboratorio solicita v2 y permite seleccionar cuatro. El evaluador final solicita cuatro por defecto y puede declarar tres con `--max-pasos-agente 3`.

La categoría nueva no añade documentos al corpus. Recuperar cero referencias pertinentes debe conservarse como tal, sin inventar cobertura.

## Registro de consumo

Las rutas HTTP protegidas añaden la cabecera `X-Codeguard-Consumo-IA`, sin alterar el cuerpo JSON:

```json
{"version":1,"intentos":2,"respuestas":2,"tokens_entrada":30,"tokens_salida":4,"tokens_totales":34,"uso_completo":true}
```

Ejemplo numérico sintético de contrato, no resultado de Gemini real.

- `intentos` cuenta invocaciones efectivamente iniciadas en el SDK con sus reintentos internos deshabilitados; no se deduce del número de pasos.
- Los tokens proceden exclusivamente de `usage_metadata`: entrada, salida y total se registran independientemente. El total no se reconstruye sumando entrada y salida.
- Si falta un contador, ese contador queda `null`. Si algún intento no devuelve respuesta, los tokens de toda la solicitud quedan desconocidos: no puede demostrarse consumo cero para ese intento.
- Se conserva uso reportado de una respuesta tardía aunque su dictamen se descarte por plazo.
- Si no hubo ninguna llamada al SDK, los contadores son cero. El modo AST local no se presenta como una medición generativa.
- El registro está aislado por solicitud y protegido para el paso al threadpool. No contiene código, prompts, motivos, claves, IDs del proveedor ni errores crudos.

El evaluador conserva la telemetría también en HTTP de error, valida su formato y marca su ausencia o invalidez. Publica cobertura, sumas parciales explícitas y totales solo cuando todas las solicitudes tienen el dato. Son contadores declarados por el servidor a partir del SDK, no una factura ni un precio. Una caída de transporte sin respuesta impide recibir la cabecera.

## Preparación de las evaluaciones

Sin red ni consumo de Gemini:

```sh
python eval/comparar_rutas.py --validar
python eval/evaluar_planificador_agente.py --version-herramientas 2
```

El primer comando prepara veinte pares (cuarenta solicitudes), v2 y cuatro pasos. Antes de una corrida real exige que OpenAPI anuncie el máximo elegido. El dataset de veinte casos conserva SHA-256 `9908373c5650a9fb87992a50d56a05636c0dc2d615a25c0189c02b31e85d85ac`.

El segundo valida los seis casos históricos, sin modificarlos: SHA-256 `b5d74038241898a76a8834557d305378db8bd8f164ed3997af64b0f05b3222ef`. Una ejecución real posterior haría doce decisiones lógicas, AB/BA con y sin resumen estático, más reintentos permitidos. Sigue midiendo solo la primera decisión, no un bucle completo ni el informe final. Registra finalización en esa primera decisión y su tasa sobre todas las solicitudes; no la confunde con la tasa de terminación de la revisión completa.

No inferir tokens ahorrados ni mejor precisión a partir de elegir otra herramienta. La comparación completa conserva fallos, abstenciones y parciales y requiere revisión humana de citas.

## Validación local

- 604 pruebas Python aprobadas: 525 del backend y 79 de QA/evaluadores.
- 135 pruebas frontend aprobadas; las 24 HTTP se omiten en la suite unitaria.
- Integración HTTP con FastAPI, ChromaDB y analizadores reales: 24/24 con estático y 19/19 aplicables sin él, con cinco omitidas por configuración. Gemini y GitHub simulados.
- Lint y compilación frontend correctos. Persiste la advertencia previa de bundle mayor de 500 kB.
- Regresión JavaScript del laboratorio aprobada.
- Se añadió al recorrido de navegador el caso de cuatro pasos, propagación a síntesis y agregado de uso SDK sintético. El laboratorio se abre en la API loopback; el proxy Vite `/agente` pertenece al PR #50, todavía independiente. No hay Chromium instalado en este entorno local; su ejecución queda a la verificación CI, sin atribuirle un resultado local.

## Coordinación y pendientes

La severidad derivada y su herencia siguen a cargo del compañero de backend. La consolidación de `08-agente.md`, el presupuesto visible y la presentación siguen a cargo de frontend/documentación. Este registro no reemplaza esos entregables.

Antes de evaluar con Gemini real: integrar los cambios acordados, verificar configuración e índice Chroma efectivos, fijar SHA y ventana sin otros despliegues y confirmar el presupuesto. Después ejecutar las cuarenta solicitudes y los seis pares del planificador, revisar citas y actualizar resultados y PDF. Ninguna prueba de este bloque demuestra todavía mejora de precisión, recall o ahorro de tokens en producción.
