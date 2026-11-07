# Cierre de la revisión 7 — 7 de noviembre de 2026

Base de trabajo: `32149601450fd632bd9f843e201908c7e990cbe2`.

## Cambios comprobables

- Decisión E4-13 aprobada por Christian: Directa por defecto para código y `.py`, con Agente como opción visible. ZIP/GitHub mantienen análisis directo por archivo. Cambiar la opción limpia el resultado y no inicia llamadas.
- P25 documenta el rechazo de cinco pasos; el máximo permitido es cuatro.
- [Matriz pública](matriz-publica-3214960.json): ejecución contra Railway con el ejecutor versionado. Consultar `resultado`, `total` y cada escenario; un checkpoint `en_progreso` no equivale a aprobación final. No utiliza Gemini.
- [Presentación vigente](../../../presentacion/README.md): diez diapositivas, PDF y editable. Los documentos anteriores se conservan en `docs/historico/presentaciones/`.
- [Reparto del ensayo](sustentacion-ensayo.json): Christian 5 minutos, Ronald 3 y Klever 4; son tiempos planificados, no una duración medida.

## Validación y límites

Validación local de frontend: 146 pruebas aprobadas, 24 HTTP omitidas en esa suite, lint y build correctos. Las pruebas de navegador modificadas se someten a CI; no se presentan como ejecutadas localmente. La descarga local de Chromium no estuvo disponible. Backend sin cambios en este bloque.

Se revisaron visualmente las diez diapositivas exportadas. Las capturas históricas mantienen su carácter real o simulado según sus etiquetas. La comparación no demuestra mayor precisión del agente: 17/20 informes completos en Directa y 14/20 en Agente. El F1 de 1,00 corresponde solo a los trece pares completos comunes.

## Evidencia humana pendiente

Christian informó que las actividades se realizaron. No proporcionó todavía la duración medida del ensayo, la fecha/hora exacta ni las observaciones orales concretas del docente. Se conservan como `null`; el reparto acordado no sustituye esos datos. Tampoco se afirma una nueva instalación independiente o una carga al portal.

El ZIP debe generarse desde el SHA final integrado con `scripts/empaquetar_entrega.py`. No reutilizar el ZIP de una versión anterior ni añadir un hash autorreferencial al mismo commit.
