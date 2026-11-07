# 37. Cierre verificado frente a la ficha docente

Fecha: 7 de noviembre de 2026. La ficha del portal revisó `605d142`, 6 de noviembre
18:00, mediante lectura estática. No describe automáticamente el main actual.
Validación pública de análisis: `c522c24f0efcfa7ee4e7411a66fcaa1a612dd740`, PR #56.
Corrección posterior de presupuestos anidados: `0a6707ba294829b9bb4a8e5c30db0b4403faa7bd`, PR #57.
Este documento distingue las versiones probadas y lo que requiere
actividad o aceptación humana. No acredita por sí solo entrega al portal.

## Trazabilidad del producto

| Observación docente | Estado verificable | Evidencia |
|---|---|---|
| buscar_referencia no elegible | Resuelto en v2: categoría tipada, fragmentos y trazabilidad, junto a ampliar_contexto ±6 y finalizar | PR #43/#45/#52; docs/08; pruebas v2 y JSON |
| Decisiones sin consecuencias | Resultados participan en planificación y síntesis; 8/20 finalizaciones tempranas en c522c24; A/B v2: 2 cambios en 5 pares comparables | resultados.json y trazas de la comparación |
| Severidad solo ordenada | YAML y derivación; Bandit alta+alta permite crítica. Herencia ID ofrecido/no ambiguo/misma línea; auditoría reconstruida | PR #55, docs/35, regresiones de herencia |
| Comparación real solo directa | Dos corridas de 40 análisis. La última conserva 17/20 y 14/20 completos, 13 pares comunes | docs/18 y comparación real de 8e66b2c |
| Documentación desfasada | README, decisiones, arquitectura, privacidad, agente, contratos y resultados actualizados | Documentos correspondientes; históricos conservados |
| PDF ausente | PDF y editable existen desde PR #53; actualización con comparación y límites en este cierre | docs/presentacion/ |
| Confirmación pública apagada | Activa en c522c24: presupuesto visible, rutas antiguas devuelven 428, aprobación y copia comprobadas | Dockerfile, compose, smoke del contenedor |
| Despliegue no demostrado | UI Railway mostró c522c24 activo y successful; ocho checks aprobaron; salud/OpenAPI 200 | procedencia-despliegue.json |
| Persistencia sin logs | En ese arranque se observó volumen, UID 10001 e índice recuperado | Registro de procedencia; huella del índice verificada durante y al final sobre c522c24; no demuestra backup restaurado |
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

## Corrección de cobertura integrada en PR #56

Se reprodujo que `buscar_referencia` sustituía toda la recuperación base aunque
sus resultados fueran impertinentes. En los casos eval, devolvió 005/003 y omitió
001. El ajuste reserva hasta tres fuentes del código y añade las elegidas,
deduplicadas, máximo seis. No añade llamadas generativas ni altera etiquetas.
Tres regresiones fallaron antes del cambio; las cuatro pasan con el ajuste.
La corrida 8e66b2c se conserva completa; la posterior c522c24 se registra separadamente.

## Validación del software y de producción

- Python: 669 pruebas aprobadas en PR #57, 589 backend y 80 QA/evaluadores. Las específicas
  están incluidas en esos totales, no se suman otra vez.
- Frontend: 146 aprobadas, 24 HTTP omitidas en la suite unitaria; lint y build correctos.
- HTTP local: 24/24 con estático y 19/19 aplicables sin él, cinco omitidas.
  FastAPI, Chroma y Ruff/Bandit reales; Gemini/GitHub simulados.
- Docker e integración HTTP aprobaron en CI de c522c24 y del PR #57.
- Nueve controles HTTP reales públicos aprobaron en c522c24. Se detectó consumo
  oculto en la aprobación de proyectos y se corrigió en PR #57 con seis regresiones.
  La evidencia original de ese cero erróneo se conserva.
- Railway activó 0a6707b (deployment 46dd6252). La aprobación pública posterior
  registró dos intentos y cero respuestas, con resultado parcial. La repetición
  devolvió el mismo cuerpo y cero intentos nuevos. No se inventan tokens.
- Cobertura de doce combinaciones y UTF-8 incorpora el aporte de cf82e84, sin
  cambiar la política. No se fusiona por segunda vez el PR #54.

## Límites que requieren personas o acceso operativo

La repetición de cuarenta análisis y el A/B v2 ya se ejecutaron sobre c522c24.
Los JSON, CSV, configuración, huella y revisión de citas están en
[evidencia pública final](evidencias/semana-4/postmerge-c522c24-20261107/README.md).
La directa obtuvo 17/20 informes completos y el agente 14/20. Trece pares comunes
tienen F1 1,0 en ambas rutas, con 3/6 parciales conservados. La media global fue
10,34/22,62 s y los intentos 21/71. Los tokens totales permanecen desconocidos.
El A/B obtuvo cinco pares válidos, uno incompleto y dos cambios de decisión.
La huella se observó durante y al final, no al inicio. No afirmar superioridad.

1. Instalación por otro integrante: la automatizada de 5 min 45 s usó herramientas
   y cachés existentes. No certifica el objetivo humano de diez minutos.
2. Ensayo oral y reparto: los doce minutos son planificados, no cronometrados.
3. Levantamiento y originales de Semana 1, nombres/cuentas/aportes y aceptación
   de riesgos: conservar faltantes reales; no inventar entrevistas ni firmas.
4. La clasificación técnica del JWT histórico como fixture está en docs/18-ci-main-docker.
   No se probó como credencial ni se acredita revocación. Confirmación del titular,
   si la exige el docente, sigue siendo una declaración humana.
5. La entrega del ZIP y el registro de correcciones en el portal requieren revisión
   del paquete exacto y envío del responsable. Un ZIP generado no acredita envío.

## Criterio de entrega

Congelar el candidato técnico, verificar CI y SHA activo, conservar resultados y
limitaciones, exportar presentación y empaquetar desde Git. La aprobación académica
corresponde al docente; no se declara 100% por aumentar el número de pruebas.
