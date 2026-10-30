# Evidencias de frontend y evaluación — semana 3

Fecha: 30 de octubre de 2026. Informe: [07-evaluacion.md](../../07-evaluacion.md).

- `00-captura-original-usuario.png`: captura aportada por el usuario, anterior a estos cambios.
- `01-fuentes-escritorio.jpg`, `02-fuentes-movil.jpg`: componente real con fixture identificado como simulado. Móvil: viewport real 390 × 844; sin desbordamiento horizontal.
- `03-abstencion-movil.jpg`, `04-referencia-ausente.jpg`: estados simulados de abstención y referencia sin metadatos.
- `05-zip-parcial.jpg`: aviso de que un archivo del proyecto no pudo analizarse.
- `rag-20-casos/`: recuperación real de 20 casos, JSON original, CSV y resumen. Cuatro fragmentos locales de seguridad, sin Gemini y sin colección de contexto de proyecto.
- `api-sin-configurar/`: 20 solicitudes reales, 20 errores HTTP 503 por falta de configuración de IA. No hay métricas de calidad de respuestas.
- `api-diagnostico.json`: salud correcta y mensaje «Proveedor de IA no configurado» de una solicitud de diagnóstico adicional.
- `rag-ejecucion.txt`, `api-ejecucion.txt`: salida del ejecutor para ambas corridas.
- `ingesta-local.txt`: ingesta de los cuatro fragmentos y consulta de comprobación.
- `frontend-pruebas.txt`, `frontend-lint.txt`, `frontend-build.txt`: pruebas, análisis estático y compilación.
- `backend-pruebas.txt`: suite existente ejecutada desde `backend/`.
- `evaluador-pruebas.txt`, `dataset-validacion.txt`: comprobación independiente de fórmulas y conjunto.
- `entorno-python.txt`: versiones realmente instaladas para reproducir este entorno.

Los archivos `comparacion-ingesta.txt`, `evaluacion-rag.txt` y `pruebas-llm-abstencion.txt` ya existían en `main`. Se preservan; no se atribuyen a esta corrida ni se mezclan sus métricas con las actuales.

Las capturas se reproducen desde `frontend/tests/fuentes-preview.html` con Vite iniciado. Las respuestas del fixture no forman parte del dataset ni de las métricas RAG/API.
