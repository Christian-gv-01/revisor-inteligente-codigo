# Bitácora de QA, Seguridad y Documentación

**Proyecto:** Revisor Inteligente de Código Seguro
**Rama:** `feature/qa-seguridad`
**Fecha de inicio:** 20 de octubre de 2026
**Estado:** En progreso

## 1. Pruebas automatizadas

- Se creó `backend/tests/test_health.py`.
- Se verificó el endpoint `GET /health` mediante `TestClient`.
- Se ejecutó `python -m pytest tests -v` desde la carpeta `backend`.
- Resultado observado: **1 prueba aprobada**.
- La ejecución inicial desde la raíz del proyecto produjo `ModuleNotFoundError: No module named 'app'`. El problema se resolvió ejecutando las pruebas desde la carpeta `backend`, sin modificar el código de la aplicación.
- Se observó una advertencia de compatibilidad relacionada con `TestClient` y HTTPX. Queda pendiente revisarla.
- Las pruebas de análisis, validación de entradas y manejo de errores del proveedor de IA están pendientes.

## 2. Documentación técnica

- Se creó `docs/03-arquitectura.md`.
- Se creó `docs/09-decisiones.md`.
- Se creó y publicó el archivo principal `README.md`.
- El README se publicó mediante el commit `04bab7c`, con el mensaje `docs: completar README inicial`.
- Queda pendiente revisar la exactitud y completitud de la documentación con el equipo.
- Las decisiones arquitectónicas definitivas deben confirmarse con los responsables correspondientes.

## 3. Revisión de seguridad

### 3.1. Credenciales y variables de entorno

- Se revisó `.gitignore`.
- Se comprobó que las reglas ignoran `.env` y `.env.local`.
- Se revisó la plantilla `.env.example` de la rama remota del backend.
- Se comprobó que `GEMINI_API_KEY` y `GEMINI_MODEL` aparecen sin valor en la plantilla consultada.
- Se inspeccionó el árbol de archivos de `origin/feature/backend-ia` y no se encontraron archivos `.env` ni variantes distintas de `.env.example` que coincidieran con el filtro utilizado.
- Estos resultados no constituyen una auditoría completa del historial de Git ni una búsqueda exhaustiva de secretos en todos los archivos.

### 3.2. Controles pendientes

- [ ] Verificar la carga y protección de las credenciales en el backend.
- [ ] Revisar el historial de Git en busca de posibles secretos expuestos.
- [ ] Verificar los tipos y tamaños de archivos permitidos.
- [ ] Comprobar la protección frente a archivos ZIP maliciosos y rutas inseguras.
- [ ] Verificar las restricciones de repositorios autorizados y la prevención de solicitudes a direcciones internas.
- [ ] Comprobar que el código recibido no se ejecute ni se importe.
- [ ] Verificar los límites de tiempo y recursos.
- [ ] Comprobar que los logs y mensajes de error no expongan información sensible.
- [ ] Verificar el tratamiento de instrucciones maliciosas dirigidas a la IA.
- [ ] Registrar pruebas y evidencias de cada control.

## 4. Evidencias pendientes

- [ ] Guardar una captura de la ejecución de pytest con la prueba de salud aprobada.
- [ ] Registrar los resultados de las pruebas adicionales.
- [ ] Recopilar evidencias reales del manejo de errores.
- [ ] Registrar el historial de commits relevantes.
- [ ] Documentar las pruebas de las tres versiones de prompts.
- [ ] Registrar los problemas encontrados y las soluciones aplicadas.
- [ ] Revisar y completar esta bitácora durante el desarrollo.

## 5. Estado del README

El README principal se creó en la raíz del repositorio y se publicó en `feature/qa-seguridad`.

Incluye descripción del proyecto, objetivos, tecnologías, estructura inicial, instrucciones de instalación, ejecución del backend, pruebas, variables de entorno, seguridad, limitaciones y organización del equipo.

Su contenido debe mantenerse alineado con las funcionalidades reales del sistema a medida que se integren los cambios.

## 6. Próximos pasos

1. Coordinar el contrato del endpoint de análisis con el responsable del backend.
2. Preparar pruebas automatizadas con mocks para las entradas inválidas y los errores del proveedor de IA.
3. Completar la revisión de seguridad.
4. Verificar la arquitectura y los ADR con el equipo.
5. Organizar las evidencias y ejecutar las pruebas finales.
6. Revisar los cambios y preparar el Pull Request.

## 7. Observaciones

Los resultados registrados corresponden a las ejecuciones y comprobaciones realizadas hasta la fecha.

Ningún control de seguridad ni prueba pendiente se considerará aprobado hasta que exista evidencia suficiente de su implementación y funcionamiento.
