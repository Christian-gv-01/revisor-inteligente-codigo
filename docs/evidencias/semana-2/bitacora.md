
# Bitácora de QA, Seguridad y Documentación

**Proyecto:** Revisor Inteligente de Código Seguro
**Rama:** feature/qa-seguridad
**Fecha de inicio:** 20 de octubre de 2026
**Estado:** En progreso

## 1. Pruebas automatizadas

- Se creó `backend/tests/test_health.py`.
- Se comprobó el endpoint GET `/health`.
- Se utilizó `TestClient` para probar la API sin iniciar un servidor independiente.
- Resultado observado: 1 prueba aprobada.
- Se detectó una advertencia relacionada con `TestClient`, pendiente de revisión.

## 2. Documentación técnica

- Se creó `docs/03-arquitectura.md`.
- Se creó `docs/09-decisiones.md`.
- Queda pendiente revisar la documentación con el equipo y confirmar las decisiones definitivas.

## 3. Revisión de seguridad

Pendiente de verificar:

- [ ] Protección de claves y variables de entorno.
- [ ] Validación del tipo y tamaño de archivos.
- [ ] Protección frente a ZIP maliciosos y rutas inseguras.
- [ ] Restricción de repositorios autorizados.
- [ ] Prohibición de ejecutar código recibido.
- [ ] Límites de tiempo y recursos.
- [ ] Protección de logs y datos sensibles.
- [ ] Tratamiento de instrucciones maliciosas dirigidas a la IA.

## 4. Evidencias pendientes

- [ ] Captura de la prueba de salud aprobada.
- [ ] Resultados de las pruebas automatizadas adicionales.
- [ ] Evidencias de manejo de errores.
- [ ] Historial de commits.
- [ ] Pruebas de las tres versiones de prompts.
- [ ] Registro de problemas y soluciones.

## 5. Observaciones

Las pruebas y los controles de seguridad se marcarán como completados
únicamente después de verificarlos. Los resultados documentados deben
corresponder a ejecuciones reales.
