# CodeGuard — Revisor Inteligente de Código Seguro

Frontend del Caso 10 de UNIANDES. React, Vite, TypeScript y Monaco Editor. Trabajo en `feature/frontend`.

## Ejecutar en Windows

Desde esta carpeta, con Node.js compatible con Vite 8 (verificado con Node.js 24.17.0):

```powershell
npm.cmd ci
npm.cmd run dev
```

Abrir la dirección Local que muestra Vite. Mantener la terminal abierta.
Para detener: Ctrl+C. Para volver a iniciar: `npm.cmd run dev`.

## Demostración para la presentación

1. La aplicación abre en **Demo**, con un ejemplo Python.
2. Pulsar **Probar análisis**: aparecen tres hallazgos en las líneas 7, 12 y 16.
3. Pulsar el título o la ubicación de un hallazgo para situar el cursor en su línea.
4. Abrir **Ver corrección sugerida** y filtrar por severidad.
5. Elegir **Sin hallazgos**, **Error del servidor** o **Error de conexión** en el selector para probar esos estados.
6. Probar **Cancelar** durante un análisis.
7. Seleccionar **Archivo .py** para previsualizar un archivo UTF-8 propio.
8. ZIP y GitHub ofrecen una demo de dos archivos ficticios, identificados con el prefijo `demo/`. No se abre el ZIP ni se descarga el repositorio.
9. Descargar el informe JSON; queda identificado como demostración.

La demo reconoce únicamente tres patrones mediante expresiones regulares. Puede generar falsos positivos y negativos: **no es IA ni un analizador de seguridad real**. El escenario vacío fuerza cero hallazgos para probar la interfaz, independientemente del código.

## Integración real disponible

Contrato verificado en `origin/feature/backend-ia`, commit `cf26cad`, el 22 de octubre de 2026. La interfaz no modifica archivos del backend.

```http
POST /api/v1/analizar
Content-Type: application/json
```

Solicitud:

```json
{ "archivo": "ejemplo.py", "codigo": "print('Hola')" }
```

Respuesta:

```json
{
  "archivo": "ejemplo.py",
  "estado": "analizado",
  "hallazgos": [
    {
      "linea": 1,
      "severidad": "alta",
      "categoria": "Ejemplo",
      "titulo": "Título del hallazgo",
      "explicacion": "Explicación del riesgo",
      "correccion_sugerida": "Corrección recomendada"
    }
  ]
}
```

Severidades: `critica`, `alta`, `media`, `baja`.
El backend limita `archivo` a 255 caracteres y `codigo` a 12.000.
El frontend comprueba el contrato; una respuesta inválida se muestra como error, nunca como cero hallazgos.

**Pasos para conectar:**

1. El compañero debe iniciar su backend en `http://127.0.0.1:8000` con su configuración de IA.
2. Iniciar el frontend con Vite y elegir **API real**.
3. Usar **Código**, **Archivo .py** o **Proyecto .zip**. Código usa JSON en `/api/v1/analizar`. Python se previsualiza localmente y se envía (con sus ediciones) como multipart, campo `archivo`, a `/api/v1/archivos`. ZIP se envía sin descomprimir al endpoint `/api/v1/archivos/zip`, con el mismo campo multipart.
4. Vite reenvía `/api` al backend mediante el proxy de `vite.config.ts`, sin modificar el backend ni requerir CORS para este flujo local.

Para otra dirección, copiar `.env.example` a `.env.local`, establecer `VITE_API_BASE_URL` y reiniciar Vite. Una dirección de otro origen requiere que el backend autorice CORS. El proxy de Vite solo funciona en desarrollo: en producción se necesita un proxy de `/api` o una URL pública de backend con CORS.

**Nunca poner claves Gemini u otros secretos en variables VITE\_**: se incluyen en el navegador.
El servicio HTTP está en `src/services/api.ts`; no llama a Gemini ni ejecuta Python.

## Pendientes de coordinación

- El backend todavía no incluye descarga de GitHub. El control está presente; su envío real queda deshabilitado con una explicación. Acordar la ruta, solicitud y contrato de respuesta.
- ZIP ya permite carga y resultados por archivo: límite de 5 MiB, hasta 5 archivos Python y 12.000 caracteres en total, validados por el backend. Respuesta: `{archivo_zip, estado: "analizado", total_archivos, informes: [RespuestaAnalisis]}`.
- El backend no devuelve el contenido de los archivos ZIP. La interfaz muestra archivos, hallazgos y números de línea, pero explica que no puede marcar el código sin ese contenido. Para completarlo, acordar que cada informe incluya el código o una ruta segura para recuperarlo. La demo sí ilustra el editor con varios archivos ficticios.
- Confirmar el backend ejecutándose para la prueba completa con IA. Las pruebas automatizadas simulan HTTP y no acreditan una conexión real con Gemini.
- Las líneas fuera del archivo se conservan en el informe, pero no se marcan en el editor.
- Las consultas tienen tiempo límite de 60 segundos (180 segundos para ZIP) y permiten cancelación. Cancelar el navegador no garantiza detener un trabajo que ya ejecuta el backend.

## Estructura

- `src/components/`: entradas, editor, resultados e iconos.
- `src/pages/HomePage.tsx`: composición y flujo de pantalla.
- `src/services/api.ts`: validación, HTTP y adaptación del contrato.
- `src/services/demo.ts`: simulación local explícita.
- `src/types/analysis.ts`: tipos compartidos.
- `src/styles/global.css`: estilos y adaptación móvil.
- `tests/analysis.test.ts`: pruebas de límites, contrato, errores, demo y cancelación.

Monaco y su worker se sirven localmente, sin CDN. Su tamaño hace que Vite pueda advertir sobre un paquete grande; no es un fallo de compilación.
Se fija DOMPurify 3.4.17 mediante un override de Monaco para resolver los avisos observados en 3.4.15; revisar el override al actualizar Monaco.

## Verificaciones

```powershell
npm.cmd test
npm.cmd run build
npm.cmd audit
```

Antes de subir cambios, revisar `git status` y confirmar `feature/frontend`.
Se incluyen `package.json` y `package-lock.json`; se excluyen `node_modules`, `dist` y archivos `.env` locales.

## Subir a GitHub

Desde la raíz del repositorio:

```powershell
git branch --show-current
git add frontend
git diff --cached --stat
git commit -m "feat(frontend): crear interfaz de revision segura con Monaco"
git push -u origin feature/frontend
```

Crear un pull request con base `main` y compare `feature/frontend`. Explicar que faltan la descarga GitHub y el contenido de los archivos ZIP para resaltarlos. Adjuntar capturas. No integrar en main sin revisión del equipo.
