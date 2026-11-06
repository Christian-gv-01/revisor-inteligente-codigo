# Abstención y conservación de hallazgos — plan de implementación

Base: `b7431c1`. Autorización: Christian aprobó comenzar con este bloque y otorgó
libertad de implementación el 6 de noviembre. La ficha PDF (cinco páginas,
inspeccionadas visualmente) confirma en p. 4 la abstención global como pendiente;
su base de revisión es `65675e2` (p. 5).

## Diseño y alcance

Reutilizar la validación individual de citas de ambos recorridos. Mantener el
anclaje literal obligatorio exclusivamente para el agente, pues el contrato
directo anterior no lo requiere. Respetar una abstención explícita del modelo,
incluso si contradice su lista de hallazgos; descartar esos hallazgos y conservar
un motivo, con texto de respaldo cuando falte. Una lista vacía analizada sigue
siendo un resultado analizado, distinto de una abstención.

Los estados públicos continúan siendo analizado/abstenido/parcial. Los resultados
mixtos conservan hallazgos válidos y fuentes, y publican un mensaje de revisión
incompleta. Si no sobrevive ninguno, se abstienen. Conservar las validaciones de
líneas existentes y no relajar citas ni anclaje del agente. No incorporar nuevas
dependencias ni llamadas reales al proveedor.

ZIP/GitHub deben agregar estado parcial sin confundir una omisión documental con
indisponibilidad del proveedor. Corregir también la comparación de rutas del test
de SQLite para que sea válida en Windows y Linux, sin cambiar la ruta productiva.

## Secuencia verificable

- [x] Añadir regresiones del servicio real con cliente Gemini simulado: abstención
  explícita, motivo ausente, estado contradictorio y mezcla de citas válidas e inválidas.
- [x] Añadir regresiones HTTP para JSON, .py, ZIP, GitHub y agente, incluyendo
  propagación del mensaje parcial y procesamiento IA del siguiente archivo.
- [x] Ejecutar las regresiones y comprobar fallos antes del código productivo.
- [x] Implementar normalización y validación compartida en services/llm.py;
  propiedades de estado en models/analisis.py y adaptación/agregación en main.py.
- [x] Ejecutar backend, QA y evaluador; frontend pruebas, lint y build; integración
  HTTP con estático activado y desactivado. Usar carpetas nuevas bajo tmp/.
- [x] Revisar el diff con un revisor independiente y corregir problemas relevantes.
- [x] Documentar resultados y pendientes de la ficha sin declarar cerrada la entrega.

## Comandos

Desde backend: `.\.venv\Scripts\python.exe -m pytest tests -q`.
Desde raíz: `backend\.venv\Scripts\python.exe -m pytest qa eval -q` y
`node qa\check_agent_lab_ui.cjs`.
Desde frontend: `npm test`, `npm run lint`, `npm run build`.
Desde raíz: `backend\.venv\Scripts\python.exe eval/run_integration.py --static-analysis --output tmp/abstencion-http-estatico`
y la variante sin `--static-analysis` con carpeta `tmp/abstencion-http-sin-estatico`.

No desplegar ni modificar credenciales como parte de este bloque. Los demás
pendientes (429, presupuesto, herramientas, confianza, evaluación real y entrega)
permanecen en el diagnóstico y se abordan después de estabilizar este contrato.
