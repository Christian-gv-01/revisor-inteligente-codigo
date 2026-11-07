# Comparación de rutas

Revisión declarada por el operador: `8e66b2cc3f10b67589edd3714de17dcc8246d729`.

Esquema estable durante la corrida: True. Si es falso, no tratar la comparación como una versión estable.

Pares con informe completo en ambas rutas: 20 de 20.

| Ruta | Completos | Aciertos / total | TP | FP | FN | Precisión | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| directa | 20 | 0.95 | 11 | 0 | 1 | 1.0 | 0.9166666666666666 | 0.9565217391304348 |
| agente | 20 | 0.75 | 8 | 1 | 4 | 0.8888888888888888 | 0.6666666666666666 | 0.7619047619047619 |

TP/FP/FN y métricas de esta tabla usan únicamente los mismos pares completos. Los estados y latencias de todas las solicitudes están en JSON/CSV.

Configuración pública completa declarada: False. Si contiene valores no verificados, la corrida es exploratoria, no una comparación bajo configuración totalmente controlada.

Una corrida pequeña no demuestra generalización ni causalidad. Las citas se resuelven por ID; su pertinencia y los parches requieren revisión humana.
La revisión del servidor y su configuración son declaradas por el operador, no atestadas por OpenAPI. Igualdad del esquema no garantiza igualdad de código.
El uso numérico procede de la cabecera del servidor y de los metadatos del SDK, no de una factura. Si falta algún contador o hay intentos sin respuesta, se conserva null; no inferir ahorro ni tokens desde el número de pasos. Cobertura y sumas parciales están en JSON.
