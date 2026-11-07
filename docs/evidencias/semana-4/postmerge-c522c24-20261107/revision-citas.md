# Revisión asistida de las citas del cierre

Versión c522c24. Revisión de los 18 hallazgos de informes completos, contra el código sintético del dataset y las seis reglas de knowledge/seguridad_python.md. Los 20 identificadores citados se resolvieron. Las categorías y las líneas respaldan los 18 hallazgos observados. Esta revisión asistida no es una segunda anotación humana independiente ni valida la ejecución de las correcciones.

| Caso | Ruta | Línea | Referencias | Pertinencia observada |
|---|---|---:|---|---|
| P01 | directa | 2 | seguridad_python-002, seguridad_python-004 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P01 | agente | 2 | seguridad_python-002 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P02 | agente | 2 | seguridad_python-002 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P02 | directa | 2 | seguridad_python-002 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P03 | directa | 2 | seguridad_python-002, seguridad_python-004 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P03 | agente | 2 | seguridad_python-002 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P04 | agente | 2 | seguridad_python-002 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P04 | directa | 2 | seguridad_python-002 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P07 | directa | 3 | seguridad_python-003 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P07 | agente | 3 | seguridad_python-003 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P08 | agente | 3 | seguridad_python-003 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P08 | directa | 3 | seguridad_python-003 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P09 | directa | 3 | seguridad_python-003 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P09 | agente | 3 | seguridad_python-003 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P13 | directa | 2 | seguridad_python-001 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P15 | directa | 2 | seguridad_python-001 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P16 | agente | 2 | seguridad_python-001 | Correspondencia con entrada externa y regla SQL/comandos/eval |
| P16 | directa | 2 | seguridad_python-001 | Correspondencia con entrada externa y regla SQL/comandos/eval |

La recomendación de ast.literal_eval en P13/P16 requiere límites de recursos y no implementa un evaluador aritmético general. Los placeholders SQL dependen del controlador. Se conserva el texto original generado; no se ejecutó ningún parche.

P06 ya no produce el falso positivo observado en la corrida previa. P16 se analiza correctamente por ambas rutas, mientras P13/P15 del agente son parciales por planificación. No atribuir una mejora global al ajuste de recuperación ni comparar F1 de 13 pares seleccionados por completitud con F1 de los 20 pares históricos. El proveedor, la latencia y la ausencia de huella inicial impiden una conclusión causal.
