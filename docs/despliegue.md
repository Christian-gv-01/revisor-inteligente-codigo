# Despliegue de CODEGUARD — Semana 4

## Diseño
El Dockerfile genera el frontend React con Node 22 y lo copia a una imagen Python 3.13 con FastAPI. El frontend se sirve en el mismo origen que la API, evitando exponer la clave de Gemini al navegador.

- Aplicación: `/`
- API: `/api/v1/`
- Estado: `/health`
- Agente: `/agente/demo`
- Índice documental persistente: `CHROMA_PATH=/data/chroma`
- Volumen único: `/data` (índice y SQLite); modelo ONNX precargado fuera del volumen, en `/opt/codeguard/.cache/chroma`.
- Solo se realiza la ingesta inicial de `seguridad_python` cuando la colección falta o está vacía. El contexto de proyecto es opcional y NO se ingiere automáticamente.
- Se requiere `GEMINI_API_KEY` como secreto de ejecución, no durante la compilación.

## Prueba local con Docker Desktop (Windows)

1. Confirmar `docker version` y `docker compose version`.
2. Crear el archivo `.env` en la **raíz** del repositorio con `GEMINI_API_KEY` y `GEMINI_MODEL` reales. No publicarlo ni enviarlo a Git.
3. Desde la raíz, ejecutar:

```cmd
docker compose config --quiet
docker compose up --build -d
docker compose ps
docker compose logs --tail=80 codeguard
```

4. Abrir `http://127.0.0.1:8080/` y comprobar `http://127.0.0.1:8080/health`.
5. Usar **API real** para probar un caso de `eval()` con citas. El modelo de embeddings podría descargarse durante el primer arranque.

## Persistencia demostrable

```cmd
docker compose restart codeguard
docker compose ps
docker compose logs --tail=80 codeguard
```

Repetir el mismo análisis después del reinicio y comprobar que vuelve a obtener fuentes. Guardar captura de ambos resultados y del log `índice documental persistente recuperado`. Para una prueba adicional puede ejecutarse `docker compose down` y `docker compose up -d`: el volumen nombrado se conserva.

**No ejecutar `docker compose down -v`**, ya que destruye el volumen y el índice.

## Despliegue HTTPS

El Dockerfile admite un servicio único en hosting con Docker y la variable `PORT`. Configurar en la plataforma:
- `GEMINI_API_KEY` y `GEMINI_MODEL` como variables privadas.
- Un **volumen persistente montado en `/data`**. Railway lo monta como usuario root; el entrypoint prepara permisos y ejecuta ingesta y FastAPI como `codeguard` (UID 10001) mediante `gosu`.
- El HEALTHCHECK usa el puerto de `PORT`, que Railway puede asignar dinámicamente.
- `CHROMA_PATH=/data/chroma`.
- Exposición HTTPS mediante el proxy del proveedor y ruta de salud `/health`.

El puerto 8080 del Compose está restringido a loopback para uso local. **Compose por sí solo no crea una URL pública HTTPS.**

## Seguridad y límites

- No hay ejecución de código Python enviado por usuarios. La ingesta ejecuta únicamente scripts del propio repositorio.
- La imagen inicia brevemente como root únicamente para fijar permisos del volumen. Después ejecuta Python y FastAPI como usuario `codeguard` (UID 10001) y no incluye `.env` ni datos de ChromaDB.
- El endpoint `/health` verifica que la API responde, pero **no** verifica por sí solo la disponibilidad del modelo o del RAG. Demostrar estos componentes con una petición de análisis real.
- Docker activa `RATE_LIMIT_ENABLED=1` (predeterminado 0 en desarrollo local): ventana deslizante de 60 segundos, 30 unidades globales y 10 por IP observada; los endpoints ZIP y GitHub cuestan 5 unidades y el agente Gemini 3. Se devuelve HTTP 429 con `Retry-After`. Los tests normales permanecen sin límites mientras se ejecutan en local.
- El mecanismo de tasa funciona por proceso (30 unidades/minuto globales; 10 por identidad) y **no** usa `X-Forwarded-For` arbitrariamente. Por defecto obtiene la IP de conexión. `TRUST_RAILWAY_REAL_IP=1` únicamente debe habilitarse después de confirmar que **todas** las solicitudes llegan exclusivamente a través del proxy público de Railway que sobrescribe `X-Real-IP`, sin rutas privadas o directas que permitan suplantarlo. El límite global permanece activo incluso sin identidad individual confiable. No afirmar validación pública del límite por visitante hasta completar esa prueba.
- El servicio Docker también activa `CONCURRENCY_LIMIT_ENABLED=1`: dos peticiones costosas simultáneas por proceso. Cuando está saturado, devuelve HTTP 503, `Retry-After: 3` y un mensaje seguro. La ruta `/health` no consume cupo.
- Para varias réplicas de aplicación se necesita un almacén de cuotas compartido como Redis, más un límite agregado de concurrencia. Las reservas actuales no representan tokens consumidos y solicitudes rechazadas pueden gastar cupo de tasa, deliberadamente para prevenir abuso.
- Antes de abrir la URL al público se debe verificar HTTP 429 real, revisar errores seguros, dependencias y protección contra abuso.
- Revisar el historial Git con un detector de secretos y comprobar que la plataforma no expone el volumen.

## Banderas del candidato de cierre

Docker compila `VITE_PROJECT_BUDGET_ENABLED=1` y
`VITE_CORRECTIONS_API_ENABLED=1`, y arranca con `PROJECT_BUDGET_ENABLED=1`.
Compose toma los mismos valores de `.env`; si se desactiva el presupuesto,
ambos lados deben cambiar conjuntamente. Para revertir la interfaz se necesita
reconstruir, no basta con reiniciar el contenedor. Estas variables son públicas,
nunca credenciales.

Al integrar, Railway puede desplegar automáticamente después de CI. Registrar
el SHA activo, comprobar `/health`, Agent Lab, presupuesto previo y rechazo sin
consumo. No aprobar un proyecto solo para demostrar que el botón existe. El
smoke Docker ejecuta previsualización y rechazo en red aislada y comprueba cero
intentos al proveedor. La aprobación real de análisis consume cuota y debe
quedar registrada por separado.
