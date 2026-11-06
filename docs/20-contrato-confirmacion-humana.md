# 20. Contrato propuesto de corrección con confirmación humana

Fecha: 6 de noviembre de 2026. Autor del lado frontend: Ronald Yépez.
Contraparte Backend: Christian Gamboa. **Estado: condiciones funcionales aceptadas
por Christian en el mensaje compartido el 6 de noviembre; campos y endpoints v1
entregados para su revisión e implementación.** Todavía no se acredita un backend
de correcciones implementado. El frontend tiene un adaptador y una demostración
local; la conexión real está deshabilitada por defecto.

Ejemplos completos, con hashes calculados y respuestas verificadas contra los
validadores del frontend: [paquete de integración v1](contrato-confirmacion-v1/README.md).

## Respuesta para coordinar con Christian

«La confirmación aparecerá después de ver el archivo original y la propuesta
completa, antes de generar/descargar el archivo corregido. La única acción que
aprobará el usuario será descargar una copia nueva. No aprobaremos ejecución de
código, sobrescritura del original, commits ni cambios del servidor.

Necesito que la previsualización devuelva un ID de propuesta, nombre original y
de salida, contenido propuesto, hashes SHA-256 del original y de la propuesta,
caducidad y advertencias. Al confirmar o cancelar enviaré una decisión vinculada
a ese ID y a los dos hashes. Al aprobar, la respuesta debe contener exactamente
el contenido previsualizado; si cambió, el frontend impedirá la descarga.

Propongo dos endpoints: POST /api/v1/correcciones/previsualizar y
POST /api/v1/correcciones/{propuesta_id}/decision. Yo implemento la interfaz,
validación del contrato y descarga; tú la generación, almacenamiento temporal,
validación de la decisión y caducidad. El análisis actual sigue siendo de solo
lectura. Confirmemos nombres y campos antes de habilitar la conexión.»

## Flujo y acción aprobada

1. Usuario selecciona un hallazgo y pide previsualización. Esta petición autoriza
   preparar texto propuesto, no crear un archivo descargable ni ejecutar código.
2. Frontend verifica que la respuesta corresponde al original y presenta ambas
   versiones completas como texto, con advertencias y estado parcial si aplica.
3. Casilla inicialmente desmarcada: «He revisado la propuesta y autorizo generar
   y descargar únicamente esta copia corregida».
4. Botón separado «Confirmar y descargar copia». Solo entonces se solicita aprobación
   y se crea el Blob descargable tras validar la respuesta.
5. «Cancelar corrección» cancela localmente y envía rechazo si ya existe propuesta.
   Si la respuesta llega tarde tras cancelar o cambiar de entrada, se descarta.

El navegador solicita descargar un nombre distinto, como `usuarios.corregido.py`.
No se usa File System Access, no se escribe en la ruta original y no se abre ni
ejecuta el `.py`. El usuario conserva el control del diálogo de descarga del navegador.

## Solicitud de previsualización propuesta

```json
{
  "archivo": "usuarios.py",
  "codigo_original": "<texto completo del archivo>",
  "sha256_original": "<SHA-256 hexadecimal del texto UTF-8 exacto>",
  "objetivo": {"linea": 6, "descripcion": "<sugerencia del hallazgo seleccionado>"}
}
```

`objetivo` es contexto no confiable, no una orden ejecutable. No se utiliza el ID
local `api-0` como si fuera un identificador persistente del backend. No se extrae
un programa de `correccion_sugerida`: ese campo puede ser una explicación en prosa.

## Respuesta de previsualización propuesta

```json
{
  "version": "1",
  "propuesta_id": "<identificador opaco no predecible>",
  "estado": "pendiente_confirmacion",
  "accion": "descargar_copia",
  "archivo_original": "usuarios.py",
  "archivo_salida": "usuarios.corregido.py",
  "sha256_original": "<hash del original>",
  "sha256_propuesto": "<hash del contenido propuesto>",
  "codigo_propuesto": "<texto completo de la nueva versión>",
  "caduca_en": "<fecha ISO 8601 UTC>",
  "advertencias": ["Requiere revisión humana antes de usar la copia."]
}
```

El frontend propuesto exige: nombres de salida `.py` simples sin rutas, nombre
distinto del original, máximo 12.000 caracteres, ausencia de NUL, propuesta distinta
del original, hashes válidos y caducidad futura. Hasta diez advertencias de 500
caracteres. Si Backend necesita otros límites o estructura, acordarlos antes de activar.

## Decisión y respuesta

```json
{"decision":"aprobar","sha256_original":"<hash>","sha256_propuesto":"<hash>"}
```

La alternativa es `decision: "rechazar"`. No se reenvía ni se regenera el código al
aprobar; se usa la propuesta inmutable. Respuesta de aprobación:

```json
{
  "version": "1",
  "propuesta_id": "<mismo ID>",
  "estado": "aprobada",
  "archivo_salida": "usuarios.corregido.py",
  "sha256_contenido": "<mismo hash propuesto>",
  "contenido": "<exactamente el texto previsualizado>",
  "tipo_contenido": "text/x-python; charset=utf-8"
}
```

Rechazo: `{"version":"1","propuesta_id":"<mismo ID>","estado":"rechazada"}`,
sin contenido descargable. Errores propuestos: 409 para conflicto de propuesta,
410 para caducidad y errores sanitizados para el resto. Si no hay corrección
sustentada, Backend debe rechazar la creación; no devolver prosa como archivo Python.

## Responsabilidades y protección

| Frontend — Ronald | Backend — Christian |
|---|---|
| Previsualización, casilla, confirmación y cancelación | Crear propuesta como datos sin ejecutar el programa |
| Vincular vista previa a archivo/contenido exactos | Verificar hashes y vincular propuesta a su solicitante |
| Descargar copia solo tras respuesta válida | Identificadores no predecibles, TTL, límites y acceso a propuestas |
| Descartar respuestas tardías y consentimientos anteriores | Resolver aprobar/rechazar de forma consistente e idempotente |
| Renderizar código como texto y conservar fuentes/traza del análisis | No registrar código/secretos en errores ni logs |
| Mantener adaptador real apagado hasta acuerdo | Implementar endpoints y pruebas sin alterar el análisis existente |

Si no hay autenticación, el backend debe definir cómo protege el acceso a las
propuestas; un ID público enumerado o un hash de contenido no autentican al usuario.
La cancelación de red no garantiza que el servidor haya dejado de procesar, por lo
que no debe escribir archivos ni ejecutar acciones durante la previsualización.

## Habilitación y estado

`VITE_CORRECTIONS_API_ENABLED` está ausente/desactivada por defecto. Solo tras
acuerdo y pruebas locales se habilitaría con `1` al compilar. No se activó en Railway,
no se modificó Backend. La demostración usa únicamente
el ejemplo SQL inicial y no atribuye su propuesta fija a Gemini.

Christian aceptó que la aprobación esté vinculada a una propuesta revisable,
autorice solo una copia y permita rechazar sin ejecutar ni sobrescribir originales.
Solicitó estos campos y ejemplos para implementar Backend. Falta confirmar la
estructura técnica definitiva y probar ambos lados localmente antes de habilitar
la conexión. Posteriormente, el líder autorizó subir la rama y abrir un PR en
borrador; no autorizó fusionar ni desplegar. Véase la
[entrega para integración](22-entrega-frontend-integracion.md).
