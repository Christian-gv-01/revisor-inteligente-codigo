# Registro de sustentación y ensayo cronometrado — 7 de noviembre de 2026

**Actualización:** 7 de noviembre de 2026, a partir de la medición comunicada por el integrante responsable del proyecto.

## Resultado real del cronómetro

| Concepto | Registro |
|---|---|
| Proyecto | CODEGUARD — revisor asistido de código Python |
| Fecha reportada de exposición/ensayo | 7 de noviembre de 2026 |
| Duración prevista en el guion | 12 minutos (720 segundos) |
| **Duración real total cronometrada** | **10 minutos (600 segundos)** |
| Diferencia frente a lo previsto | 2 minutos menos (120 segundos) |
| Procedencia del dato | Medición comunicada por Christian en el chat; no se adjuntó archivo de cronómetro |
| Duración por participante | No informada; no se infiere desde el reparto planificado |
| Observaciones o correcciones del ingeniero | Se recibió una nota escrita el 8 de noviembre; observaciones orales adicionales no documentadas |

**Estatus de evidencia:** la duración total fue reportada como cronometrada y existe una nota escrita del docente que se transcribe al final. La distribución individual y posibles observaciones del tribunal realizadas verbalmente siguen sin aportarse.

## Presentación aportada para el cierre

El equipo aportó el archivo `CODEGUARD-SEMINARIO-12 diapos.pdf`, comprobado con **12 páginas**, resolución de página 960 × 540 pt, tamaño **476.707 bytes** y SHA-256:

`bb52e1a8f57f4b29a2aa0f66855a097d6a9f487a391fb45189bb202a737aa8a8`

**Actualización de repositorio (8 de noviembre):** este PDF ya figura como [único vigente](../../presentacion/README.md) en `docs/presentacion/` y su hash se valida al empaquetar. No se ha acreditado cuál archivo específico se proyectó durante el cronometraje de diez minutos.

## Plan previo de intervención, solo como referencia

Existió una planificación **de 10 diapositivas**, total 12 minutos: Christian 5 minutos; Ronald 3; Klever/Andy 4. Ese plan **no coincide** con el PDF de 12 diapositivas aportado después y no representa el tiempo real de cada expositor. El único valor total medido comunicado es **10:00**.

| Expositor | Plan anterior | Tiempo real |
|---|---:|---|
| Christian | 5:00 | No informado |
| Ronald | 3:00 | No informado |
| Klever/Andy | 4:00 | No informado |
| **Total** | **12:00** | **10:00 cronometrados** |

## Pendientes concretos antes del envío al portal — lunes 9 de noviembre

- [x] Registrar la **duración real total: 10 minutos**.
- [x] Distinguir de la planificación histórica de 12 minutos.
- [x] Identificar el archivo PDF de 12 diapositivas aportado para el cierre y verificar número de páginas y hash.
- [x] Incorporar el PDF definitivo a `docs/presentacion/` y dejar allí una única versión vigente. Las anteriores se preservan en `docs/historico/presentacion/`.
- [ ] Completar observaciones docentes **solo si efectivamente hubo y se pueden describir**.
- [ ] Confirmar si los 10 minutos corresponden al ensayo o a la sustentación realizada; el dato recibido dice 'tardamos 10 minutos cronometrados' y no distingue ambos eventos.
- [ ] Revisar y aceptar la decisión E4-13 del agente (17/20 frente a 14/20).
- [x] Generar un ZIP candidato verificado en GitHub Actions para `75644cf` (workflow `42521350730`, 11.425.834 bytes de artefacto y estado aprobado). **Repetir para el SHA de `main` que resulte de cualquier limpieza posterior; no entregar el candidato antiguo como versión final**.
- [ ] Subir el paquete y conservar comprobante del envío. El registro por sí solo no acredita ese envío.

## Fuentes técnicas

- [Matriz pública aprobada](pruebas-publicas-post-merge-20261105.json): 26/26, ejecutada el 5 de noviembre.
- [Validación real posterior y A/B](postmerge-c522c24-20261107/README.md): 17/20 informes completos directos y 14/20 agente.
- [Decisiones técnicas](../../09-decisiones.md) y [pruebas](../../08-pruebas.md).

## Retroalimentación escrita del docente recibida el 8 de noviembre de 2026

**Procedencia:** captura proporcionada por Christian con una nota titulada «Lo que les falta para la entrega final», atribuida al docente tras la sustentación del sábado 7. Esta es **retroalimentación escrita recibida por el equipo**; no confirma que los siete puntos se enunciaran verbalmente durante la intervención del tribunal. Plazo indicado: **lunes 9 de noviembre, 23:59**; prórroga máxima **miércoles 11 de noviembre, 23:59** (hora local).

| N.º | Observación resumida | Acción documentada | Estado |
|---:|---|---|---|
| 1 | Encuestar al menos a cinco revisores Python y registrar respuestas, fecha real, 3–4 conclusiones | [Levantamiento complementario](../../levantamiento.md), fuente Word de cinco cuestionarios del 7 de noviembre; commits `f0006723` y `5fce8ec2` | **Corregida documentalmente**, pendiente de aceptación docente |
| 2 | Incorporar evidencias auténticas de Semana 1 o declarar ausencias | [Inventario Semana 1](../semana-1/README.md), cuatro capturas y faltantes; commits `db10d7d6` y `5fce8ec2` | **Corregida documentalmente**, pendiente de aceptación docente |
| 3 | Justificar el agente predeterminado con 14/20 vs 17/20, o cambiarlo | [Decisión E4-13](../../09-decisiones.md), justificación sin afirmar superioridad; commit `177a0ac8` | **Justificada**, aceptación del equipo pendiente |
| 4 | Corregir P25 y enlazar matriz pública | [Pruebas](../../08-pruebas.md): cinco pasos inválidos y [matriz 26/26 del 5 nov](pruebas-publicas-post-merge-20261105.json); commit `1bf55b74` | **Corregida documentalmente** |
| 5 | Regenerar ZIP del commit final y dejar solo un PDF vigente | PDF definitivo [versionado](../../presentacion/README.md), versiones anteriores archivadas; candidato CI generado sobre `75644cf` | **PDF corregido; regenerar ZIP tras última integración** |
| 6 | Registrar observaciones del tribunal y respuesta por commit | Esta tabla registra la nota escrita; falta confirmar cuáles observaciones provinieron del tribunal oral, si fueron distintas | **En curso** |
| 7 | Subir un ZIP único ≤20 MB sin secretos ni dependencias mediante el portal | CI en `75644cf`: paquete candidato 11.425.834 bytes; `gitleaks` aprobado. Hace falta el ZIP del **SHA final** y comprobante de carga en el portal | **Pendiente del envío** |

**Control de cambios:** se indican los commits de preparación de cada corrección; al fusionar el PR, el commit de integración aporta la revisión de `main`. No afirmar enviado al portal hasta disponer del comprobante. Los diez minutos cronometrados ya están registrados arriba; no deben confundirse con el requisito independiente de instalación limpia.
