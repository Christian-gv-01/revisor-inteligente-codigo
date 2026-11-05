# CODEGUARD — Evaluación controlada del planificador (Semana 4)

## 1. Pregunta de investigación

**¿Cambian las decisiones del agente supervisado cuando recibe, además de la estructura AST inicial, un resumen verificable de los hallazgos producidos por Ruff y Bandit?**

Esta evaluación es **adicional** a la evaluación RAG de los 20 casos y a las pruebas de aceptación públicas. No pretende medir precisión, recall, F1 o tasa de detección de vulnerabilidades, porque solo se evalúa la **primera decisión del planificador** antes de ejecutar herramientas adicionales.

## 2. Diseño A/B pareado

El script `eval/evaluar_planificador_agente.py` analiza seis programas Python **sintéticos**, con los mismos fragmentos de código para ambas condiciones y hasta tres repeticiones:

| Variable | Condición A | Condición B |
|---|---|---|
| Código Python | Idéntico | Idéntico |
| Modelo y prompt del planificador | Mismos | Mismos |
| Inspección inicial AST | Sí | Sí |
| Ruff + Bandit | Se ejecutan | Se ejecutan |
| Resumen Ruff/Bandit visible al planificador | **No** | **Sí** |
| Llamadas al informe final Gemini + RAG | No | No |
| Herramienta escogida | Se registra | Se registra |

Las condiciones se ejecutan en orden **AB/BA alternado** por caso y repetición. El modelo se configura en CODEGUARD con `temperature=0`, pero ello **no garantiza decisiones idénticas** a través de llamadas distintas. La cuota o disponibilidad del proveedor también puede variar.

**Importante:** la condición A es *solo una condición experimental*; el sistema desplegado sigue ejecutando Ruff y Bandit obligatoriamente. No se desactivan las herramientas en CODEGUARD ni se modifica la configuración de producción.

## 3. Datos y alcance

Los seis casos públicos del repositorio están en `eval/casos_planificador_agente.json`:

- `eval_entrada`: llamada sensible con entrada de usuario.
- `exec_entrada`: ejecución dinámica.
- `sql_concatenado`: SQL construido con entrada de usuario.
- `comando_shell`: comando del sistema mediante `os.system`.
- `funcion_limpia`: función aritmética sin patrón peligroso conocido.
- `sql_parametrizado`: consulta SQL con parámetros.

Estos casos no tienen datos personales reales, credenciales ni rutas internas. Se interpretan como texto y AST; **jamás se ejecutan los fragmentos**.

El archivo de datos puede ampliarse de forma revisada sin exceder los 10 casos ni el presupuesto máximo de 60 solicitudes por ejecución.

## 4. Ejecución en Windows — sin modificar Railway

Abrir CMD en la **raíz** del proyecto, con la rama de evaluación activa y el entorno virtual previamente instalado:

```cmd
backend\.venv\Scripts\python.exe eval\evaluar_planificador_agente.py
```

El comando anterior **no consulta Gemini**. Solo comprueba que el dataset y el presupuesto de llamadas sean válidos.

Cuando se quiera medir el comportamiento del modelo real:

```cmd
backend\.venv\Scripts\python.exe eval\evaluar_planificador_agente.py --ejecutar --repeticiones 1
```

**Advertencia:** este segundo comando puede consumir hasta **12 solicitudes** al planificador Gemini; el SDK podría realizar reintentos ante 502/503/504. El modelo requiere `GEMINI_API_KEY` en el archivo `.env` local o en variables de entorno, **nunca en Git**. El script se beneficia de los límites y manejo de errores establecidos en `planificar_gemini`.

Una segunda sesión con `--repeticiones 2` podría consumir hasta **24 solicitudes**. No ejecutar pruebas repetidas si hay saturación del proveedor; las respuestas fallidas deben conservarse como evidencia, no repetirse hasta obtener una puntuación favorable.

Los resultados se guardan bajo `docs/evidencias/semana-4/agente-ab-<fechaUTC>/`. Se producen:

- `resultados.json`: configuración de evaluación, resumen de pares y decisiones por solicitud.
- `resultados.csv`: métricas tabulares para el análisis.
- `resumen.md`: comparación legible con limitaciones.

No se guardan fragmentos de código, motivos textuales del modelo, claves ni respuestas crudas de errores. Se utiliza una huella SHA-256 abreviada de cada código para comprobar que ambos grupos reciben el mismo fragmento.

## 5. Métricas y criterios de interpretación

**Métricas reportadas:**

1. **Pares completos:** ambos grupos respondieron con una herramienta válida.
2. **Pares no comparables:** hubo error de proveedor o faltó una respuesta.
3. **Tasa de cambio de decisión:** pares completos que eligieron herramientas diferentes / pares completos.
4. **Distribución de herramientas:** frecuencia de `detectar_llamadas_sensibles`, `revisar_consultas_sql` y `finalizar` por condición.
5. **Latencia media de respuestas válidas**, más tasa de éxito/error por condición.
6. **Casos excluidos:** si Ruff/Bandit no completaron el análisis, el caso no se utiliza para establecer comparaciones.

Un **cambio de decisión no implica automáticamente una decisión mejor**. Para evaluar calidad sería necesario fijar de antemano los criterios expertos de cada escenario, ampliar el número de casos y comparar falsos positivos/negativos, precisión, latencia y costo; eso corresponde a una investigación posterior.

**Posible resultado sin cambios:** si el agente selecciona lo mismo con y sin las alertas, la integración técnica funciona, pero **no se demuestra beneficio de la evidencia Ruff/Bandit para esas muestras**. Esta conclusión debe declararse sin modificar retrospectivamente los casos.

**Limitaciones:** tamaño pequeño, diseño experimental no aleatorizado (orden contrabalanceado), variabilidad del servicio, selección de una sola decisión, casos sintéticos y ausencia de medición del informe RAG final.

## 6. Evidencias y aprobación

El ensayo debe incluir en la entrega final los resultados **reales** obtenidos en Windows con el modelo efectivamente utilizado; no sustituirlos por resultados simulados de pruebas unitarias.

Los tests `backend/tests/test_evaluacion_planificador.py` y el modo sin `--ejecutar` verifican la metodología sin consumir solicitudes. Su aprobación **no sustituye** la ejecución de la comparación real.

La consolidación en `integration/semana4-candidata`, el despliegue a `main` y la publicación en Railway siguen sujetos a revisión de QA y de los demás integrantes del equipo.


## 7. Primera ejecución real: 5 de noviembre de 2026

**Procedencia:** resultados leídos de `resumen.md` y `resultados.csv` mostrados por el operador en capturas de pantalla de su ejecución Windows. Este apartado registra la interpretación de esos datos; **los archivos CSV/JSON originales no están incluidos todavía en este commit**. El comando ejecutado fue `python eval/evaluar_planificador_agente.py --ejecutar --repeticiones 1` con el modelo `gemini-3.5-flash-lite`.

| Métrica | Resultado |
|---|---:|
| Casos sintéticos | 6 |
| Solicitudes efectuadas | 12 |
| Pares válidos | 5 |
| Pares no comparables | 1 |
| Pares válidos con diferente herramienta | 0 |
| Tasa de cambio de decisión | 0,00 (0/5) |
| Respuestas del proveedor fallidas | 1 (HTTP 503, condición sin contexto) |
| Latencia media sin contexto, solo los cinco pares válidos | 1.815,52 ms |
| Latencia media con contexto, solo los cinco pares válidos | 3.085,12 ms |

### Primera decisión observada

| Caso | Sin contexto | Con contexto | Interpretación |
|---|---|---|---|
| `eval_entrada` | `detectar_llamadas_sensibles` | `detectar_llamadas_sensibles` | Igual |
| `exec_entrada` | `detectar_llamadas_sensibles` | `detectar_llamadas_sensibles` | Igual |
| `comando_shell` | `detectar_llamadas_sensibles` | `detectar_llamadas_sensibles` | Igual |
| `sql_concatenado` | `revisar_consultas_sql` | `revisar_consultas_sql` | Igual |
| `funcion_limpia` | `detectar_llamadas_sensibles` | `detectar_llamadas_sensibles` | Igual; revisar posible inspección innecesaria |
| `sql_parametrizado` | Error HTTP 503 | `revisar_consultas_sql` | No comparable |

**Interpretación honesta:** La integración de Ruff/Bandit como contexto quedó probada técnicamente en pruebas unitarias e inspecciones locales, pero **no se observó cambio de herramienta en los cinco pares comparables**. Esto **no significa** que la información adicional no sirva nunca ni que el agente sea más preciso: solamente indica que el primer paso elegido fue idéntico en estas muestras. El paso de revisión en `funcion_limpia` tampoco equivale a un falso positivo hasta examinar los hallazgos de la herramienta.

Las medias de latencia se calcularon sobre **las mismas cinco parejas completas**, excluyendo la pareja con error. La latencia observada fue mayor con contexto en cuatro de cinco casos; por tamaño de muestra y variación temporal del proveedor, **no se establece causalidad ni significación estadística**.

La captura del reporte antiguo muestra secuencias de escape Markdown `\\`` y caracteres mal interpretados por la consola Windows. El generador se corrigió en el PR de evaluación, pero **los archivos ya generados requieren regeneración local sin volver a solicitar respuestas de Gemini**. No modificar el CSV real para ajustar cifras. El HTTP 503 de este CSV no debe confundirse con errores 429 observados en sesiones anteriores.

**Pendiente para evidencia académica:** incorporar los `resultados.json`, `resultados.csv` y `resumen.md` originales generados localmente en `docs/evidencias/semana-4/agente-ab-20261105T190848Z/`, después de revisar que no incluyan datos privados, claves o rutas sensibles.

