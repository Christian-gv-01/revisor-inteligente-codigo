# Severidad derivada y herencia contextual

## 1. Objetivo

Implementar la política de severidad derivada solicitada por el docente,
conservando la severidad original, la confianza proporcionada por Bandit
y la trazabilidad de las reglas vinculadas al contexto.

## 2. Política de derivación

La lógica se centraliza en:

`backend/app/services/severidad.py`

Regla implementada:

- Bandit con severidad alta y confianza alta: severidad derivada crítica.
- Las demás combinaciones conservan la severidad original.
- No se inventa confianza cuando el analizador no proporciona ese dato.
- Ruff y el informe de IA no reciben confianza artificial.

La severidad derivada es una clasificación operativa y no una
probabilidad calibrada.

## 3. Vinculación contextual

La construcción de evidencia se encuentra en:

`backend/app/services/evidencia.py`

Las reglas estáticas pueden vincularse con una inspección cuando
su línea pertenece a la ventana contextual de esa inspección.

Cada vínculo conserva la línea objetivo y la información de severidad
y confianza necesaria para aplicar la política.

No se considera que las reglas de herramientas sean citas RAG.

## 4. Herencia de severidad

La función:

`heredar_severidad_contextual()`

aplica la severidad derivada a los hallazgos de Gemini que coinciden
con la línea objetivo del vínculo contextual.

Criterios:

- Se conserva la severidad más alta.
- Nunca se reduce una severidad existente.
- Se conservan los hallazgos que no tienen vínculos.
- No se modifica directamente el objeto original del hallazgo.

La integración se realiza en:

`backend/app/services/llm.py`

La secuencia es:

1. Validar los hallazgos del informe.
2. Aplicar la herencia contextual.
3. Priorizar los hallazgos con la severidad resultante.

## 5. Archivos implementados

- `backend/app/services/severidad.py`
- `backend/app/services/evidencia.py`
- `backend/app/services/llm.py`
- `backend/tests/test_severidad_derivada.py`
- `backend/tests/test_severidad_herencia.py`

## 6. Validación automatizada

Rama de trabajo:

`feature/backend-severidad-derivada-20261107`

Resultados locales registrados:

- Compilación Python correcta.
- 29 pruebas específicas de severidad y herencia aprobadas.
- 44 pruebas de regresión aprobadas.
- 554 pruebas de la suite completa del backend aprobadas.
- `git diff --check` correcto.

Tiempo registrado de la suite completa: 21.98 segundos.

## 7. Alcance y limitaciones

Estos resultados acreditan la ejecución de las pruebas automatizadas
locales del backend.

No acreditan por sí solos:

- Una evaluación con Gemini real.
- Una mejora demostrada de precisión, recall o F1.
- Una reducción real del consumo de tokens.
- Un despliegue de esta implementación en producción.
- La aceptación definitiva del cambio por el equipo.

## 8. Estado de entrega

La implementación y sus pruebas están preparadas en la rama de trabajo.

Quedan pendientes:

- Actualizar la documentación general del agente.
- Revisar la coherencia de los documentos de coordinación.
- Revisar la presentación y sus evidencias.
- Crear el commit.
- Abrir el Pull Request.
- Obtener la revisión del equipo.
