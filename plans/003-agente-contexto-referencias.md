# Herramientas contextuales y finalización anticipada del agente

Base solicitada: `605d142ff8f643d755689e257c649e0a9e79a8ea`. Rama nueva
`codex/agente-contexto-referencias`. CI consultada antes de comenzar: los seis
workflows aprobados, incluida integración HTTP (runs 42303489327 y
42303489443 para HTTP/backend). No modificar frontend, priorización,
presupuestos del PR42, confirmación ZIP/GitHub ni archivos del evaluador PR41.

## Diseño del contrato

Solicitud optativa `version_herramientas: "2"`; defecto "1" conserva los nombres
y la forma de trazas que consume el frontend actual. Ambas versiones mantienen
1..3 pasos totales, incluida inspección inicial obligatoria; como máximo dos
decisiones y una síntesis, sin aumentar llamadas/plazo del PR42.

Decisiones con herramienta, motivo y argumentos: ampliar_contexto requiere
linea estrictamente entera 1..12000 y existente en el código real;
buscar_referencia requiere categoria en ejecucion_codigo/inyeccion_sql/
inyeccion_comandos/inyeccion/credenciales/rutas. Otras herramientas y finalizar
requieren argumentos vacíos. Se rechazan extras, URLs y coerción de tipos.

Ampliar solo devuelve una ventana literal de radio3, máximo siete líneas, cada
una de hasta500 caracteres, con numeración y truncamiento explícito. Buscar
usa una consulta fija por categoría sobre ChromaDB, máximo dos fuentes de
seguridad y2000 caracteres por fragmento; nunca recibe URLs ni hace fetch de
URLs. Metadatos son referencia no confiable; no certifican pertinencia semántica.

Paso y decisión registran argumentos validados. Los resultados completos y
acotados se envían a la siguiente decisión. EvidenciaRevision conserva contexto
de código y resultados de búsqueda para enviarlos a la síntesis; las fuentes
efectivamente buscadas participan en el allowlist RAG final (tope seis existente).
Conservar validación de citas, anclaje y estados parciales. No reemplazar el
corpus ni el prompt de base; añadir instrucciones específicas versionadas en código.

Finalizar detiene inspecciones adicionales, registra motivo público y mantiene
una síntesis final. En v2 se expone terminacion: finalizacion_anticipada,
max_pasos o herramienta_repetida. Repetir la misma herramienta/argumentos no se
ejecuta; argumentos diferentes pueden ocupar otro paso dentro del mismo tope.
Fallos de herramienta/RAG/plazo preservan traza y respaldo del contrato actual.

## Secuencia

- [x] Pruebas primero de argumentos/límites y herramientas de solo lectura.
- [x] Implementar módulo tipado acotado y revisar independientemente.
- [x] Integrar planificación, despacho y trazabilidad v2; mantener v1 por defecto.
- [x] Integrar evidencia y citas buscadas en recuperación/síntesis final.
- [x] Probar argumentos inválidos, repetición, límites de pasos/llamadas/plazo,
  resultados en siguiente decisión/síntesis y finalización anticipada.
- [x] Generar ejemplos JSON reproducibles de solicitud, decisiones y respuestas
  v2, error/degradación y compatibilidad v1 para coordinación visual.
- [x] Backend, QA/eval existentes, frontend sin cambios e integración HTTP
  activada/desactivada; revisión general, evidencias y PR en borrador.

Comandos: backend/.venv/Scripts/python.exe -m pytest tests -q (cwd backend),
-m pytest qa eval -q (raíz); npm test/lint/build (frontend); run_integration.py
con/sin --static-analysis en carpetas nuevas tmp/agente-v2-http-*. Sin llamadas
reales a Gemini ni despliegue. No se afirma mejora de calidad sin evaluación real.
