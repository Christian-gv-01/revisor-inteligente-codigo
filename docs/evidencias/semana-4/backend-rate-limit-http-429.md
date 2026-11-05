# Evidencia de producción — Limitación HTTP 429

**Proyecto:** CODEGUARD / Revisor Inteligente de Código Seguro  
**Fecha de ejecución:** 2026-11-04 (hora local de Ecuador)  
**Entorno:** Railway, despliegue público HTTPS  
**Endpoint probado:** `POST https://revisor-inteligente-codigo-production.up.railway.app/api/v1/agente/analizar`

## Objetivo

Comprobar que la API impide superar el presupuesto de peticiones costosas antes de llegar al planificador Gemini.

## Procedimiento

Se enviaron 11 solicitudes POST consecutivas, con `Content-Type: application/json` y cuerpo deliberadamente inválido `{}`. Estas solicitudes deben rechazarse mediante validación de FastAPI, sin llamar al proveedor de IA. El endpoint del agente tiene un peso configurado de 3 unidades por solicitud.

## Resultados observados

| Solicitudes | Estado HTTP | Interpretación |
|---|---|---|
| 1–10 | 422 | Cuerpo inválido rechazado por validación |
| 11 | 429 | Solicitud bloqueada por el limitador |

**Resultado:** conforme para el **presupuesto global por proceso** configurado en 30 unidades cada 60 segundos. Los 10 primeros POST consumieron 30 unidades y el siguiente se bloqueó.

## Límites de la evidencia

- La captura de PowerShell la conserva el integrante y todavía debe agregarse al repositorio como archivo de imagen.
- Este resultado **no** demuestra que el límite de 10 unidades por dirección IP funcione de manera estable detrás del proxy Railway: las cuatro solicitudes iniciales devolvieron 422, 422, 422 y 422. Se debe revisar la identidad del cliente detrás del proxy sin confiar arbitrariamente en cabeceras proporcionadas por el usuario.
- Tampoco demuestra limitación compartida entre réplicas: el mecanismo actual es en memoria y por proceso.
- No se verificaron aquí el encabezado HTTP `Retry-After` ni el contenido JSON del 429; requieren una comprobación adicional en producción.
- No enviar pruebas de carga intensiva ni analizar código real para evaluar este límite; usar cuerpos inválidos y una frecuencia controlada.

## Uso en la entrega

Referencia para `docs/08-pruebas.md` (QA): incluir la captura, el método, los 11 códigos HTTP y el resultado esperado/observado. Mantener esta prueba separada de las pruebas de Gemini real y de evaluación RAG.
