# Despliegue de CODEGUARD — Semana 4

## Diseño
El Dockerfile genera el frontend React con Node 22 y lo copia a una imagen Python 3.13 con FastAPI. El frontend se sirve en el mismo origen que la API, evitando exponer la clave de Gemini al navegador.

- Aplicación: `/`
- API: `/api/v1/`
- Estado: `/health`
- Agente: `/agente/demo`
- Índice documental persistente: `CHROMA_PATH=/data/chroma`
- Volumen único: `/data` (incluye la caché de embeddings).
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
- Un **volumen persistente montado en `/data`**.
- `CHROMA_PATH=/data/chroma`.
- Exposición HTTPS mediante el proxy del proveedor y ruta de salud `/health`.

El puerto 8080 del Compose está restringido a loopback para uso local. **Compose por sí solo no crea una URL pública HTTPS.**

## Seguridad y límites

- No hay ejecución de código Python enviado por usuarios. La ingesta ejecuta únicamente scripts del propio repositorio.
- La imagen usa un usuario no privilegiado y no contiene `.env` ni datos de ChromaDB.
- El endpoint `/health` verifica que la API responde, pero **no** verifica por sí solo la disponibilidad del modelo o del RAG. Demostrar estos componentes con una petición de análisis real.
- Antes de abrir la URL al público se deben incorporar límites de tasa, revisar errores seguros, dependencia y protección contra abuso.
- Revisar el historial Git con un detector de secretos y comprobar que la plataforma no expone el volumen.
