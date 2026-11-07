# Validación pública de c522c24

Fecha 7 de noviembre de 2026. Railway deployment 750ebee5-57bf-4cb2-8b81-ad50c1606ebc enlazó la revisión completa c522c24f0efcfa7ee4e7411a66fcaa1a612dd740 y mostró éxito antes de iniciar. Los ocho checks de main aprobaron. Se conserva el esquema estable y la configuración pública original, sin secretos.

## Archivos y denominadores

- comparacion-rutas/: cuarenta respuestas, veinte por ruta, AB/BA, Gemini real. Sin reintentos del evaluador, sin cambiar etiquetas y sin ejecutar código del usuario.
- planificador-ab/: doce primeras decisiones, seis pares sintéticos, Gemini real ejecutado dentro del contenedor con usuario codeguard. Ruff/Bandit en ambos grupos. Cinco pares comparables y un par con error 503. Dos decisiones distintas entre los cinco pares válidos. No es una medida de calidad de informes.
- flujo-real.json: nueve controles HTTP públicos, incluido consentimiento, rechazo, aprobación de ZIP y aprobación idempotente de copia revisada. La aprobación de proyecto expuso un contador incorrecto en c522c24, documentado y corregido separadamente en PR #57. Su cero no significa ausencia de generación; se conserva la evidencia original.
- presupuesto-publico.png: interfaz pública con API real y acceso visible al presupuesto.
- corpus-atestacion.json: seis reglas coinciden exactamente con documentos y metadatos del fuente. La misma huella de documentos/metadatos/embeddings se observó durante y después de las pruebas. No se verificó antes de la primera petición y se conserva corpus_sha256=null en la configuración inicial.
- revision-citas.md: revisión asistida, no humana independiente, de los 18 hallazgos completos y 20 IDs citados.

## Resultado de los cuarenta informes

| Medida | Directa | Agente v2 |
|---|---:|---:|
| Completos / total | 17/20 | 14/20 |
| Parciales / total | 3/20 | 6/20 |
| Acierto con informe completo / total | 17/20 | 14/20 |
| TP / FP / FN en 13 pares completos comunes | 8 / 0 / 0 | 8 / 0 / 0 |
| F1 solo en esos 13 pares | 1,000 | 1,000 |
| Media / p95 de todas las solicitudes | 10,34 / 21,07 s | 22,62 / 43,45 s |
| Intentos SDK reportados | 21 | 71 |
| Tokens totales | desconocidos | desconocidos |
| Suma de tokens solo en solicitudes con dato completo | 25.255 en 17/20 | 65.057 en 12/20 |
| Finalizaciones tempranas / total | no aplica | 8/20 |

Los pares P10, P11, P13, P14, P15, P18 y P20 permanecen en los resultados pero se excluyen únicamente de la métrica pareada por estar incompleta al menos una ruta. Cinco parciales del agente corresponden a planificación y uno a informe. El formato parcial conserva el respaldo estático y comunica la ausencia de dictamen generativo completo.

## Interpretación

La igualdad de F1 entre trece pares completos no demuestra que las rutas sean equivalentes en producción ni que el agente mejore respecto de la corrida histórica. El agente mostró menor completitud y mayor tiempo e intentos. La corrida previa de 8e66b2c se conserva con veinte pares completos y F1 0,957/0,762. P16 con eval ahora obtuvo un hallazgo respaldado en ambas rutas, pero otros casos eval del agente fueron parciales. No se selecciona la corrida más favorable ni se rellenan consumos desconocidos con cero.

El conjunto es propio, pequeño y conocido durante el desarrollo, sin holdout ni repetición estadística. Las fuentes curadas tienen cobertura limitada. La huella inicial no estaba disponible. Son resultados exploratorios reproducibles por protocolo, sin conclusión causal ni generalización.

El A/B del planificador usó el evaluador SHA256 5ee4cf7f02cc11a234aa23f2e0072ea9c43c73b756f8d93e900dec1e39755c65 y dataset b5d74038241898a76a8834557d305378db8bd8f164ed3997af64b0f05b3222ef. Los tres archivos de salida se recuperaron de la consola y se verificó SHA256 del contenedor canónico de transferencia 6b1e87d031d387ab5a4e831d8c4b73f2ea73fbb96512e7c00b6d026675f94d8d. La clave permaneció en el entorno del servidor.

## Verificación posterior de PR #57

Railway activó 0a6707ba294829b9bb4a8e5c30db0b4403faa7bd en deployment
46dd6252-fa89-4552-b906-4f9bd1c64f26. Las ocho verificaciones de main aprobaron.
Una aprobación pública registró dos intentos, cero respuestas y resultado parcial:
el contador ya conserva los intentos fallidos y mantiene tokens desconocidos.
Repetir la misma decisión devolvió el cuerpo idéntico con cero intentos nuevos.
Ver consumo-corregido-publico.json. Esta prueba no sustituye la comparación de
c522c24 ni acredita éxito generativo en esa aprobación.

Recorrido adicional de interfaz en 0a6707b: SQL concatenado, un hallazgo y su fuente, dos decisiones Gemini visibles, Ruff/Bandit y acceso a previsualización. Captura agente-integrado-publico.jpg y recorrido-interfaz.json. No se añade al conjunto de evaluación.
