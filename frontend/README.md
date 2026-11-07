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

Iniciar el backend en `http://127.0.0.1:8000`, configurar su proveedor de IA en el `.env` de la raíz y seleccionar **API real**. El proxy de desarrollo de Vite reenvía `/api` y `/agente` a ese servidor; `CODEGUARD_DEV_API_TARGET` permite cambiar el destino local.

El agente ya está conectado al análisis principal de código y `.py`. El bloque **Agente de revisión** explica este recorrido y ofrece **Abrir laboratorio del agente** (`/agente/demo`) en otra pestaña, conservando el editor. Abrir ese enlace no transmite el código ni llama a Gemini. El laboratorio es una pantalla independiente que permite escoger inspección AST local sin IA o análisis con Gemini; no es el modo Demo simulado de React.

| Entrada | Endpoint | Formato |
|---|---|---|
| Código o archivo Python | `/api/v1/agente/analizar` | JSON: `archivo`, `codigo` visible/editado, `max_pasos: 3`, `version_herramientas: "2"` |
| ZIP | `/api/v1/archivos/zip` | Multipart: campo `archivo` |
| GitHub | `/api/v1/repositorios/github` | JSON: `url` |

Referencia de esta revisión: `467d00e` (integración PR #48). El agente devuelve `informe`, pasos y decisiones: React muestra el **Proceso de revisión del agente** y conserva la traza en el JSON. El informe incluye `archivo`, `estado`, `hallazgos`, `fuentes` y `mensaje`; el estado parcial conserva la evidencia disponible sin afirmar un análisis completo. Cada hallazgo puede incluir IDs en `referencias`. Una fuente contiene `id`, `documento`, `seccion`, `fuente`, `url` y `distancia`. Véase el [contrato del agente v2](../docs/contrato-agente-v2/README.md).

ZIP/GitHub usan revisión por archivo, no el agente v2. Cuando el presupuesto está habilitado por la configuración acordada, primero se prepara y confirma la propuesta según el [contrato de presupuesto](../docs/28-presupuesto-proyectos.md). Este ajuste no cambia los flags.

Las citas se resuelven dentro del informe de su archivo antes de combinar resultados ZIP. Las referencias desconocidas se identifican sin inventar metadatos. Los errores de contrato no se convierten en respuestas sin hallazgos. La abstención y el análisis parcial se muestran en pantalla y se conservan al exportar.

Para otro servidor, configurar `VITE_API_BASE_URL` en `.env.local` de `frontend/` y reiniciar Vite. El enlace al laboratorio usa esa misma base. Una URL de otro origen requiere CORS autorizado para las peticiones de la API. En el despliegue conjunto se deja la base vacía: FastAPI sirve `/api` y `/agente/demo` en el mismo dominio. En un hosting separado deben publicarse ambas rutas en el backend configurado; el proxy de Vite solo sirve para desarrollo.

**No configurar claves privadas en variables `VITE_`: su contenido llega al navegador.** La IA se llama únicamente desde el backend.

## Límites y funcionalidades pendientes

- Código: hasta 12.000 caracteres; nombre Python de hasta 255 caracteres.
- Python: hasta 48 KB y texto UTF-8, sujeto al límite de caracteres.
- ZIP: hasta 5 MiB, 5 archivos Python y 12.000 caracteres en total, con validación adicional en backend.
- GitHub admite repositorios públicos mediante la ruta correspondiente; requiere conectividad y está sujeto a validaciones y límites del backend.
- Si la respuesta de proyecto no incluye código fuente, se muestran hallazgos y líneas con aviso de que falta el contenido para resaltarlo. No se fabrica una vista previa.
- Tiempo máximo de espera: 180 segundos para el agente y las rutas directas de proyectos. Cancelar en el navegador no garantiza detener un trabajo que ya comenzó en el servidor.
- Sin proveedor disponible, el agente puede conservar evidencia local y devolver estado parcial; las rutas directas pueden devolver errores de disponibilidad. Eso no equivale a una evaluación con Gemini real.

## Verificación

```powershell
npm.cmd test
npm.cmd run lint
npm.cmd run build
```

La suite cubre entradas, contrato, HTTP simulado, fuentes, abstención, exportación y trazabilidad. La [evidencia del rediseño](../docs/evidencias/semana-3/redisenointerfaz/README.md) incluye pruebas y capturas de escritorio y móvil. La evaluación de 20 casos se documenta en [07-evaluacion.md](../docs/07-evaluacion.md).

Para verificar la integración por HTTP con FastAPI y ChromaDB reales, ejecutar desde la raíz `.\.venv\Scripts\python.exe eval/run_integration.py`. Los proveedores externos se simulan; las pruebas HTTP se omiten en `npm test` cuando falta su servidor/configuración. Véase la [explicación de integraciones](../docs/integracion-frontend-evaluacion.md). La comprobación específica del acceso al agente está en [estas evidencias](../docs/evidencias/semana-4/acceso-agente-20261107/README.md).

Monaco genera una advertencia de tamaño del paquete al compilar; la compilación termina correctamente.

## Archivos principales

- `src/pages/HomePage.tsx`: composición, carga, modos y flujo de análisis.
- `src/components/CodeEditor.tsx`: tema local y marcadores de seguridad de Monaco.
- `src/components/FindingsPanel.tsx`: informe, filtros, correcciones y fuentes.
- `src/components/EvidenceTrace.tsx`: vínculo entre selección y referencias.
- `src/services/api.ts`: validaciones, transporte y normalización por archivo.
- `src/services/demo.ts`: simulación explícita y ejemplos.
- `src/styles/global.css`: paleta, composición y adaptación a pantallas.
