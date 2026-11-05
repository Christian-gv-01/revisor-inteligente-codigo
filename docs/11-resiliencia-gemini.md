# CODEGUARD · Resiliencia cuando Gemini no responde

## Incidente reproducido en Railway

En las pruebas públicas del 5 de noviembre de 2026, después de resultados HTTP 200 en ZIP y archivo Python, Gemini devolvió errores HTTP 504 y 503. Los reintentos del SDK no garantizan disponibilidad. El backend no debe descartar alertas locales por un fallo externo.

## Política propuesta (rama de trabajo, NO desplegada aún)

1. **Ejecutar Ruff/Bandit antes de consultar Gemini**: solo analizan el código como dato, sin ejecutarlo.
2. Si Gemini responde con éxito, conservar hallazgos Gemini/RAG y resultados estáticos en campos separados.
3. Si Gemini falla (502/503/504) pero alguna herramienta estática terminó, devolver HTTP 200 con `estado="parcial"`, `hallazgos=[]`, `fuentes=[]`, `analisis_estatico` y mensaje explícito sobre la indisponibilidad de IA. Esto **no significa que el código sea seguro ni que haya concluido la auditoría de Gemini**.
4. Si las herramientas estáticas no están disponibles, conservar el código HTTP de error (no fingir éxito).
5. En ZIP/GitHub: cuando la primera consulta a Gemini falla, no repetir consultas Gemini con todos los archivos restantes de esa misma petición. Los otros archivos reciben análisis estático con estado `parcial`.
6. No inventar equivalencias OWASP/CWE ni referencias cuando solo hay una alerta Ruff/Bandit.

## Contrato y limitaciones

- `RespuestaAnalisis.estado` admite `analizado | abstenido | parcial`. Las respuestas agregadas ZIP/GitHub también admiten `parcial`.
- En los resultados parciales, la lista `hallazgos` de Gemini queda vacía porque **no** se produjo una evaluación de IA con citas.
- El frontend debe distinguir claramente `analisis_estatico.hallazgos` de `hallazgos` y no mostrar «Sin vulnerabilidades» ante `estado=parcial`.
- No existe garantía de que Ruff/Bandit identifiquen todos los problemas; estas herramientas son complementarias.
- Las solicitudes pueden seguir tardando demasiado antes del fallback si Gemini agota sus dos intentos y el timeout configurado. Próximo trabajo: validar presupuesto de tiempo y latencia máxima, especialmente ZIP.
- La protección actual de concurrencia es por proceso; una degradación estática no convierte la API en un servicio ilimitado.
- No desplegar sin pruebas en Windows, GitHub Actions, revisión de QA y frontend.

## Pruebas automatizadas

`backend/tests/test_static_resilience.py` verifica: error Gemini 503 con resultado estático, error conservado sin herramientas locales, estado correcto con Gemini operativo y supresión de consultas adicionales para ZIP/GitHub.

## Actividad necesaria de frontend

Mostrar banner «Análisis parcial: Gemini no disponible. Resultados Ruff/Bandit disponibles», con estados de cada herramienta y exportación JSON completa. No sumar automáticamente alertas de ambos motores como vulnerabilidades únicas verificadas.
