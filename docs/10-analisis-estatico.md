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
- Cada ejecución usa `subprocess.run(shell=False)`, `cwd` temporal,
  ambiente reducido, tiempo máximo y límite de 1 MB de salida.
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
abstención de Gemini+RAG. Si la IA falla por error HTTP, la respuesta de la
ruta principal también falla; el endpoint estático **sí** funciona autónomamente.
Una política explícita de degradación de la ruta combinada queda como decisión
pendiente de producto.

## Estados y fallos
`completo`: ambas herramientas disponibles y válidas.
`parcial`: una herramienta pudo analizar, la otra falló.
`no_disponible`: ninguna pudo completar el análisis.
Los fallos internos y `stderr` no se devuelven al usuario. Una ausencia de
hallazgos con estado `parcial` no equivale a código sin vulnerabilidades.

## Integración de frontend (responsabilidad del equipo)
El frontend necesita mostrar por separado el bloque
`analisis_estatico.hallazgos` y los estados `herramientas`; no debe
mezclarlo en la lista RAG ni inventar referencias. La documentación de la API
está en `/docs` y se dispone de pruebas de contrato para las cuatro entradas.
El componente visual queda pendiente hasta que el equipo de frontend valide
esta estructura.

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
