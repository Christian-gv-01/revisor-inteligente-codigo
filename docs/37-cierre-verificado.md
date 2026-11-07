# 37. Cierre verificado frente a la ficha docente

Fecha: 7 de noviembre de 2026. La ficha del portal revisó `605d142`, 6 de noviembre
18:00, mediante lectura estática. No describe automáticamente el main actual.
Base activa comprobada: `8e66b2cc3f10b67589edd3714de17dcc8246d729`, PR #55.
Este documento distingue lo integrado, el candidato posterior y lo que requiere
actividad o aceptación humana. No acredita por sí solo entrega al portal.

## Trazabilidad del producto

| Observación docente | Estado verificable | Evidencia |
|---|---|---|
| buscar_referencia no elegible | Resuelto en v2: categoría tipada, fragmentos y trazabilidad, junto a ampliar_contexto ±6 y finalizar | PR #43/#45/#52; docs/08; pruebas v2 y JSON |
| Decisiones sin consecuencias | Resultados participan en planificación y síntesis; 10/20 finalizaciones tempranas en la corrida real de 8e66b2c | resultados.json y trazas de la comparación |
| Severidad solo ordenada | YAML y derivación; Bandit alta+alta permite crítica. Herencia ID ofrecido/no ambiguo/misma línea; auditoría reconstruida | PR #55, docs/35, regresiones de herencia |
| Comparación real solo directa | Corrida nueva de 40 análisis: 20 por ruta, 20 pares completos; cifras desfavorables conservadas | docs/18 y comparación real de 8e66b2c |
| Documentación desfasada | README, decisiones, arquitectura, privacidad, agente y contratos actualizados en candidato | Documentos correspondientes; históricos conservados |
| PDF ausente | PDF y editable existen desde PR #53; actualización con comparación y límites en este cierre | docs/presentacion/ |
| Confirmación pública apagada | En 8e66b2c seguía apagada; candidato Docker compila ambas interfaces y exige presupuesto backend | Dockerfile, compose, smoke del contenedor |
| Despliegue no demostrado | UI Railway mostró PR #55 Active/Deployment successful y enlace exacto al SHA; salud/OpenAPI 200 | procedencia-despliegue.json |
| Persistencia sin logs | En ese arranque se observó volumen, UID 10001 e índice recuperado | Registro de procedencia; no demuestra backup restaurado ni hash del corpus |
| Matriz pública envejecida | P25 actualizado para rechazar cinco pasos; cuatro ya es un máximo válido | Script público y regresión QA |

## Resultados reales anteriores a la corrección de cobertura

Mismos veinte casos, orden alternado, revisión 8e66b2c, sin reintentos del
cliente evaluador. Modelo gemini-3.5-flash-lite. No se ejecutó el código recibido.

| Medida | Directa | Agente v2, máximo cuatro pasos |
|---|---:|---:|
| Informes completos | 20/20 | 20/20 |
| TP / FP / FN | 11 / 0 / 1 | 8 / 1 / 4 |
| Precisión | 1,000 | 0,889 |
| Recall | 0,917 | 0,667 |
| F1 | 0,957 | 0,762 |
| Latencia media / p95 | 4,85 / 6,15 s | 9,27 / 12,76 s |
| Tokens totales reportados | 31.116 | 100.573 |
| Intentos reportados | 18 | 70 |
| Abstenciones | 3 | 2 |
| Finalización anticipada | No aplica | 10/20 |

El agente no mejoró calidad, tiempo ni consumo en esta muestra. Resolver IDs de
citas no basta: P06 es un falso positivo pese a citar la regla correcta. El A/B
histórico de una decisión usa otro protocolo; no se sustituye por estos informes.
La huella del índice activo no pudo verificarse: corrida exploratoria respecto
a ese control. Las correcciones sugeridas no fueron ejecutadas.

## Corrección de cobertura del candidato

Se reprodujo que `buscar_referencia` sustituía toda la recuperación base aunque
sus resultados fueran impertinentes. En los casos eval, devolvió 005/003 y omitió
001. El candidato reserva hasta tres fuentes del código y añade las elegidas,
deduplicadas, máximo seis. No añade llamadas generativas ni altera etiquetas.
Tres regresiones fallaron antes del cambio; las cuatro pasan con el ajuste.
La corrida 8e66b2c se conserva completa; no se le atribuye la corrección posterior.

## Validación del candidato

- Python: 663 pruebas aprobadas, 583 backend y 80 QA/evaluadores. Las específicas
  están incluidas en esos totales, no se suman otra vez.
- Frontend: 146 aprobadas, 24 HTTP omitidas en la suite unitaria; lint y build correctos.
- HTTP local: 24/24 con estático y 19/19 aplicables sin él, cinco omitidas.
  FastAPI, Chroma y Ruff/Bandit reales; Gemini/GitHub simulados.
- Smoke de imagen preparado: presupuesto visible, rechazo con sesión y cero
  intentos al proveedor. Smoke local aprobado; Docker y navegador se verifican en CI.
- Cobertura de doce combinaciones y UTF-8 incorpora el aporte de cf82e84, sin
  cambiar la política. No se fusiona por segunda vez el PR #54.

## Límites que requieren personas o acceso operativo

1. Repetir la comparación sobre el candidato desplegado si se incorpora la
   corrección funcional de cobertura. No elegir la mejor corrida ni descartar la anterior.
2. A/B v2 de seis pares sin/con contexto estático: ejecutor preparado, pero la
   consola web de Railway mostró Disconnected. No se extrajo ni publicó la clave.
   Debe ejecutarse en un entorno autorizado con GEMINI_API_KEY ya configurada.
3. Instalación por otro integrante: la automatizada de 5 min 45 s usó herramientas
   y cachés existentes. No certifica el objetivo humano de diez minutos.
4. Ensayo oral y reparto: los doce minutos son planificados, no cronometrados.
5. Levantamiento y originales de Semana 1, nombres/cuentas/aportes y aceptación
   de riesgos: conservar faltantes reales; no inventar entrevistas ni firmas.
6. La clasificación técnica del JWT histórico como fixture está en docs/18-ci-main-docker.
   No se probó como credencial ni se acredita revocación. Confirmación del titular,
   si la exige el docente, sigue siendo una declaración humana.
7. La entrega del ZIP y el registro de correcciones en el portal requieren revisión
   del paquete exacto y envío del responsable. Un ZIP generado no acredita envío.

## Criterio de entrega

Congelar el candidato técnico, verificar CI y SHA activo, conservar resultados y
limitaciones, exportar presentación y empaquetar desde Git. La aprobación académica
corresponde al docente; no se declara 100% por aumentar el número de pruebas.
