# Revisor Inteligente de Código Seguro — Frontend

Interfaz del proyecto de titulación UNIANDES, desarrollada con React, TypeScript, Vite y Monaco Editor. Rama de trabajo: `feature/frontend`.

## Diseño integrado

Se implementó la [propuesta visual aprobada](../docs/diseno/propuesta-revisor-elegante-v3.png): encabezado académico, paleta azul noche/turquesa/ámbar, editor Python e informe en dos paneles y trazabilidad entre hallazgos y fuentes. En móvil los paneles se apilan y el código se ajusta al ancho disponible.

El diseño está construido con componentes y CSS; la imagen es una referencia, no el contenido de la interfaz. Las tipografías del sistema y los recursos de Monaco se sirven localmente.

## Ejecutar en Windows

Desde `frontend/`, con una versión de Node compatible con Vite 8:

```powershell
npm.cmd ci
npm.cmd run dev -- --host 127.0.0.1
```

Abrir la dirección indicada por Vite. Para detener el servidor, usar Ctrl+C.

## Demostración

La pantalla abre en **Demo**, sin llamar al proveedor de IA ni consultar ChromaDB. El ejemplo `usuarios.py` tiene nueve líneas y muestra un hallazgo de inyección SQL en la línea 6 al pulsar **Probar análisis**.

- El hallazgo selecciona la línea en Monaco y actualiza la sección de trazabilidad.
- La corrección aparece expandida y se puede contraer.
- Las referencias locales ilustrativas se identifican expresamente como demostración; no son resultados de recuperación RAG.
- El filtro permite cambiar la severidad; el selector de escenarios permite probar cero hallazgos, errores y cancelación.
- **Exportar JSON** conserva modo, estado, mensaje, archivos, hallazgos y fuentes.
- **Cargar ejemplo** vuelve al código SQL inicial.

La demo reconoce patrones sencillos mediante expresiones regulares, con posibles falsos positivos y negativos. Los ZIP y GitHub en Demo usan archivos ficticios con prefijo `demo/`; no se analizan sus contenidos.

## Conexión con el backend

Iniciar el backend en `http://127.0.0.1:8000`, configurar su proveedor de IA en el `.env` de la raíz y seleccionar **API real**. El proxy de desarrollo de Vite reenvía `/api` a ese servidor.

| Entrada | Endpoint | Formato |
|---|---|---|
| Código | `/api/v1/analizar` | JSON: `archivo`, `codigo` |
| Archivo Python | `/api/v1/archivos` | Multipart: campo `archivo`; se envía el código visible y editado |
| ZIP | `/api/v1/archivos/zip` | Multipart: campo `archivo` |

El contrato integrado es el de `main` base `8f27ddc`. Una respuesta individual incluye `archivo`, `estado` (`analizado` o `abstenido`), `hallazgos`, `fuentes` y `mensaje`. Cada hallazgo puede incluir IDs en `referencias`. Una fuente contiene `id`, `documento`, `seccion`, `fuente`, `url` y `distancia`.

Las citas se resuelven dentro del informe de su archivo antes de combinar resultados ZIP. Las referencias desconocidas se identifican sin inventar metadatos. Los errores de contrato no se convierten en respuestas sin hallazgos. La abstención y el análisis parcial se muestran en pantalla y se conservan al exportar.

Para otro servidor, configurar `VITE_API_BASE_URL` en `.env.local` de `frontend/` y reiniciar Vite. Una URL de otro origen requiere CORS autorizado en el backend. En producción debe configurarse un proxy `/api` o una URL de backend con CORS; el proxy de Vite solo sirve para desarrollo.

**No configurar claves privadas en variables `VITE_`: su contenido llega al navegador.** La IA se llama únicamente desde el backend.

## Límites y funcionalidades pendientes

- Código: hasta 12.000 caracteres; nombre Python de hasta 255 caracteres.
- Python: hasta 48 KB y texto UTF-8, sujeto al límite de caracteres.
- ZIP: hasta 5 MiB, 5 archivos Python y 12.000 caracteres en total, con validación adicional en backend.
- La API todavía no descarga GitHub. La interfaz explica esta limitación y deshabilita su envío real.
- ZIP no devuelve código fuente: se muestran hallazgos y líneas, con aviso de que falta el contenido para resaltarlo. No se fabrica una vista previa.
- Tiempo máximo de espera: 60 segundos por fragmento y 180 por ZIP. Cancelar en el navegador no garantiza detener un trabajo que ya comenzó en el servidor.
- La API local de esta entrega devuelve HTTP 503 mientras falta `GEMINI_API_KEY`. La evaluación completa de respuestas queda pendiente de esa configuración.

## Verificación

```powershell
npm.cmd test
npm.cmd run lint
npm.cmd run build
```

La suite cubre entradas, contrato, HTTP simulado, fuentes, abstención, exportación y trazabilidad. La [evidencia del rediseño](../docs/evidencias/semana-3/redisenointerfaz/README.md) incluye pruebas y capturas de escritorio y móvil. La evaluación de 20 casos se documenta en [07-evaluacion.md](../docs/07-evaluacion.md).

Para verificar la integración por HTTP con FastAPI y ChromaDB reales, ejecutar desde la raíz `.\.venv\Scripts\python.exe eval/run_integration.py`. Solo la respuesta externa de IA se simula. Este flujo ejecuta nueve pruebas dedicadas; se omiten en `npm test` cuando el servidor temporal no está activo. Véase la [explicación de integraciones](../docs/integracion-frontend-evaluacion.md).

Monaco genera una advertencia de tamaño del paquete al compilar; la compilación termina correctamente.

## Archivos principales

- `src/pages/HomePage.tsx`: composición, carga, modos y flujo de análisis.
- `src/components/CodeEditor.tsx`: tema local y marcadores de seguridad de Monaco.
- `src/components/FindingsPanel.tsx`: informe, filtros, correcciones y fuentes.
- `src/components/EvidenceTrace.tsx`: vínculo entre selección y referencias.
- `src/services/api.ts`: validaciones, transporte y normalización por archivo.
- `src/services/demo.ts`: simulación explícita y ejemplos.
- `src/styles/global.css`: paleta, composición y adaptación a pantallas.
