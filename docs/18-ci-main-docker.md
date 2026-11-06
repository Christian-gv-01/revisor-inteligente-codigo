# CI en main, secretos y modelo de embeddings en Docker

## Alcance

Respuesta a la revisión docente: ejecutar pruebas también tras un push a `main`, incorporar Gitleaks y descargar el modelo de embeddings durante el build. No modifica el contrato de confirmación humana ni los cambios locales de backend/frontend de los compañeros.

Los workflows de backend, frontend, integración HTTP y captura estática conservan sus disparadores de PR e incorporan `push` a `main` y ejecución manual. Los workflows de secretos e imagen Docker también se ejecutan en PR y en `main`.

## Secretos

Gitleaks 8.30.1 se descarga desde su publicación oficial y se verifica contra el SHA-256 del archivo de distribución antes de ejecutarlo. Se usa el CLI directamente, sin depender de una licencia de la acción comercial. Checkout recupera historial con `fetch-depth: 0`, no persiste credenciales y el escaneo recorre los refs disponibles con `--all`. Los valores se redactan; no se publican reportes con secretos completos.

`.gitleaks.toml` conserva las reglas por defecto. Su única excepción inicial es la línea exacta y el SHA-256 conocido de `frontend/src/services/api.ts` en la evidencia `agente-integrado-20261105/validacion.json`. Se contrastó con el hash del archivo y se verificó que otro valor en ese campo sigue siendo detectado. No se excluyen directorios completos de pruebas, documentos ni commits.

El primer escaneo completo de Actions revisó 168 commits y detectó además el fixture P26 del dataset histórico `eval/preguntas_referencia_final.json`, commit `288616b3fe1be68a52f1971b8713e87c0a1cba80`, línea 336. Su contexto es un caso de evaluación de credenciales almacenadas como literal. La cabecera declara HS256, pero la firma decodificada tiene 24 bytes en lugar de 32: no es una firma HS256 válida. Se clasifica como token ilustrativo de prueba, sin evidencia de una credencial real; no se afirma que haya sido revocado. `.gitleaksignore` registra únicamente su fingerprint completo, ligado a ese commit y ubicación inmutables. Los JWT nuevos y el resto del archivo siguen bajo las reglas por defecto.

Un resultado sin hallazgos no certifica ausencia absoluta de secretos, revocación de credenciales ni las variables privadas configuradas en Railway. Cualquier detección adicional del historial debe clasificarse sin mostrar su valor; no se aceptan excepciones generales para obtener una corrida verde.

## Modelo dentro de la imagen

La versión fijada de ChromaDB utiliza MiniLM ONNX y guarda el modelo en `Path.home()/.cache/chroma`. Docker descarga el modelo y comprueba una inferencia de 384 dimensiones durante el build. `HOME` y el home del usuario `codeguard` coinciden en `/opt/codeguard`, por lo que `gosu` conserva esa ruta al abandonar privilegios.

El modelo queda fuera de `/data`: montar el volumen no lo oculta. ChromaDB mantiene su índice en `/data/chroma` y el arranque recupera el índice existente o lo inicializa. No requiere instalar PyTorch ni cambiar el modelo o el corpus. El primer build necesita acceso al proveedor del modelo y añade su tamaño a la imagen.

El nuevo workflow construye la imagen y arranca un contenedor con `--network none`, `/data` temporal vacío y una clave ficticia que solo permite superar la comprobación de configuración. No llama a Gemini. Comprueba `/health` en el puerto alternativo 8093, el modelo bajo `/opt/codeguard` y que el proceso principal tenga UID 10001.

## Verificación y despliegue

Antes de abrir el PR se verificaron sintaxis YAML/shell, 250 pruebas backend/QA, Gitleaks del árbol de trabajo y una inferencia con caché precargada bloqueando conexiones de red. El entorno local no dispone de Docker; la construcción y el arranque real se verifican en GitHub Actions. El escaneo del historial completo también se acredita mediante Actions, no mediante la copia local del árbol.

Estas pruebas no despliegan ni configuran Railway. Tener CI en `main` no garantiza que Railway espere sus resultados: el responsable debe revisar la rama conectada, los despliegues de PR y el mecanismo que condiciona la publicación a los checks. No se añade un deploy hook ni una credencial de despliegue.

Después de revisar y fusionar, se debe verificar la corrida `push` sobre el commit integrado, el despliegue de esa revisión, salud pública y continuidad de citas. La evaluación final con Gemini real queda para la versión integrada con los compañeros.
