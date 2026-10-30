# Evaluación de la semana 3

`preguntas_referencia.json` contiene exactamente 20 preguntas propias, código Python, respuesta de referencia, fuentes esperadas, estado esperado y hallazgos esperados. No se ejecuta ni importa el código de los casos. Las preguntas describen la intención de la prueba; la API recibe únicamente `archivo` y `codigo`, de acuerdo con su contrato.

- P01–P06: SQL; cuatro ejemplos vulnerables y dos controles negativos.
- P07–P12: comandos del sistema; cuatro ejemplos vulnerables y dos controles negativos.
- P13–P18: ejecución dinámica; cuatro ejemplos vulnerables y dos alternativas sin ejecución de texto.
- P19–P20: fuera de la cobertura documental actual; se espera abstención.

Las etiquetas se basan en `knowledge/seguridad_python.md` y sus cuatro fuentes oficiales. Son una propuesta para revisión del equipo, no un conjunto externo validado. «Sin hallazgos esperados» se limita al fragmento y a las reglas del conjunto; no certifica seguridad general.

## Comprobar el conjunto y el evaluador

Desde la raíz del repositorio, con Python 3.10 o posterior:

```powershell
python eval/run_eval.py --validate-only
python -m unittest discover -s eval -p "test_*.py" -v
```

Estas dos comprobaciones usan solo la biblioteca estándar.

## Recuperación RAG sin clave de IA

Usar el entorno del backend con sus dependencias. El entorno local de esta entrega está en `.venv`; sus versiones exactas se registran en `docs/evidencias/semana-3/entorno-python.txt`.

```powershell
.\.venv\Scripts\python.exe scripts/ingest.py
.\.venv\Scripts\python.exe eval/run_eval.py --mode rag
```

La primera ingesta puede descargar el modelo de embeddings de ChromaDB. El ejecutor utiliza `_construir_consulta_rag` y `_recuperar_contexto_rag`, las mismas funciones que el análisis real. Evalúa las fuentes de seguridad devueltas, no el contexto interno del proyecto. Comprueba la colección y realiza una consulta de calentamiento antes de medir latencias. No llama a Gemini.

## Evaluación completa con IA

El responsable de backend debe configurar `GEMINI_API_KEY` y, si corresponde, `GEMINI_MODEL` en el `.env` local antes de iniciar el servidor. El archivo está ignorado por Git. Reiniciar el backend después de modificarlo, porque la configuración se carga al importar el servicio.

Primera terminal, desde la raíz:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Segunda terminal, desde la raíz:

```powershell
.\.venv\Scripts\python.exe eval/run_eval.py --mode api --base-url http://127.0.0.1:8000
```

Esta ejecución envía hasta 20 solicitudes secuenciales al backend y puede consumir la cuota del proveedor que configure el equipo. El evaluador no reintenta automáticamente. Admite `--timeout 90`, `--k 3`, `--dataset ruta.json` y `--output carpeta-nueva`. Cada ejecución crea una carpeta fechada y nunca sobrescribe una carpeta de evidencias existente.

Si se ejecuta contra otro servidor, registrar además su revisión, modelo, prompt y configuración RAG: los hashes automáticos corresponden a los archivos locales, no permiten identificar un servidor remoto.

## Resultados

- `resultados.json`: respuestas originales, resultados por caso, métricas, fecha UTC, revisión base, cambios locales, hashes y versiones.
- `resultados.csv`: tabla por caso para inspección y comparación.
- `resumen.md`: resumen legible con errores.
- Código de salida `0`: ejecución completada; no implica calidad aprobada. `1`: uno o más errores de ejecución. `2`: argumentos o dataset inválidos.

El modo API calcula coincidencias por categoría/título y línea admisible, con emparejamiento uno a uno. Un hallazgo duplicado cuenta como falso positivo. Las abstenciones se distinguen de respuestas sin hallazgos. Los errores HTTP o de conexión se registran aparte y nunca se convierten en aciertos; consultar siempre completitud junto a las métricas de calidad.

Una referencia resuelta significa que su ID está en `fuentes`; no demuestra que el documento sustente semánticamente el hallazgo. Las explicaciones, correcciones, severidad y pertinencia documental requieren revisión humana. Las fórmulas y limitaciones están en [el informe](../docs/07-evaluacion.md).

## Verificación visual reproducible

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Abrir `http://127.0.0.1:5173/tests/fuentes-preview.html`. La página usa el componente real con respuestas simuladas identificadas y permite probar fuentes, ausencia de metadatos, abstención y ZIP parcial. Está fuera de la entrada de producción de Vite. La aplicación normal está en `http://127.0.0.1:5173/`.
