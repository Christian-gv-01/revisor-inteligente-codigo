# CODEGUARD — backend de confirmación humana v1

Este paquete agrega el módulo de previsualización y decisión humana conforme a
`docs/20-contrato-confirmacion-humana.md`.

## Contenido

- `backend/app/models/correcciones.py`: modelos y validaciones HTTP.
- `backend/app/services/correcciones.py`: generación, almacenamiento temporal,
  hashes SHA-256, caducidad e idempotencia.
- `backend/app/routes/correcciones.py`: endpoints FastAPI.
- `backend/tests/test_correcciones.py`: pruebas del contrato.
- `APLICAR_EN_WINDOWS.ps1`: integra el router en el `main.py` existente.
- `docs/20-contrato-confirmacion-humana.md`: contrato funcional recibido del frontend.

## Instalación

1. Haz una copia de seguridad o confirma que Git tiene tus cambios actuales.
2. Extrae el ZIP en la raíz del repositorio `revisor-inteligente-codigo`.
   Debe fusionar las carpetas `backend` y `docs`; no extraigas dentro de `backend`.
3. Desde PowerShell, en la raíz del repositorio, ejecuta:

   ```powershell
   .\APLICAR_EN_WINDOWS.ps1
   ```

4. Ejecuta las pruebas desde `backend`:

   ```powershell
   cd .\backend
   python -m pytest tests/test_correcciones.py -v --tb=short
   python -m pytest -q --tb=short
   ```

No se reemplaza `main.py` completo: el script añade el import y el `include_router`
sobre las líneas de integración que ya existen. Crea una copia de seguridad antes
de escribir.

## Endpoints

- `POST /api/v1/correcciones/previsualizar`
- `POST /api/v1/correcciones/{propuesta_id}/decision`

## Decisiones de implementación

- SQLite local en `backend/data/correcciones.sqlite3`.
- TTL de propuesta: 300 segundos.
- El ID aleatorio de propuesta funciona como credencial portadora; solo se almacena
  su hash en SQLite. Sin autenticación de usuario, quien posea el ID puede decidir.
- Los datos del código propuesto se eliminan al caducar; se conserva un tombstone
  por 24 horas para responder HTTP 410 en lugar de confundirlo con un ID inexistente.
- La decisión se serializa con `BEGIN IMMEDIATE`. La misma decisión es idempotente;
  una decisión contraria devuelve HTTP 409.
- El backend devuelve el texto aprobado como JSON. El frontend es quien crea el Blob
  y solicita la descarga local.
- No se crea un archivo corregido en el servidor, no se ejecuta código y no se
  sobrescribe el original.
- La propuesta se valida con `ast.parse`, que analiza sintaxis sin ejecutar Python.
- Se usan las funciones existentes de `app.config` y el SDK Gemini ya presente
  en el backend. No se añade una dependencia nueva.

## Antes de habilitar en el frontend

Probar en local los escenarios de aprobación, rechazo, expiración, hashes alterados,
doble decisión, decisión opuesta y respuesta tardía. Mantener el adaptador real
desactivado hasta completar la prueba conjunta con Frontend.

Este paquete no hace `git add`, `commit`, `push`, merge ni despliegue.
