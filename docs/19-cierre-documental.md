# 19. Cierre documental — Entrega 4

> Registro histórico del 5 de noviembre. Para el estado vigente del 7 de noviembre
> consultar [37-cierre-verificado.md](37-cierre-verificado.md), con la comparación
> real, herramientas v2, herencia, documentación y pendientes humanos. Las filas
> siguientes conservan el diagnóstico de su fecha; no deben interpretarse como
> comprobaciones repetidas hoy.

Fecha: 5 de noviembre de 2026, America/Bogota. Responsable: Ronald Yépez.
Base revisada: `65675e27fd996a7e71a926336dba6dffb5e539e2`.
Esta edición añade documentación y materia prima; no ejecuta una nueva evaluación
de IA, no despliega y no convierte documentos retrospectivos en evidencia de Fase 1.

Requisitos contrastados con el [portal del seminario](https://fabig76.github.io/entregas-ia-uniandes/)
y la [auditoría precedente](16-auditoria-entrega-integracion.md).

## Semana 1: subsanación documental

| Punto | Estado de esta revisión | Evidencia / acción pendiente |
|---|---|---|
| s1a Propuesta y modelo | Documento actualizado | [01-propuesta.md](01-propuesta.md), alternativas y justificación sin métricas inventadas |
| s1b Historias y RNF | Documento completado | [02-requisitos.md](02-requisitos.md): doce historias y umbrales observables; aceptación con usuarios no acreditada |
| s1c Arquitectura | Documento actualizado | [03-arquitectura.md](03-arquitectura.md): C4, secuencia, herramientas, fuentes y vectorial |
| s1d Inventario | Documento incorporado | [04-fuentes.md](04-fuentes.md): ocho referencias para seis reglas |
| s1e Levantamiento real | **Pendiente de evidencia real** | [Instrumento de 18 preguntas](levantamiento.md) preparado; respuestas y actividad original no aportadas |
| s1f Materia prima | Incorporada ahora | [data/raw](../data/raw/README.md): ocho HTML, origen, fechas y hashes; no acredita entrega histórica |
| s1g Base del repositorio | Presente y README actualizado | README, `.gitignore`, `.env.example`; variables heredadas aclaradas |
| s1h Evidencias originales | **Pendientes** | [Registro](evidencias/semana-1/README.md); no se fabricaron capturas ni actas |
| s1i Salud local, opcional | Implementado y probado posteriormente | `test_health.py`; no acredita fecha de ejecución de Semana 1 |

Los documentos técnicos faltantes se subsanan en la fecha real de esta edición.
La aceptación de una subsanación tardía corresponde al docente.

Validación de esta edición: [reporte y reproducción](evidencias/semana-4/cierre-documental-20261105/README.md).
Los enlaces relativos, hashes de fuentes y conservación de históricos se
comprobaron localmente; no se reejecutó el producto por cambios documentales.

## Responsabilidad de QA, seguridad y documentación

| Tarea del rol | Evidencia disponible | Límite o pendiente |
|---|---|---|
| Más de 15 escenarios públicos | [Matriz propia 26/26](evidencias/semana-4/produccion-integrada-20261105/pruebas-publicas.json) | Corresponde a la revisión desplegada en esa corrida |
| Prompt injection | Regresiones y P26 AST en [pruebas](08-pruebas.md) | No prueba resistencia general del Gemini real ni todos los documentos maliciosos |
| `.py`, ZIP, GitHub inválido y excesos | Matriz pública y regresiones locales | Éxito de GitHub real en la versión final requiere su propia ejecución |
| 429, 503, timeout y errores seguros | [Cierre QA](12-cierre-qa-entrega4.md) y [resiliencia](11-resiliencia-gemini.md) | Mantener origen de simulación versus error real |
| Persistencia de citas | Baseline, comparación y captura del comparador aportados por Christian | Continuidad observada; la imagen no es un log Railway. Falta evidencia independiente del reinicio/volumen |
| Secretos | Auditorías y QA-H02 documentados | **Pendiente** conclusión trazable de credencial histórica y auditoría final correspondiente |
| Documentación base | Propuesta, requisitos, arquitectura, fuentes, ADR, README y datos actualizados | Originales de Fase 1 y aceptación formal no aportados |
| Aportes e IA | [Integrantes confirmados](11-aportes-ia.md) | Apellido de Andy y validación final de aportes/cuentas por el equipo |
| Organización de evidencias | Índices por semana, fuente y revisión | No reemplazar resultados anteriores por resultados de otra corrida |

## Pendientes de cierre del equipo

| ID | Responsable principal | Dato o actividad necesaria | Criterio de cierre |
|---|---|---|---|
| D01 | Ronald y equipo | Recuperar levantamiento y originales de Semana 1 | Respuestas auténticas, fecha, procedencia y notas/capturas; si no existen, aclaración y subsanación acordada |
| D02 | Ronald, Christian y titular de la credencial | Resolver QA-H02 sin divulgar el valor | Conclusión documentada sobre carácter sintético/revocación y alcance de auditoría final |
| D03 | Andy y Christian | Comparación generativa final equivalente | Dataset/configuración congelados y resultados reales según [protocolo](18-comparacion-semanas-3-4.md) |
| D04 | Andy y equipo | Presentación final PDF de 12 minutos | PDF bajo `docs/`, revisión conjunta y cifras compatibles con evidencia; este cierre no sustituye su presentación |
| D05 | Integrante que no preparó el entorno; Ronald registra | Instalación limpia cronometrada | Equipo/cachés, comandos y tiempo real; objetivo de diez minutos |
| D06 | Andy y Christian; Ronald verifica | Revisión final desplegada | Relación Git/despliegue, comprobación visual y escenarios necesarios para PR #31; no reutilizar evidencia de otro SHA |
| D07 | Los tres integrantes | Identidades, aportes y aceptación de riesgos | Apellido de Andy, correspondencia de cuentas y confirmación individual sin reasignar commits |
| D08 | Equipo | Observaciones de sustentación | Registrar lo que ocurra en la fecha real; aún no ocurrido al redactar |
| D09 | Responsable de entrega; Ronald revisa | ZIP final y correspondencia Git | `CODEGUARD_Semana4.zip`, máximo 20 MB, sin secretos/cachés/dependencias; verificar contenido de la revisión acordada |
| D10 | Christian; Ronald revisa | Log real del reinicio y recuperación del volumen | Evidencia fechada del servicio y montaje; la imagen actual solo muestra continuidad HTTP |

Las actividades de Andy y Christian figuran para coordinar el cierre; no se
presentan como aportes ejecutados por Ronald. El guion del rol QA está disponible
en [guion-qa.md](guion-qa.md).

## Dictamen documental

Se completó la estructura técnica que puede sustentarse con código y evidencias
existentes. **No se declara cumplimiento académico total:** faltan respaldos
originales, validaciones y entregables grupales identificados arriba. Esta
distinción permite entregar un informe verificable sin inventar resultados.
