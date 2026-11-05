# Agente en la revisión principal

## Problema y comportamiento

La comparación registrada en `docs/evidencias/semana-4/comparacion-muestra-20261105/resultados.json` mostró 15 observaciones estáticas conservadas y dos hallazgos contextuales. El agente localizó `eval` por AST, pero su informe final no recibía esa evidencia y devolvió una ubicación incorrecta. No se demostró una regresión histórica de precisión: los contadores pertenecen a capas distintas.

En modo API real, el botón principal para código pegado y archivos `.py` llama a `/api/v1/agente/analizar`. Ruff/Bandit se ejecutan una vez, el agente inspecciona la estructura y Gemini elige hasta dos inspecciones adicionales o finalizar. La síntesis recibe los resultados realmente obtenidos, consulta RAG y devuelve un informe con la traza visible y exportable. El modo Demo sigue siendo explícito.

ZIP y GitHub mantienen la revisión directa existente. Este cambio integra el agente para un archivo; no afirma que los proyectos completos ya tengan planificación agéntica. Agent Lab conserva su función de demostración técnica.

## Contrato y límites

- Evidencia tipada: hasta tres inspecciones, veinte indicadores por inspección y cuarenta reglas estáticas, priorizadas por severidad. Se conserva el total original y la lista estática completa en la respuesta.
- RAG consulta categorías conocidas a partir de reglas e indicadores y reserva cobertura entre ellas, con un máximo de seis fuentes únicas. Las consultas son constantes controladas; las herramientas no producen URLs ni citas RAG.
- El filtro `area` del recuperador pertenece al contexto del proyecto; la recuperación del agente no lo utiliza para buscar seguridad. Se filtran las fuentes por su tipo real después de recuperar.
- Cada hallazgo contextual exige IDs presentes en las fuentes recuperadas y un fragmento literal de una sola línea. Si el número propuesto no coincide, solo se corrige cuando el fragmento tiene una única ubicación. Se conserva `linea_reportada_modelo` cuando ocurre esa corrección.
- Un fragmento ambiguo o una cita inválida excluye ese hallazgo. Si quedan otros válidos, el estado es parcial; si todos se rechazan, el sistema se abstiene. La coincidencia textual y la existencia de una cita no certifican la interpretación semántica ni la explotabilidad.
- Los fallos del proveedor conservan las observaciones estáticas, los pasos y las decisiones realmente ejecutadas, con estado parcial y origen local explícito.
- La interfaz distingue hallazgos contextuales y observaciones de herramientas. Pueden señalar el mismo riesgo y no se suman como vulnerabilidades diferentes.
- El código se analiza como texto; no se importa ni se ejecuta. Los resultados y el código se serializan como datos no confiables separados de las instrucciones del modelo.

## Validación reproducible

Desde `backend/`: `python -m pytest tests ../qa -q`.

Desde `frontend/`: `npm ci`, `npm run lint`, `npm test -- --run` y `npm run build`.

Desde la raíz, con dependencias e índice local preparado:

```bash
python eval/run_integration.py --static-analysis --output tmp/agente-http-estatico
python eval/run_integration.py --output tmp/agente-http-sin-estatico
```

Resultados locales: 250 pruebas backend/QA y 76 frontend aprobadas; 17/17 HTTP con estático y 12/12 aplicables sin él (cinco omitidas por configuración). Las pruebas HTTP usan FastAPI, ChromaDB y Ruff/Bandit reales, con Gemini y la API externa de GitHub simulados. No miden precisión de Gemini.

Las regresiones incluyen la corrección de `eval` de las líneas 24/27 a la línea real 25, fragmentos repetidos, citas inválidas, conservación de hallazgos válidos y transmisión real de evidencia a la síntesis. Se utilizan casos controlados y no se ejecuta la muestra del usuario.

Pendiente tras despliegue: repetir la comparación autorizada con Gemini real, usando la misma muestra y configuración, registrar citas, ubicaciones y tiempo. No se afirma una mejora de recall a partir de respuestas simuladas. El índice actual cubre seis reglas documentales; no respalda automáticamente todos los patrones de Bandit. La compilación conserva la advertencia conocida del paquete Monaco. No se completó la revisión visual en navegador en este entorno: no estuvo disponible el ejecutable Chromium.
