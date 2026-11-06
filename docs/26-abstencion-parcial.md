# Abstención explícita y conservación parcial de hallazgos

Fecha: 6 de noviembre de 2026. Base: `b7431c1`.
Rama: `codex/abstencion-hallazgos`.

## Problema y comportamiento corregido

El backend calculaba el estado público a partir de metadatos internos sin
normalizar `estado="abstenido"` de Gemini. Una lista vacía con abstención podía
aparecer como análisis terminado y perder el motivo. Ahora se conserva la
abstención, se descartan los hallazgos contradictorios y se utiliza un mensaje
de respaldo cuando el modelo no proporciona uno.

La ruta directa devolvía abstención global ante cualquier cita inválida.
Ahora comparte la validación individual con el agente: los hallazgos con citas
verificables sobreviven, los demás se omiten y el informe se marca `parcial`,
con un mensaje de revisión incompleta. Si ninguno sobrevive, se abstiene.
Una lista vacía expresamente analizada sigue siendo `analizado`.

El agente conserva su requisito adicional de fragmento literal de una línea
y sus controles de ubicación. La ruta directa mantiene la compatibilidad con
hallazgos sin `fragmento_codigo`. No se agregan campos al contrato público ni
se cambia la política de severidad.

ZIP/GitHub propagan el estado parcial sin confundir la omisión documental con
indisponibilidad del proveedor. Un parcial con fuentes conserva los hallazgos
verificados y permite consultar IA para el siguiente archivo. Si el proveedor
falla realmente, la respuesta de respaldo no tiene fuentes RAG y se omiten
nuevos intentos dentro del mismo lote, manteniendo los resultados estáticos.

## Relación con la ficha del ingeniero

Se inspeccionaron visualmente las cinco páginas del archivo aportado por Christian,
`revision 5_11.pdf`. La p. 4 identifica como pendiente la abstención global de la
ruta directa; la p. 5 indica que la revisión fue estática sobre `65675e2`.
La fecha de impresión visible es 6 de noviembre. Este cambio atiende ese defecto
y añade la preservación de abstención explícita detectada en la revisión propia.

Las otras observaciones de la ficha siguen separadas: reintento 429,
severidad × confianza, presupuesto confirmado ZIP/GitHub, decisiones de búsqueda
y ampliación del agente, comparación real de veinte casos por ambas rutas,
consolidación documental y PDF/ZIP finales. No se recalculan los porcentajes
de avance del docente ni se declara entrega completa.

## Verificación

Evidencias: [resultados de esta ejecución](evidencias/semana-4/abstencion-parcial-20261106/README.md).

Las regresiones nuevas se ejecutaron antes de modificar el código productivo:
21 fallaban y seis pasaban. La causa observada fue la pérdida del estado de
abstención, el rechazo global de citas y la adaptación HTTP sin estado parcial.
Después se añadieron tres pruebas de compatibilidad/cortacircuito de lotes.

Las pruebas HTTP de backend cubren las cinco modalidades con la síntesis y
validación reales, sustituyendo Gemini y la descarga externa GitHub. La
planificación del agente se sustituye en esos casos: no se mide su calidad.
La integración frontend/API usa ChromaDB real y Ruff/Bandit reales cuando están
activados, con Gemini/GitHub externos simulados. No hubo llamadas reales a IA.

La verificación inicial encontró una aserción de ruta específica de Linux en
`test_correcciones_integracion.py`. Se cambió a comparación de objetos `Path`,
para validar la misma ubicación en Windows y Linux; no cambia la configuración
de SQLite en producción.

La revisión independiente no encontró bloqueos. Se incorporó su sugerencia de
probar un lote con parcial documental, fallo posterior y respaldo estático del
tercer archivo. El frontend conserva la advertencia conocida de bundle >500 kB.

No se realizó despliegue ni evaluación nueva contra Gemini/Railway. Los resultados
de este bloque acreditan contratos y regresiones locales, no precisión del modelo.
