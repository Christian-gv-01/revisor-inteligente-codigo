# Severidad derivada y herencia contextual verificable

## 1. Objetivo

Implementar una política determinista de severidad derivada y herencia contextual que permita combinar los resultados de Bandit y Ruff con los hallazgos generados por Gemini.

El objetivo es mejorar la consistencia de la clasificación de vulnerabilidades, conservando la severidad original, la confianza proporcionada por Bandit y la trazabilidad de las reglas estáticas que justifican una elevación.

La decisión final de severidad corresponde al backend y no a una clasificación inventada por el modelo de IA.

## 2. Política de derivación

La lógica se centraliza en:

`backend/app/services/severidad.py`

La configuración se encuentra en:

`backend/app/config/severidad.yaml`

### Reglas de Bandit

| Severidad original | Confianza | Severidad derivada |
|---|---|---|
| Crítica | Alta, media o baja | Crítica |
| Alta | Alta | Crítica |
| Alta | Media | Alta |
| Alta | Baja | Alta |
| Media | Alta, media o baja | Media |
| Baja | Alta, media o baja | Baja |

Las políticas adicionales son:

- La confianza desconocida conserva la severidad original.
- Ruff conserva su severidad original.
- Las herramientas sin derivación conservan su severidad original.
- No se inventa confianza cuando el analizador no proporciona ese dato.

La severidad derivada es una clasificación operativa y determinista, no una probabilidad estadística de explotación.

## 3. Configuración YAML

La política se externalizó para facilitar su mantenimiento sin modificar directamente las reglas del servicio.

El archivo YAML contiene:

- Versión de la configuración.
- Matriz de severidad de Bandit.
- Niveles de confianza.
- Política para confianza desconocida.
- Política para herramientas sin derivación.

El servicio carga la configuración mediante `yaml.safe_load()` y valida su estructura y sus valores.

La dependencia PyYAML está declarada en:

`backend/requirements.txt`

## 4. Identificación y vinculación de evidencia

La construcción de evidencia se encuentra en:

`backend/app/services/evidencia.py`

Las reglas estáticas de Bandit y Ruff se proporcionan al proceso de análisis con información suficiente para identificar su procedencia y ubicación.

La herencia no se autoriza únicamente porque una regla esté cerca de un hallazgo o pertenezca a la misma ventana contextual.

Para que una regla pueda justificar una elevación:

1. Debe haber sido proporcionada por el backend.
2. Debe tener un identificador válido.
3. Gemini debe citar ese identificador en `reglas_evidencia`.
4. La regla debe corresponder exactamente a la línea del hallazgo.
5. La relación debe poder verificarse mediante la evidencia original.

Las reglas estáticas no se consideran citas documentales RAG.

## 5. Herencia verificable de severidad

La lógica se encuentra en:

`backend/app/services/severidad.py`

La función `heredar_severidad_contextual()` aplica la herencia únicamente cuando existe una relación verificable entre el hallazgo y una regla estática citada.

Criterios:

- Se conserva la severidad más alta.
- Nunca se reduce una severidad existente.
- Se descartan identificadores desconocidos o ambiguos.
- No se aplica herencia por proximidad de líneas.
- Los hallazgos sin vínculos verificables conservan su severidad original.
- Se mantiene la trazabilidad de las reglas que justifican la elevación.

La integración se realiza desde:

`backend/app/services/llm.py`

## 6. Auditoría y trazabilidad

La implementación incorpora información de auditoría en:

`backend/app/models/analisis.py`

Se conserva la información necesaria para reconstruir:

- La severidad original generada por Gemini.
- Las reglas estáticas citadas.
- La herramienta de procedencia.
- La ubicación de la evidencia.
- La severidad original de la regla.
- La confianza proporcionada por Bandit.
- La severidad derivada.
- La justificación de la herencia aplicada.

Esto permite verificar por qué un hallazgo recibió una severidad superior y evita depender exclusivamente de la explicación generada por el modelo.

## 7. Integración con Gemini

El flujo de procesamiento se integra en:

`backend/app/services/llm.py`

La secuencia general es:

1. Recibir el código y los resultados de los analizadores estáticos.
2. Construir la evidencia disponible.
3. Enviar el contexto pertinente a Gemini.
4. Validar los hallazgos generados.
5. Comprobar las reglas estáticas citadas.
6. Aplicar la herencia verificable.
7. Conservar la información de auditoría.
8. Priorizar los hallazgos con la severidad resultante.

Gemini participa en el análisis, mientras que el backend controla la aplicación de las reglas deterministas.

## 8. Archivos principales implementados

- `backend/app/config/severidad.yaml`
- `backend/app/services/severidad.py`
- `backend/app/services/evidencia.py`
- `backend/app/services/llm.py`
- `backend/app/models/analisis.py`
- `backend/tests/test_severidad_derivada.py`
- `backend/tests/test_severidad_herencia.py`
- `backend/tests/test_herencia_llm_integrada.py`
- `backend/tests/test_contrato_herencia_frontend.py`

También se actualizaron los workflows de pruebas del backend y de integración.

## 9. Validación automatizada

Se realizaron pruebas específicas de severidad, herencia, integración y contrato con el frontend.

Resultados locales registrados:

- 42 pruebas específicas de integración aprobadas.
- 567 pruebas de la suite completa del backend aprobadas.
- `git diff --check` correcto.

Entorno de validación:

- Windows.
- Python 3.13.2.
- pytest 9.1.1.

También se corrigió la lectura del fixture JSON para utilizar codificación UTF-8 explícita, evitando diferencias dependientes de la configuración regional de Windows.

## 10. Alcance y limitaciones

Los resultados acreditan la ejecución satisfactoria de las pruebas automatizadas locales.

No acreditan por sí solos:

- Una mejora estadística demostrada de precisión, recall o F1.
- Una reducción demostrada del consumo de tokens.
- Una evaluación completa con Gemini real en producción.
- Un despliegue satisfactorio mediante Docker.
- La aceptación definitiva del cambio por el equipo.

La validación de Docker permanece pendiente porque Docker CLI no está disponible en el entorno local utilizado.

## 11. Estado de integración

El trabajo se integró sobre la referencia del PR #55.

Commit adicional:

`cf82e84`

Mensaje:

`test(severidad): ampliar cobertura de matriz y UTF-8`

Este commit se publicó en la rama remota:

`codex/herencia-verificable-cierre`

La documentación se encuentra pendiente de incorporación al commit correspondiente.

Quedan pendientes:

- Revisión final de la documentación.
- Validación mediante Docker.
- Revisión del equipo.
- Confirmación de aceptación e integración definitiva del Pull Request.