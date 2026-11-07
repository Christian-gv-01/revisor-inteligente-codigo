# Comparación de rutas

Revisión declarada por el operador: `c522c24f0efcfa7ee4e7411a66fcaa1a612dd740`.

Esquema estable durante la corrida: True. Si es falso, no tratar la comparación como una versión estable.

Pares con informe completo en ambas rutas: 13 de 20.

| Ruta | Completos | Aciertos / total | TP | FP | FN | Precisión | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| directa | 17 | 0.85 | 8 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| agente | 14 | 0.7 | 8 | 0 | 0 | 1.0 | 1.0 | 1.0 |

TP/FP/FN y métricas de esta tabla usan únicamente los mismos pares completos. Los estados y latencias de todas las solicitudes están en JSON/CSV.

Configuración pública completa declarada: False. Si contiene valores no verificados, la corrida es exploratoria, no una comparación bajo configuración totalmente controlada.

Una corrida pequeña no demuestra generalización ni causalidad. Las citas se resuelven por ID; su pertinencia y los parches requieren revisión humana.
La revisión del servidor y su configuración son declaradas por el operador, no atestadas por OpenAPI. Igualdad del esquema no garantiza igualdad de código.
El uso numérico procede de la cabecera del servidor y de los metadatos del SDK, no de una factura. Si falta algún contador o hay intentos sin respuesta, se conserva null; no inferir ahorro ni tokens desde el número de pasos. Cobertura y sumas parciales están en JSON.
