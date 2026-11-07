# Aviso de IA, tratamiento de datos y limitaciones

Descripción técnica actualizada el 7 de noviembre de 2026, base `8e66b2c`.
No constituye una certificación legal ni atribuye al proveedor condiciones de
retención que el equipo no haya verificado.

## Qué procesa CODEGUARD

En modo API, recibe código pegado, archivos `.py`, archivos Python contenidos en
ZIP o recuperados de un repositorio público de GitHub. Valida formato, tamaño y
rutas antes del análisis. El programa recibido se analiza como texto, sin
importarlo ni ejecutarlo. Ruff/Bandit y AST realizan inspecciones; el código,
contexto documental y evidencia pertinente se envían a Gemini para el análisis
generativo. El agente puede realizar más de una llamada al proveedor.

El modo Demo utiliza resultados ilustrativos locales. El endpoint estático y la
previsualización AST no necesitan Gemini; no confundirlos con el análisis real.

## Destinatarios y almacenamiento

| Componente | Datos y propósito | Límite de lo afirmado |
|---|---|---|
| Frontend | Entrada y resultado para mostrar y exportar | No ofrece historial de informes persistente de usuarios |
| Backend | Validación y análisis; memoria y temporales necesarios | No ejecutar el código no significa que nunca se escriba un temporal de análisis |
| Gemini | Código y contexto necesarios para generación/planificación | Aplican las condiciones de la cuenta/servicio; no se declara retención cero |
| GitHub API | Consulta del repositorio público solicitado | Solo repositorios públicos, descarga limitada y sin redirecciones arbitrarias |
| SQLite | Propuestas de corrección y proyectos pendientes vinculados a sesión | Puede guardar temporalmente código/propuesta/instantánea; caducidad y limpieza, no historial permanente de informes |
| ChromaDB | Conocimiento curado e índice de contexto del proyecto | No es una base de informes privados de usuarios |
| Hosting/logs | Operación del servicio y telemetría | Los controles del proyecto no certifican todas las prácticas de terceros |

El aviso visible está implementado en
[PrivacyNotice.tsx](../frontend/src/components/PrivacyNotice.tsx). Explica envío a
Gemini, análisis como texto y exclusión de información sensible.

## Minimización y controles

- Enviar solo el fragmento necesario y usar ejemplos sintéticos en las pruebas.
- No incluir contraseñas, claves API, tokens, datos personales o material privado.
- No exponer secretos del servidor en variables `VITE_*`, capturas o informes.
- Sanitizar errores de validación y del proveedor; no mostrar payloads sensibles.
- Conservar evidencia con entorno, fecha y alcance, evitando respuestas crudas si
  contienen información sensible.
- Revisar los hallazgos antes de cambiar software; abstención, estado parcial o
  ausencia de alertas no garantizan seguridad.

## Limitaciones declaradas

Puede haber falsos positivos y negativos. El corpus contiene seis reglas y no
cubre todas las vulnerabilidades Python. Las citas se verifican estructuralmente;
su pertinencia y las correcciones requieren revisión humana. El proveedor puede
fallar o limitar cuota. Los límites por proceso no equivalen a autenticación ni a
cuotas individuales de tokens.

No existe evidencia de una auditoría legal integral, de backups restaurados ni
de ausencia absoluta de secretos en todo el historial. El hallazgo QA-H02 se
mantiene en el [registro de cierre](19-cierre-documental.md).

## Confirmaciones y conservación temporal

Previsualizar una corrección envía código y objetivo al backend y puede llamar a
Gemini antes de la aprobación de descarga. Aprobar solo permite descargar el
contenido revisado. No afirmar que rechazar esa descarga evita la generación
que ya ocurrió. Las propuestas caducan a los 300 segundos. La limpieza elimina
el contenido vencido y conserva metadatos de decisión temporalmente para
idempotencia/caducidad (retención configurada de 24 horas).

El presupuesto ZIP/GitHub guarda una instantánea temporal del código. Preparar
GitHub consulta su API pública; no llama a Gemini. Aprobar autoriza el análisis
de esa instantánea. Rechazar no añade llamadas generativas y elimina la
instantánea almacenada. Caducidad inicial: 300 segundos; ejecución y retención
operativa se rigen por el servicio de proyectos. Cookies HttpOnly/SameSite y
hashes vinculan las decisiones a la sesión.

Las bases SQLite residen junto al volumen del índice y usan permisos 0600.
La limpieza lógica y secure_delete no certifican eliminación física de backups,
SSD ni copias del proveedor. Dejar de esperar en el navegador no revoca una
operación ya aprobada. Los contadores de tokens recibidos del SDK sirven para
trazabilidad, no son una factura ni justifican inferir valores ausentes.
