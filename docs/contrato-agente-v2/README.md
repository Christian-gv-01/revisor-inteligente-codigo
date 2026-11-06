# Contrato optativo v2: herramientas contextuales del agente

Base inicial: `605d142`. Referencia integrada: `9c97ca1` (PR #45).
Endpoint existente: `POST /api/v1/agente/analizar`.
Enviar `version_herramientas: "2"` habilita el contrato nuevo. Omitirlo o enviar
"1" conserva el recorrido anterior. Desde PR #45, el frontend solicita v2 para
código y .py y sigue interpretando v1. ZIP/GitHub conservan análisis por archivo.

**Los diez JSON son ejemplos sintéticos**, generados por FastAPI y el orquestador
reales con proveedor, RAG y Ruff/Bandit simulados. `modo: "gemini_real"` es el
valor del contrato de la ruta, no evidencia de una llamada real en estos ejemplos.
No son resultados diagnósticos, propuestas activas ni métricas del modelo.

## Ejemplos y reproducción

| Archivo | Uso |
|---|---|
| [01 solicitud](01-solicitud-contexto-y-referencia.json) | Código Python, versión2, máximo tres pasos |
| [02 ampliar](02-decision-ampliar-contexto.json) | Decisión interna del planificador con línea tipada |
| [03 buscar](03-decision-buscar-referencia.json) | Decisión con categoría permitida |
| [04 respuesta completa](04-respuesta-contexto-y-referencia.json) | Inspección inicial, ventana, referencia y síntesis |
| [05 solicitud breve](05-solicitud-finalizacion-anticipada.json) | Caso para finalizar sin más inspecciones |
| [06 finalizar](06-decision-finalizar.json) | Argumentos vacíos; sigue una síntesis final |
| [07 respuesta anticipada](07-respuesta-finalizacion-anticipada.json) | Un paso, una decisión, finalización anticipada |
| [08 error de herramienta](08-respuesta-error-herramienta.json) | Error RAG con traza conservada y respaldo AST |
| [09 compatibilidad v1](09-respuesta-v1-compatible.json) | Sin metadatos ni herramientas de v2 |
| [10 esquema de decisión](10-esquema-decision.json) | Tipos y límites generados por Pydantic |

Desde la raíz, con Python/dependencias backend:

```powershell
backend\.venv\Scripts\python.exe docs/contrato-agente-v2/generar.py
```

Siempre sustituye servicios externos; no ofrece modo de generación real. La
prueba `backend/tests/test_contrato_agente_v2.py` compara lo regenerado con los
JSON publicados. Las decisiones 02/03/06 son salidas internas del planificador,
no cuerpos de nuevos endpoints ni acciones que el navegador deba ejecutar.

## Argumentos y resultados

- `ampliar_contexto`: `{"linea":2}`. Entero estricto, 1..12000 y existente en el
  código recibido. Se rechazan booleanos, floats, cadenas y propiedades extra.
  Devuelve `linea_objetivo`, `linea_inicio`, `linea_fin` y hasta siete `lineas`:
  `numero`, `texto` (hasta500 caracteres) y `truncada`. Ventana fija de radio3;
  nunca importa, ejecuta ni modifica el código.
- `buscar_referencia`: `{"categoria":"inyeccion_sql"}`. Lista cerrada:
  `ejecucion_codigo`, `inyeccion_sql`, `inyeccion_comandos`, `inyeccion`,
  `credenciales`, `rutas`. Cada categoría usa una consulta fija al índice local.
  Devuelve categoría y hasta dos fragmentos, texto de hasta2000 caracteres, ID
  exacto y metadatos acotados. La procedencia RAG debe ser de seguridad; una
  etiqueta de documento no puede convertir una fuente del proyecto en oficial.
  No admite consulta libre ni URL. Las URLs salientes son metadatos HTTPS de
  OWASP/CWE, validados; la herramienta no los visita ni descarga.
- Herramientas AST previas y `finalizar`: argumentos vacíos u omitidos.
  Los argumentos vacíos se omiten al serializar decisiones para conservar v1.
  Los pasos v2 ejecutados sí incorporan sus argumentos; el inicial automático
  conserva la forma anterior.

El esquema representa los tipos de argumentos; la correspondencia entre nombre
y tipo se verifica además en código. Un argumento correcto para otra herramienta
se rechaza. Se mantiene la distinción entre un indicador y un hallazgo validado.

## Trazabilidad y finalización

`pasos` conserva solo ejecuciones concluidas; `decisiones` indica `ejecutada`,
`finalizar`, `repetida` o, en v2, `error`. No mostrar una decisión `error` como si
hubiese devuelto resultado. Una respuesta degradada puede incluir inspecciones
de respaldo `origen: "local"`; no atribuirlas al modelo.

La respuesta v2 añade `version_herramientas: "2"` y, cuando se determinó,
`terminacion`: `finalizacion_anticipada`, `max_pasos` o `herramienta_repetida`.
Finalizar evita inspecciones posteriores y conserva una síntesis con la evidencia
ya reunida; no certifica cobertura completa ni ausencia de vulnerabilidades.
Si después falla la síntesis, su fase y estado parcial siguen visibles.

`fase_error` admite `herramienta` en v2, además de `planificacion`/`informe`.
Argumentos inválidos del modelo se rechazan en planificación sin publicar el
payload crudo. Una línea tipada pero inexistente o RAG no disponible produce
error de herramienta. Se mantiene el respaldo HTTP200/degradado existente.

Los resultados acotados y argumentos se envían a la siguiente decisión y a la
evidencia de síntesis. Las referencias efectivamente buscadas se reutilizan como
contexto y allowlist de citas; si no se recuperó ninguna, permanece la recuperación
heurística existente. Todas las cadenas recuperadas son datos no confiables.
Resolver un ID no prueba que la cita sea semánticamente pertinente.

## Límites y coordinación visual

No se amplían límites del PR42: tres pasos totales incluida inspección inicial,
dos decisiones, una síntesis, máximo nueve intentos Gemini y plazo cooperativo
de150 s para la solicitud. Ruff/Bandit siguen siendo obligatorios. Buscar en el
índice local no añade llamadas Gemini. Repetir herramienta/argumentos detiene el
bucle; argumentos diferentes ocupan otro paso dentro del mismo máximo.

El frontend integrado valida y muestra ventanas de código, fragmentos documentales,
argumentos, errores y motivo de terminación, conservándolos al exportar JSON.
El campo `resultado` de una
herramienta contextual tiene su forma propia y no lleva una falsa
`sintaxis_valida`. Las citas del informe conservan su validación actual.

La [revisión frontend y trazabilidad](../29-revision-frontend-agente-presupuesto.md)
describe el recorrido integrado. La comparación real, la regla severidad × confianza
y la versión activa en Railway requieren evidencias independientes. Los ejemplos
de esta carpeta siguen siendo sintéticos, no resultados de la comparación final.
