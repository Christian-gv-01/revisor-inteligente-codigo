# Integración HTTP conjunta

Fecha: 30 de octubre de 2026.

Se ejecutó `eval/run_integration.py` contra una instancia temporal del FastAPI real del proyecto y ChromaDB local real. Solo el cliente externo de IA se sustituyó por respuestas controladas. No se utilizó una clave real ni se hizo una llamada externa de IA.

- `resultado-integracion.json`: procedencia, configuración, 9 pruebas aprobadas y comprobación HTTP del evaluador.
- `vitest-integracion.json`: resultados detallados de las nueve pruebas.
- `respuesta-api-controlada.json`: respuesta real de FastAPI con fuentes de ChromaDB y un hallazgo del proveedor simulado.
- `frontend-http.txt`: salida del proceso de integración del frontend.
- `frontend-unitarias.txt`: 58 aprobadas y 9 omitidas intencionadamente sin el servidor temporal.
- `frontend-lint.txt`: ESLint sin errores.
- `backend-pruebas.txt`: 58 pruebas aprobadas del backend.
- `evaluador-pruebas.txt`: 10 pruebas aprobadas del evaluador.

La suite dedicada ejecuta las nueve comprobaciones omitidas en la suite habitual. El servidor añade `X-Integration-Provider: stub`; las pruebas verifican ese identificador antes de enviar código, para evitar que se use accidentalmente un proveedor real.

No derivar métricas de calidad de IA de estas respuestas controladas. Las métricas reales de recuperación se conservan en `../rag-20-casos/`; la ejecución contra el backend sin configurar se conserva en `../api-sin-configurar/`.

[Explicación de las integraciones](../../../integracion-frontend-evaluacion.md).
