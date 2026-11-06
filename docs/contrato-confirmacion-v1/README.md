# Entrega a Christian — confirmación humana v1

Fecha: 6 de noviembre de 2026. Frontend: Ronald Yépez. Backend: Christian Gamboa.
Condiciones funcionales aceptadas; campos y rutas propuestos para implementar.
Referencia frontend: commit `4c483dd`. No se modificó ni desplegó Backend.

## Archivos para implementar

- Contrato completo: [20-contrato-confirmacion-humana.md](../20-contrato-confirmacion-humana.md).
- [Previsualización: solicitud](01-previsualizar-solicitud.json).
- [Previsualización: respuesta de la demo](02-previsualizar-respuesta.json).
- [Aprobación: solicitud](03-aprobar-solicitud.json) y
  [respuesta](04-aprobar-respuesta.json).
- [Rechazo: solicitud](05-rechazar-solicitud.json) y
  [respuesta](06-rechazar-respuesta.json).
- [Procedencia y verificación](verificacion.json).

Los JSON son cuerpos HTTP completos. Las respuestas se obtuvieron del cliente
simulado `correctionDemo.ts`; se validaron con las mismas funciones que consume
la interfaz. No son respuestas de un endpoint real ni propuestas persistidas.

La aprobación y el rechazo son **alternativas para una propuesta inicialmente
pendiente**, no una secuencia para aprobar y luego rechazar el mismo contenido.
Para probar ambos recorridos con Backend, crear dos propuestas independientes.
El identificador `demo-...` no existe en el servidor. `caduca_en` pertenece a la
instantánea de ejemplo (cinco minutos); no reutilizarla como una propuesta vigente.

## Rutas y formato

| Operación | Solicitud | Respuesta exitosa propuesta |
|---|---|---|
| Preparar propuesta | `POST /api/v1/correcciones/previsualizar`, JSON 01 | HTTP 200, JSON 02, `pendiente_confirmacion` |
| Aprobar copia | `POST /api/v1/correcciones/{propuesta_id}/decision`, JSON 03 | HTTP 200, JSON 04, `aprobada` |
| Rechazar propuesta | Misma ruta de decisión, JSON 05 | HTTP 200, JSON 06, `rechazada`, sin contenido |

Usar `Content-Type: application/json`. `propuesta_id` se toma de la respuesta 02
y se incluye en la URL de decisión, no en el cuerpo de solicitud. La respuesta
de aprobación es JSON con el texto completo; **no un binario ni una URL de descarga**.
Frontend comprueba el contenido y crea la descarga local después de confirmar.

Los campos `version`, `estado`, `accion` y `tipo_contenido` requieren los literales
documentados. Los hashes son SHA-256 hexadecimal minúsculo del texto UTF-8 exacto,
no de la representación JSON. No recortar, añadir una línea final ni cambiar
CRLF/LF después de calcularlos. La demo no tiene salto de línea final.

El límite del validador frontend es `string.length <= 12000` (unidades UTF-16 de
JavaScript). En Python, `len(texto)` difiere para algunos caracteres Unicode;
acordar y comprobar el mismo límite al implementar. Las advertencias tienen
longitud máxima 500 unidades, hasta diez elementos.

Nombre de salida compatible: expresión
`^[a-zA-Z0-9_-][a-zA-Z0-9_.-]{0,115}\.py$`, sin `..` y distinto del nombre base
original. ID: `[a-zA-Z0-9_-]`, longitud 6–128. Estas reglas reflejan el frontend
actual; si se cambian, coordinar ambos validadores antes de habilitar.

## Comportamiento esperado del servicio

- Preparar la propuesta como datos; no crear un archivo final, ejecutar el código
  o sobrescribir originales. `objetivo.descripcion` también es dato no confiable.
- Vincular ID, solicitante, original, propuesta, nombre de salida y caducidad.
  Un hash no autentica al usuario; Christian define la protección de acceso.
- Al aprobar, verificar identidad, vigencia y ambos hashes. Devolver exactamente
  la propuesta guardada; no regenerar con Gemini después de la confirmación.
- Al rechazar, cancelar la propuesta y no devolver contenido descargable.
- Resolver decisiones concurrentes y repeticiones de forma consistente. Propuesta
  para discutir: repetir la misma decisión devuelve el mismo resultado; una decisión
  contraria a un estado terminal devuelve 409.
- HTTP 409 para conflicto de contenido/estado; 410 para caducidad. Los demás
  errores se muestran genéricamente en la interfaz. No incluir código ni secretos
  en el mensaje de error. El adaptador no depende del cuerpo de esos errores.
- Abortar una petición del navegador no garantiza que el servidor deje de trabajar.
  La previsualización no debe producir acciones externas irreversibles.

## Qué necesita Ronald para conectar

Confirmar estas rutas/campos, compartir la rama del backend y los comandos para
iniciarlo localmente. Probar aprobar, rechazar, caducidad, conflicto, doble decisión
y respuesta tardía. La prioridad determinista del nuevo backend se alinea también
en esa integración; no se sustituye por una regla de negocio inventada en frontend.

`VITE_CORRECTIONS_API_ENABLED=1` solo se usaría en una compilación local de prueba
después del acuerdo técnico. Mantener la versión publicada sin cambios. No subir,
fusionar ni desplegar ramas hasta revisar con Christian los disparadores de Railway.
