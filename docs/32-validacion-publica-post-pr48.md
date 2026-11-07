# Validación pública después del PR #48

## Revisión y alcance

Revisión probada: `467d00e0d56a98cd758f382a5c713737eb490845`, fusión del PR #48. Se verificaron en GitHub los seis workflows disparados por push a esta revisión: backend, frontend, captura estática multiplataforma, Docker, integración HTTP y secretos, todos completados con éxito.

En el panel de Railway se observó el deployment `3eb5a324-4385-42f7-8324-1e160eb5261e` como **Active / Deployment successful** y su enlace de origen apuntaba exactamente a ese commit. Se contrastó de nuevo el enlace al finalizar la matriz. Esta es una observación del panel: `/health` informa `0.1.0`, sin SHA, y OpenAPI tampoco atestigua la revisión del servidor.

URL probada: https://revisor-inteligente-codigo-production.up.railway.app

## Pruebas públicas

Se ejecutó el script existente, sin modificarlo:

```sh
python scripts/pruebas_produccion.py --base-url https://revisor-inteligente-codigo-production.up.railway.app --usar-proxy-entorno --output tmp/publico-completo-467d00.json
```

El cliente respeta diez unidades por ventana de 61 segundos; las pausas de presupuesto pueden quedar incluidas en `duracion_ms` del script. Ese campo no es una medición aislada de latencia del servidor.

La matriz comprueba salud, OpenAPI, errores controlados, límites y validación de archivos, ZIP y URL GitHub, y previsualización AST en modo lectura. No envía análisis válidos a Gemini, no ejecuta el código recibido y no modifica archivos del usuario. Los cuerpos de error se omiten de la evidencia.

El esquema público anuncia `version_herramientas` con versiones `1` y `2`; la versión predeterminada sigue siendo `1`. Esta comprobación de compatibilidad no sustituye un recorrido completo del agente v2 con Gemini real.

Evidencias: [matriz pública](evidencias/semana-4/post-pr48-20261107/pruebas-publicas.json) y [despliegue y CI](evidencias/semana-4/post-pr48-20261107/despliegue-ci.json).

Resultado: **26/26 escenarios aprobados**, cero fallos. El detalle de cada aserción y su duración está en el JSON enlazado.

## Preparación de la comparación

Se volvió a ejecutar `python eval/comparar_rutas.py --validar`: veinte casos, cuarenta solicitudes previstas, agente v2 explícito, cero solicitudes realizadas. SHA-256 del dataset: `9908373c5650a9fb87992a50d56a05636c0dc2d615a25c0189c02b31e85d85ac`. Las cuarenta pruebas unitarias del comparador y del contrato aprobaron.

Se leyeron únicamente valores públicos del panel del deployment: modelo `gemini-3.5-flash-lite`, salida máxima de síntesis `2048`, timeout LLM `20` segundos y distancia máxima RAG `0.75`. Estos cuatro valores no son una atestación completa de la configuración efectiva ni del contenido del volumen Chroma.

## Pendientes de cierre

- Congelar configuración efectiva, prompts y corpus realmente ingerido; el archivo de conocimiento en Git no demuestra el contenido del índice persistente.
- Ejecutar veinte pares directa/agente v2 sobre una misma revisión, con presupuesto y ventana sin otros despliegues, y revisar citas y resultados humanos. Conservar errores y parciales, sin seleccionar solo los casos favorables.
- Confirmar el recorrido público y decidir la activación de funciones que siguen deshabilitadas; esta validación no cambió flags ni configuraciones.
- Incorporar los resultados finales a la presentación/PDF, completar instalación por otro integrante y ensayo cronometrado reales, y regenerar el ZIP desde el commit final.

Este registro no acredita una nueva medición de calidad de Gemini, una comparación final entre rutas, una instalación humana ni un ensayo oral. No modifica código, main o producción.
