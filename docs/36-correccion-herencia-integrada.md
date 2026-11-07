# Corrección e integración de la severidad derivada

Base de la contribución: PR #54, `44c8ef0834e4dd2b00210aacb97a5f029ec77aec`, sobre
main `ba6fa4f598954ebcf1c4bffa1f874e75d2caaf2a` (PR #53). Se conserva la autoría y
el historial de la entrega original; esta revisión completa su validación.

## Problemas reproducidos antes del cambio

| Caso sintético | Resultado original |
|---|---|
| Regla Bandit B602 crítica en línea 10; hallazgo independiente en línea 12 | Se elevaba a crítica por compartir ventana |
| Mismas ventanas en orden `[10,11]` y `[11,10]`; hallazgo en línea 11 | La severidad variaba de baja a crítica por deduplicar solo la primera asociación |

Las 554 pruebas originales y el CI del PR #54 aprobaban, pero no cubrían estas
dos regresiones. No se utilizó Gemini real para reproducirlas.

## Comportamiento corregido

- Matriz completa en `backend/app/config/severidad.yaml`, sin nuevas dependencias.
- Identidad estática por herramienta, regla, línea y columna.
- Herencia únicamente por ID ofrecido, no ambiguo, citado por el hallazgo y en su
  misma línea validada. Ni proximidad, categoría ni orden autorizan elevaciones.
- Las ventanas conservan sus asociaciones con orden estable. La herencia usa las
  reglas ofrecidas, por lo que finalizar sin ampliar contexto no elimina controles.
- Severidad original del modelo y reglas aplicadas conservadas en respuesta,
  pantalla y exportación; nunca se reduce severidad.
- Auditoría calculada solo por el servidor: no forma parte del esquema solicitado
  a Gemini y se descarta incluso si el modelo intenta enviarla malformada.
- Vínculos inválidos se omiten, conservando hallazgos válidos y marcando parcial.

La política es una clasificación operativa. La coincidencia de línea e ID no
certifica pertinencia semántica ni explotabilidad. Una llamada multilínea no
hereda por inferencia automática. Esas limitaciones requieren revisión humana.

## Validación local

- 646 pruebas Python aprobadas: 567 backend y 79 QA/evaluadores.
- 146 pruebas frontend aprobadas; 24 HTTP omitidas en suite unitaria.
- Lint y compilación correctos; advertencia de bundle grande preexistente.
- HTTP con FastAPI, ChromaDB y Ruff/Bandit reales y proveedores simulados: 24/24
  con análisis estático y 19/19 aplicables sin él (cinco omitidas). Los nuevos
  casos de navegador quedan a la comprobación CI.
- El contrato de auditoría que usa React se regenera desde FastAPI con SDK, RAG y
  estático simulados. No son resultados de calidad de Gemini.

La verificación local desactiva telemetría y bloquea conexiones/DNS externos,
conservando loopback para las pruebas HTTP. Se usan pesos ONNX ya disponibles;
no se necesitan claves reales ni descargas de modelos para esa ejecución.

Se añaden al navegador del agente dos casos: herencia desde Bandit real con
modelo simulado, incluida descarga y cotejo del JSON; y rechazo de la elevación
por una regla de otra línea. No hay Chromium local: el CI debe ejecutar esos
casos, sin trasladar resultados de ramas anteriores como comprobación nueva.

## Estado y siguiente paso

No se han cambiado main, flags ni producción ni se han ejecutado análisis con
Gemini real. Tras revisar el candidato, integrar una sola versión, verificar
configuración e índice efectivos y ejecutar la comparación real de veinte pares
y los seis pares del planificador. Luego actualizar PDF/PPTX, revisar citas y
generar el ZIP final. La implementación no demuestra por sí sola una mejora de
precisión, recall, F1 ni consumo de tokens.
