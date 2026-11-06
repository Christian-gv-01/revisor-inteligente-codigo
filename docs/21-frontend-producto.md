# 21. Frontend y documentación del producto — nueva asignación

Fecha: 6 de noviembre de 2026. Responsable: Ronald Yépez, Compañero 2.
Rama: `feature/entrega4-frontend-producto`, derivada del cierre documental
`578adee` y del producto `65675e2`. Preparada para PR en borrador según la autorización
del líder. Ver [entrega para integración](22-entrega-frontend-integracion.md).

## Alcance realizado del lado frontend

- Previsualización completa del original y la propuesta, con casilla inicialmente
  desmarcada y botón separado para confirmar la generación/descarga de una copia.
- Cancelación sin descarga, descarte de respuestas tardías y reinicio del
  consentimiento al cambiar de entrada, archivo o hallazgo.
- Comprobación de ID, hashes, contenido, nombre y caducidad. Si la respuesta de
  aprobación cambia lo previsualizado, no se descarga.
- Demostración explícita con el ejemplo SQL inicial. La propuesta es fija y local;
  no se extrae código de la explicación de una sugerencia ni se atribuye a Gemini.
- Adaptador de API propuesto, deshabilitado por defecto. Christian debe acordar e
  implementar el contrato antes de habilitarlo.
- Prioridad visible y orden de revisión derivado de la severidad actual, sin
  alterar los datos originales/exportados. El estado parcial se muestra incluso
  con hallazgos útiles y sin mensaje del backend.
- Fuentes contextuales, observaciones estáticas y traza del agente conservadas
  por separado.

El campo `requiere_confirmacion_humana` por sí solo no identifica una propuesta
ni autoriza una acción. Tampoco implica que existan endpoints de aprobación.
El [contrato para Christian](20-contrato-confirmacion-humana.md) define lo que falta
acordar sin modificar archivos de Backend.

Para revisar la demo local: desde `frontend/`, ejecutar
`npm run dev -- --host 127.0.0.1`; abrir la URL local que indica Vite, mantener el
ejemplo SQL inicial en modo Demo, pulsar «Probar análisis» y después
«Previsualizar propuesta». El servidor de desarrollo no debe exponerse a la red.

## Ocho historias del producto y criterios de aceptación

Estas historias específicas complementan las historias generales del
[documento de requisitos](02-requisitos.md). Son criterios verificables de esta
asignación, no entrevistas retrospectivas.

| ID / historia | Dado | Cuando | Entonces | Verificación / estado |
|---|---|---|---|---|
| FP-01. Como revisor quiero previsualizar una corrección | Un archivo disponible y una propuesta válida vinculada a su contenido | Solicito previsualizar | Veo original y propuesta completos, sin descarga ni ejecución | Flujo local y pruebas de contrato; Backend real pendiente |
| FP-02. Como usuario quiero aprobar exactamente lo revisado | Una propuesta vigente y la casilla sin marcar | Reviso, marco autorización y pulso confirmar | Solo entonces se solicita aprobación; se descarga una copia con nombre diferente y contenido idéntico al previsualizado | Pruebas de integridad y navegador local |
| FP-03. Como usuario quiero cancelar | Hay una preparación o confirmación pendiente | Pulso cancelar | No se descarga ni se sobrescribe el original; se descartan respuestas tardías y se comunica si el rechazo remoto no pudo registrarse | Cancelación local, incluso durante aprobación |
| FP-04. Como usuario quiero que mi aprobación no se reutilice | Existe consentimiento para una propuesta | Cambio de archivo/entrada, cancelo o la propuesta caduca | El consentimiento queda invalidado; se exige nueva previsualización y aprobación | Pruebas de caducidad, nueva entrada y casilla reiniciada |
| FP-05. Como revisor quiero atender primero los riesgos prioritarios | Hay hallazgos de severidades diferentes | Consulto el informe | Veo prioridad y severidad, ordenadas de crítica a baja, sin sumar capas ni modificar el informe exportable | Regresión frontend; alinear con priorización de la rama nueva de Backend antes de integrar |
| FP-06. Como usuario quiero reconocer una revisión incompleta | El resultado tiene estado parcial, con o sin hallazgos/mensaje | Se presenta el informe | Veo advertencia explícita y resultados conservados; no se declara código seguro | Regresión de estado parcial y carga nueva |
| FP-07. Como evaluador quiero comprobar las fuentes | Un hallazgo contiene referencias | Consulto su respaldo | Las citas corresponden al informe del archivo; reglas estáticas siguen separadas y sin fuentes inventadas | Suites de trazabilidad y estático existentes |
| FP-08. Como evaluador quiero entender el proceso del agente | El backend devuelve una traza validada | Abro el proceso de revisión | Veo herramientas, decisiones, origen y fase incompleta; la exportación conserva la traza | Suite del agente existente; no se inventan pasos ausentes |

## Validación local

- 91 pruebas frontend aprobadas. 17 pruebas HTTP omitidas por no iniciar su backend
  de integración; no se presentan como aprobadas en esta rama.
- ESLint sin errores y build correcto; persiste la advertencia conocida de paquete
  superior a 500 kB.
- Ocho escenarios de interacción en Edge headless local, incluidos cancelación
  durante aprobación, respuesta alterada, nueva entrada y pantalla de 390 px.
  El último verifica el flujo desde la página principal real en modo Demo.
- [Evidencias locales](evidencias/semana-4/frontend-producto-20261106/README.md).

No se ejecutaron Gemini, código Python de entrada ni llamadas a la URL pública.
No se realizó una nueva evaluación del backend de Christian; sus 199 pruebas
comunicadas corresponden a su trabajo, no a esta validación frontend.

## Documentación y presentación

Se mantiene el [inventario de ocho fuentes](04-fuentes.md), con originales y hashes,
y se actualizan [propuesta](01-propuesta.md), [arquitectura](03-arquitectura.md) y
[aportes](11-aportes-ia.md) para distinguir esta asignación del rol anterior de QA.

El [borrador de presentación](presentacion/README.md) tiene doce diapositivas y un
reparto de 720 segundos, con notas y fuentes. La corrección real figura como
pendiente de acuerdo e integración, no como funcionalidad desplegada.

## Protección del servicio publicado

Se revisaron los workflows de GitHub disponibles: contienen pruebas, no pasos
de despliegue. Esto no verifica las conexiones automáticas configuradas en Railway.
El líder informó que verificó pipeline y despliegue y autorizó subir ramas separadas
y abrir PR en borrador hacia `main`. Se conserva esta rama propia, opción permitida
en su mensaje. No se autoriza fusionar, hacer push a `main` ni desplegar manualmente.
No se cambian Docker, Backend ni variables del hosting. La prueba conjunta se hará
en una rama de integración separada con el backend candidato.

## Integración pendiente, por responsable

| Responsable | Acción |
|---|---|
| Christian y Ronald | Acordar nombres, límites, estados y semántica del [contrato v1](20-contrato-confirmacion-humana.md) |
| Christian | Implementar propuestas, aprobación/rechazo, TTL y protección de acceso; entregar su contrato real |
| Ronald | Adaptar los campos si cambian y ejecutar integración HTTP real local, incluidos 409/410 y rechazo |
| Christian y Ronald | Alinear la prioridad visible con la priorización determinista que Christian informó en su rama |
| Equipo | Revisar el borrador de sustentación y autorizar por separado la integración/publicación de una revisión concreta |
