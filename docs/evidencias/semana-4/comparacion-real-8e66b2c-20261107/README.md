# Comparación real directa/agente: 8e66b2c

Corrida del 7 de noviembre de 2026, cuarenta solicitudes sobre la misma versión
activa de Railway, veinte por ruta, sin reintentos del evaluador. Proveedor
Gemini real mediante el servidor. Dataset y etiquetas no modificados.

- `resultados.json`, `resultados.csv`, `comparacion.md`: resultados completos.
- `checkpoint.json`: secuencia conservada durante la ejecución.
- `configuracion-publica.json`: parámetros públicos y límites; no secretos.
- `procedencia-despliegue.json`: verificación de versión y logs observados.
- `revision-citas.md`: revisión asistida de pertinencia y análisis de errores.
- `pruebas-publicas.json`: matriz HTTP segura, ejecutada después de la comparación.

20/20 pares completos. Directa TP/FP/FN 11/0/1 y F1 0,9565; agente 8/1/4 y
F1 0,7619. Los datos se conservan aunque no favorezcan al agente. Se observó
pérdida de cobertura cuando una búsqueda de categoría sustituía la recuperación
base; el candidato posterior la corrige y no se atribuye esta corrida.

La huella del índice activo no se verificó. La configuración se declara
exploratoria respecto a ese control. Referencias resolubles no son pertinencia
semántica ni certificación de correcciones ejecutables. La revisión es asistida,
no validación independiente de expertos ni aprobación académica.
