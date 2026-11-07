# CODEGUARD · Análisis estático (Ruff + Bandit)

## Motivación y alcance
CODEGUARD combina Gemini+RAG (interpretación contextual con citas verificables) con
Ruff (reglas de calidad de Python) y Bandit (indicadores estáticos de seguridad).
**Ningún resultado estático se presenta como hallazgo certificado**, y la
existencia de una regla de Bandit no equivale a una prueba de explotación.

Los dos informes tienen **procedencia separada**: las alertas de Ruff/Bandit no
se incluyen en `hallazgos` de Gemini, pues ese campo exige citas RAG.
Los informes estáticos proporcionan `herramienta`, `regla`, `tipo`,
`linea`, `severidad`, `confianza` (Bandit) y `referencia` cuando la
herramienta suministra documentación. Nunca se inventan fuentes OWASP o MITRE.

## Herramientas
- **Ruff:** `ruff check --isolated --select E4,E7,E9,F --output-format json --stdin-filename codigo.py -`.
  Analiza calidad y errores; se usan reglas sin superposición de seguridad
  `S` para no duplicar los hallazgos de Bandit.
- **Bandit:** `bandit -f json -q /tmp/…/codigo.py`.
  Procesa AST de Python, sin ejecutar código recibido, con límite 12 s.
- Cada ejecución usa `subprocess.Popen(shell=False)`, `cwd` temporal y ambiente reducido.
  Dos lectores drenan stdout/stderr simultáneamente. Retienen como máximo
  1.000.000 bytes combinados; al superar el presupuesto se mata y recolecta
  el proceso y se devuelve `error`, sin salida parcial ni stderr público.
  El timeout de 12 s cubre la espera del proceso y el drenaje; se devuelve
  `timeout` tras la terminación y limpieza. Stdin es un archivo temporal acotado
  por la entrada validada o DEVNULL; nunca hereda la terminal.
  Cada lector puede retener además un bloque transitorio de hasta 64 KiB.
  Esto limita la captura, no la memoria total del analizador, del JSON parseado
  ni del contenedor. El control de recursos del árbol de procesos requiere
  mecanismos de plataforma independientes.
  El nombre enviado por el usuario **no** se utiliza para construir la ruta
  temporal; solo se admiten rutas relativas seguras para archivos internos.

## Contratos públicos

### Endpoint autónomo
`POST /api/v1/estatico/analizar`

Ejemplo:
```json
{"archivo":"usuarios.py","codigo":"eval(input())"}
```

Respuesta:
```json
{
  "archivo":"usuarios.py",
  "estado":"completo",
  "hallazgos":[
    {
      "herramienta":"bandit",
      "regla":"B307",
      "tipo":"seguridad",
      "linea":1,
      "columna":null,
      "severidad":"alta",
      "titulo":"Bandit B307: blacklist",
      "descripcion":"...",
      "confianza":"alta",
      "referencia":"..."
    }
  ],
  "herramientas":[
    {"herramienta":"ruff","estado":"ok","hallazgos":0},
    {"herramienta":"bandit","estado":"ok","hallazgos":1}
  ],
  "mensaje":null
}
```

Los valores ilustrativos de descripción no deben confundirse con una respuesta
obtenida de una ejecución concreta.

### Integración en las entradas existentes
Con `STATIC_ANALYSIS_ENABLED=1`, cada `RespuestaAnalisis` incluye un campo
opcional **`analisis_estatico`**. Esto abarca:
- `/api/v1/analizar` (código),
- `/api/v1/archivos` (Python),
- cada informe de `/api/v1/archivos/zip`,
- cada informe de `/api/v1/repositorios/github`.

Con la bandera desactivada el campo se omite para conservar el contrato anterior.
La salida del motor estático no modifica `hallazgos`, `fuentes` ni el estado de
abstención de Gemini+RAG. La integración resiliente puede conservar el resultado
estático como respuesta contextual `parcial` ante errores de Gemini, según el
contrato de [resiliencia](11-resiliencia-gemini.md); no representa un informe IA
completo. El endpoint estático también funciona autónomamente.

## Estados y fallos
`completo`: ambas herramientas disponibles y válidas.
`parcial`: una herramienta pudo analizar, la otra falló.
`no_disponible`: ninguna pudo completar el análisis.
Los fallos internos y `stderr` no se devuelven al usuario. Una ausencia de
hallazgos con estado `parcial` no equivale a código sin vulnerabilidades.

## Integración de frontend (responsabilidad del equipo)
El frontend muestra por separado el bloque
`analisis_estatico.hallazgos` y los estados `herramientas`; no debe
mezclarlo en la lista RAG ni inventar referencias. La documentación de la API
está en `/docs` y se dispone de pruebas de contrato para las cuatro entradas.
El componente visual y la exportación fueron integrados mediante PR #19/#23;
las evidencias y el alcance constan en [el cierre QA](12-cierre-qa-entrega4.md).

## Seguridad y límites pendientes de aceptación
- Limitar carga de código a 12.000 caracteres y rutas relativas seguras.
- No pasar `shell=True` ni ejecutar `python codigo.py`.
- Conservar el código fuente temporal solo durante el análisis.
- Ejecutar Ruff/Bandit sin red saliente, con cuotas de CPU y memoria a nivel de
  contenedor para una defensa adicional. **No se ha configurado aún un sandbox
  de procesos ni un bloqueo de red por subprocess; no debe afirmarse tal control.**
- Dos analizadores secuenciales de hasta 12 segundos cada uno pueden aumentar
  la latencia especialmente con ZIP/GitHub de cinco archivos.
- Un máximo de dos análisis HTTP concurrentes está configurado en producción.
- En un despliegue de varias réplicas se necesita una cuota de peticiones
  compartida.
- Ejecutar tests unitarios, tests HTTP y pruebas smoke reales antes de fusionar
  esta implementación a la rama que despliega Railway.

## Política de priorización: severidad × confianza

Esta política reemplaza las descripciones anteriores que presentaban la
categoría como segundo criterio.

Los pesos y factores se centralizan en `app/config/priorizacion.py`:

- Severidad: crítica 8, alta 4, media 2 y baja 1.
- Confianza: alta 1.0, media 0.8 y baja 0.6.

`calcular_puntuacion(severidad, confianza)` devuelve el producto de ambos
valores cuando los dos están reconocidos. Si falta alguno o no está
reconocido, devuelve `None`; nunca asigna cero a una confianza ausente.
Son ponderaciones operativas del proyecto, no probabilidades calibradas.

El orden de presentación conserva la regla lexicográfica existente:
severidad dominante; confianza conocida (alta, media y baja), dejando la
confianza ausente detrás dentro de la misma severidad; categoría como tercer
criterio (seguridad, desconocida y calidad); y orden original estable para
los empates restantes. La puntuación descendente y el orden lexicográfico
son equivalentes para las doce combinaciones conocidas.

Bandit aporta confianza exclusivamente mediante `issue_confidence`.
Ruff y el informe de IA no proporcionan confianza en sus contratos actuales,
por lo que permanecen sin puntuación cuando ese dato no existe. No se inventa
ni se deduce confianza a partir de la severidad, no se añade un campo
obligatorio al contrato de IA y no se modifica la severidad original.

