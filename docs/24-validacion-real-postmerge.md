# Validación real después del PR 36

Fecha: 6 de noviembre de 2026. Revisión desplegada y evaluada:
`caecd719a92fa40c060f24051b765e77721ee19b`. Este documento registra una corrida
nueva; no altera las evidencias históricas ni atribuye esta ejecución a otro integrante.

## Versión, CI y despliegue

Los seis workflows de `push` en main aprobaron. Railway muestra activo el
despliegue `5fe3f82b-9fd5-43d0-85fd-55c3d63395e3`, con enlace al commit indicado.
La URL pública respondió en `/health` y su OpenAPI incorporó las dos rutas de
correcciones. Se observó arranque con UID 10001 y recuperación del índice persistente.
No se inició un despliegue manual ni se cambiaron variables de Railway.

Evidencia: [registro del despliegue y enlaces de CI](evidencias/semana-4/postmerge-caecd71-20261106/despliegue-verificado.json)
y [captura del arranque](evidencias/semana-4/postmerge-caecd71-20261106/railway-arranque.jpg).
Este registro no sustituye el log no aportado del 5 de noviembre ni demuestra
integridad de todos los datos del volumen.

## Evaluación del modelo real

Se conservó el dataset de veinte casos de `eval/preguntas_referencia.json`, sus
etiquetas y el evaluador de métricas. Se enviaron únicamente fragmentos sintéticos
al endpoint `/api/v1/analizar`, con Gemini del servidor; el evaluador no simuló
sus respuestas ni reintentó casos. El backend conserva sus reintentos propios.

| Métrica | Resultado |
|---|---:|
| Informes completos | 20/20 |
| Respuestas parciales o errores | 0 |
| Casos coincidentes con la referencia | 20/20 |
| TP / FP / FN | 12 / 0 / 0 |
| Precisión / recall / F1 de hallazgos | 1 / 1 / 1 |
| Hallazgos con referencias resueltas | 12/12 |
| Referencias presentes en las fuentes devueltas | 14/14 |
| Líneas fuera del archivo | 0 |
| Latencia media / p95 del cliente | 5964,98 / 8107,56 ms |

Los veinte casos son propios, pequeños y ligados al corpus del proyecto. Se hizo
una sola corrida. El emparejamiento compara categoría/título y una línea admisible;
no prueba automáticamente que cada explicación o parche sea correcto. Resolver
un ID de cita no demuestra por sí mismo pertinencia semántica. No se ha medido
generalización a repositorios grandes ni estabilidad prolongada del proveedor.

Los parámetros efectivos y el modelo del servidor no se exponen por API; se
registran como no verificados en lugar de inferirlos de los valores predeterminados.
No se publican variables privadas ni cookies.

Esta evaluación mide el flujo directo, **no el planificador del agente**. Su smoke
real se conserva por separado. Tampoco permite afirmar una mejora porcentual de
calidad frente a Semana 3: esa corrida no tenía proveedor generativo configurado.

Evidencias: [JSON completo](evidencias/semana-4/postmerge-caecd71-20261106/evaluacion-real-20/resultados.json),
[CSV](evidencias/semana-4/postmerge-caecd71-20261106/evaluacion-real-20/resultados.csv)
y [resumen](evidencias/semana-4/postmerge-caecd71-20261106/evaluacion-real-20/resumen.md).

## Recuperación documental local

Con el corpus e índice local de esta revisión, sin Gemini, completaron los veinte
casos. Entre los dieciocho con referencias esperadas: Precision@3 0,4630,
Recall@3 0,8056, MRR@3 0,8611 y Hit@3 0,8889. Los dos casos fuera de cobertura
no devolvieron fuentes. Media 163,88 ms y p95 182,95 ms, después del calentamiento.

La latencia corresponde a este entorno de QA, no a Railway. El corpus y su
cobertura cambiaron desde la baseline de Semana 3; no se declara una mejora por
comparar cifras de condiciones diferentes. La recuperación y los hallazgos tienen
denominadores distintos: el recall documental 0,8056 no contradice el recall de
hallazgos 1 sobre esta muestra.

Evidencia: [recuperación local](evidencias/semana-4/postmerge-caecd71-20261106/recuperacion-local-20/resultados.json).

## Trazabilidad de observaciones

| Observación registrada | Cambio y comprobación | Estado y límite |
|---|---|---|
| Agente separado de la interfaz | PR 31 y PR 36; HomePage usa agente para código y .py; CI HTTP y navegador | Integrado para esas modalidades; ZIP/GitHub conservan revisión por archivo |
| Herramientas sin influencia en síntesis | PR 31 conserva envío de evidencia AST/Ruff/Bandit al informe; regresiones en main | Contrato verificado; no demuestra una mejora causal de precisión |
| Ruff/Bandit y hallazgos invisibles | Evidencia independiente en informe, marcadores y estado parcial; pruebas HTTP con herramientas reales | Los conteos de herramientas y Gemini pueden referirse al mismo riesgo |
| Configuración dispersa | PR 35 integrado con settings y reglas de prioridad; 11 pruebas de configuración | Los contratos de entrada conservan límites fijos explícitos |
| Priorización | Nueve pruebas específicas y presentación en frontend | Ordena severidad/categoría; no recalcula la severidad de Gemini |
| Confirmación humana | Contrato v1, sesión propietaria, hashes, caducidad, idempotencia y conflictos; CI con interfaz/FastAPI/SQLite reales | Descarga de copia; no ejecución ni sobrescritura; interfaz pública deshabilitada por defecto |
| CI solo en PR / modelo descargado al arrancar | PR 33 y seis workflows verdes tras fusionar PR 36; Docker sin red | Incluye modelo precargado, UID sin privilegios y SQLite en /data |
| Gitleaks fallido | Clasificación de fixture histórico y hashes de procedencia; excepciones exactas | CI de historial aprobado; no equivale a revocación ni auditoría de variables privadas |
| Falta de evaluación generativa final | Corrida real de veinte casos con respuestas y etiquetas congeladas | Medición actual completada; sin baseline generativa comparable ni holdout independiente |
| Falta de log independiente del volumen | Captura real del arranque actual y relación con commit | Acredita este arranque, no reconstruye el evento histórico |

## Pendientes que no se cierran con estas pruebas

- Confirmación del equipo sobre integración, aportes, identidades y documentación.
- Revisión semántica de explicaciones, citas y correcciones; evaluación amplia del agente.
- Levantamiento auténtico y evidencias iniciales, o explicación de su ausencia al docente.
- Instalación limpia cronometrada, PDF final de doce minutos y ZIP revisado contra Git.
- Observaciones de sustentación, registradas únicamente después de que ocurran.
- Decisión explícita sobre habilitar correcciones en el frontend de producción.

## Reproducción

Desde la raíz, con el entorno backend preparado y usando una carpeta de salida nueva:

```sh
python scripts/evaluar_produccion_postmerge.py --base-url URL --commit-servidor SHA_VERIFICADO --output tmp/evaluacion-nueva
python eval/run_eval.py --mode rag --output tmp/recuperacion-nueva
python scripts/pruebas_produccion.py --base-url URL --output tmp/matriz-nueva.json
python scripts/probar_flujo_real_postmerge.py --base-url URL --commit-servidor SHA_VERIFICADO --output tmp/flujo-nuevo.json
```

El parámetro de commit es una referencia comprobada por el operador en el
despliegue; no es una atestación que devuelva la API. El evaluador respeta el
presupuesto público. Si el equipo necesita proxy, la matriz admite
`--usar-proxy-entorno`; TLS sigue verificado y no se siguen redirecciones.
No ejecutar varias corridas simultáneamente contra el mismo presupuesto por IP.


## Matriz pública y flujo real del agente y correcciones

La [matriz pública](evidencias/semana-4/postmerge-caecd71-20261106/matriz-publica.json)
aprobó 26/26 escenarios sobre esta revisión. Comprueba salud, errores HTTP,
validación, archivos/ZIP inválidos, GitHub inválido y AST local. Su caso P26 no
llama a Gemini y no certifica resistencia general del modelo a prompt injection.

El [smoke real](evidencias/semana-4/postmerge-caecd71-20261106/flujo-real.json)
aprobó nueve aserciones: agente con decisiones/informe/fuentes, dos propuestas
generadas realmente, bloqueo de decisión sin sesión, aprobación exacta,
idempotencia, rechazo sin contenido y dos conflictos por decisión contraria.
El ejemplo SQL fue localizado en la línea 6. La propuesta inspeccionada conserva
la consulta con `?` y pasa `(nombre,)` por separado a `cursor.execute`.
No se ejecutó el fragmento ni se escribió una copia sobre el original.

Esta prueba usa HTTP, no la interfaz pública, cuya bandera sigue desactivada.
La interfaz contra backend real ya tiene siete escenarios de navegador aprobados
en CI con Gemini simulado. La caducidad 410 se comprobó en ese entorno controlado;
no se esperaron cinco minutos para repetirla con el proveedor de producción.

Se verificaron los blobs Git de servicios, configuración, prompt y dataset contra
main. La copia local del corpus tiene una línea final adicional; su texto restante
es idéntico y su hash se distingue del servidor. La recuperación local no se
presenta como medición remota. Ver [procedencia](evidencias/semana-4/postmerge-caecd71-20261106/fuentes-verificadas.json).

Gitleaks del árbol de trabajo no detectó secretos. Durante la preparación marcó
el hash del esquema OpenAPI por el nombre de su campo; se comprobó que era el
SHA-256 del esquema público y se nombró `esquema_sha256`. No se añadió una excepción
ni se alteraron respuestas del modelo para resolver ese falso positivo. La
validación del historial de esta rama corresponde a su corrida de Actions.
