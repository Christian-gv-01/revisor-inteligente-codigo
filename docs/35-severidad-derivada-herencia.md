# Severidad derivada y herencia contextual verificable

## Procedencia

Se conserva la entrega del compañero en PR #54, commit `44c8ef0834e4dd2b00210aacb97a5f029ec77aec`, basada en `ba6fa4f`. Esta revisión corrige dos casos reproducidos: elevación de un hallazgo por mera cercanía y pérdida de vínculos al cambiar el orden de ventanas.

## Política operativa

La matriz completa está en `backend/app/config/severidad.yaml`: cubre las cuatro severidades, tres confianzas y confianza desconocida. Bandit alta × alta deriva crítica; las demás combinaciones conservan la original. Ruff conserva su severidad. No se inventa confianza de IA ni se interpreta como probabilidad o explotabilidad demostrada.

`ReglaEvidencia` conserva severidad y confianza normalizadas de la herramienta, columna, severidad derivada e identidad `estatica-<SHA256>`. El identificador se calcula sobre la tupla JSON canónica herramienta/regla/línea/columna. No depende de las decisiones del modelo ni del orden de las ventanas. Identidades con metadatos contradictorios no autorizan herencia.

## Vínculo que autoriza la herencia

El modelo puede seleccionar IDs ofrecidos en `reglas_evidencia`. El backend exige:

1. ID existente y no ambiguo dentro de las reglas efectivamente ofrecidas.
2. Coincidencia con la línea del hallazgo, después de validar su fragmento literal y citas RAG.
3. Severidad derivada calculada por la política del backend, nunca aceptada del modelo.

Compartir ventana o categoría no es suficiente. Una regla de línea 10 no eleva un hallazgo de línea 12 aunque ambos aparezcan en la misma ventana. No se infieren asociaciones multilínea o semánticas. La selección explícita tampoco demuestra explotabilidad: sigue requiriendo revisión humana.

La herencia usa las reglas estáticas ofrecidas, no requiere que el planificador haya ampliado el contexto. Por tanto, finalizar temprano no suprime controles deterministas. Los vínculos de ventana se conservan por regla y contexto, con orden estable y límite de cuarenta, únicamente como trazabilidad; no autorizan elevaciones por sí solos.

## Conservación y auditoría

La severidad efectiva es la mayor entre la original del modelo y las reglas válidas citadas. Nunca se reduce. No se modifica el objeto recibido.

La respuesta conserva `severidad_original_modelo`, `reglas_evidencia` y `herencia_severidad`, con ID, herramienta, regla, ubicación, severidad original, confianza y derivada. El esquema generativo no solicita los campos de auditoría; cualquier intento del modelo de proporcionarlos se ignora antes de validar y el servidor los reconstruye.

Los vínculos desconocidos, ambiguos o de otra línea se omiten sin eliminar hallazgos con citas y fragmentos válidos. El informe del agente queda parcial para señalar esa limitación. La ruta directa, sin evidencia de herramientas entregada a síntesis, no hereda ni publica auditoría inventada.

React valida la estructura y coherencia de la auditoría, muestra el ajuste y conserva los mismos datos al exportar JSON. No recalcula la matriz de negocio en el navegador ni presenta la clasificación como certeza de vulnerabilidad.

## Límites de cobertura

La selección de evidencia mantiene el máximo de cuarenta reglas ya existente. Una regla no ofrecida no puede autorizar herencia. Los identificadores son trazabilidad, no secretos ni firmas de seguridad. No sustituyen referencias documentales RAG.

El emparejamiento conservador por línea puede omitir herencia en una llamada multilínea. Tampoco prueba que toda regla citada corresponda semánticamente al hallazgo, especialmente si hay varias expresiones en una misma línea; eso pertenece a la revisión humana.

## Validación y estado

La entrega original registró 554 pruebas backend. La corrección añade regresiones de orden, cercanía, ausencia/ambigüedad de IDs, conservación de originales, auditoría fabricada, SDK simulado, contrato FastAPI y presentación/exportación en React. Los resultados de la combinación y su procedencia están en [36-correccion-herencia-integrada.md](36-correccion-herencia-integrada.md).

No son una evaluación con Gemini real ni demuestran mejora de precisión, recall, F1 o consumo. La comparación final debe ejecutarse después de revisar e integrar este candidato y verificar una única revisión desplegada y su corpus/configuración.

## Aportes posteriores y contraste

El compañero publicó cf82e84 (doce combinaciones y UTF-8) y
113347c6da9c52c614a6212c0ae6b1742141da6e (ampliación documental) en la rama
del PR #55 después de su fusión. Las pruebas ya se incorporaron mediante PR #56.
Actualizar esa rama no vuelve a fusionar un PR cerrado. La ampliación se contrastó
con el código, conservando su explicación de matriz, secuencia y auditoría.

| Entrada | Comportamiento real del servicio |
|---|---|
| Bandit, confianza ausente/no reconocida | Columna desconocida del YAML, conserva severidad |
| Ruff | Matriz YAML sin inventar confianza |
| Herramienta o severidad no reconocida | ValueError; no hay fallback genérico silencioso |
| YAML ausente, incompleto o inválido | Error de configuración; no fabrica reglas de respaldo |

La política contiene version, bandit y ruff; desconocida es una columna de cada
fila Bandit. Los conteos Windows comunicados son históricos de otro entorno,
no sustituyen los 583 backend comprobados en CI de PR #56 ni una evaluación real.
