# 01. Propuesta del proyecto

> Ampliación local del 6 de noviembre: Ronald asume Frontend y documentación del
> producto. Se incorpora un flujo de previsualización y aprobación de una copia,
> probado con simulación; la conexión real espera acuerdo con Backend. Ver
> [alcance actual](21-frontend-producto.md). No se ejecuta código, se sobrescriben
> originales ni se afirma que esta ampliación esté publicada.

## Identificación

- Proyecto: CODEGUARD — Revisor Inteligente de Código Seguro.
- Caso académico: Caso 10.
- Entrega: 4.
- Producto: aplicación web para revisión asistida de código Python.

Actualización documental: 5 de noviembre de 2026, sobre `main` en `65675e2`.
Esta consolidación no sustituye evidencias originales de Semana 1. Responsables:
Ronald Yépez (QA, seguridad y documentación), Andy (Frontend y evaluación) y
Christian Gamboa (Backend, IA, agente y despliegue), confirmados por Ronald.

## Problema

La revisión manual de seguridad consume tiempo, depende de la experiencia del revisor y puede producir resultados poco trazables. Las herramientas generativas, si se usan sin controles, también pueden inventar referencias, obedecer instrucciones incluidas en el código o exponer información sensible.

## Propuesta de solución

CODEGUARD recibe código Python como texto, archivo, ZIP o repositorio público de GitHub. El backend valida la entrada, recupera documentación de seguridad desde ChromaDB y solicita a Gemini un informe estructurado. Cada hallazgo debe citar fragmentos realmente recuperados. Si no existe respaldo documental suficiente, el sistema se abstiene.

La interfaz React utiliza el agente supervisado para código pegado y `.py`: combina Ruff/Bandit, inspecciones AST y evidencia RAG en la síntesis. ZIP y GitHub conservan el flujo directo por archivo. Las alertas estáticas se muestran aparte de los hallazgos contextuales, sin asignarles citas inventadas. Agent Lab permite explorar el agente. Ningún flujo ejecuta o importa el código recibido como programa.

## Modelo elegido y justificación

La integración implementada utiliza Google Gemini mediante `google-genai`. El identificador predeterminado del código es `gemini-3.5-flash-lite`; `GEMINI_MODEL` permite sustituirlo por un modelo disponible en la cuenta. Este dato describe la configuración del repositorio, no verifica el catálogo ni las condiciones comerciales del proveedor.

Se mantiene esta integración porque ya dispone de generación estructurada, validación Pydantic, manejo de errores y pruebas acumuladas. Cambiarla durante el cierre exigiría repetir los contratos y la evaluación. No hay un estudio controlado que demuestre superioridad de coste, velocidad o precisión frente a otros modelos.

| Alternativa | Valor y limitación | Decisión técnica actual |
|---|---|---|
| Solo Ruff/Bandit | Reglas reproducibles; no proporciona por sí solo una explicación contextual fundamentada por RAG | Complemento obligatorio del agente y endpoint independiente |
| Gemini con recuperación documental | Reutiliza el adaptador probado y permite síntesis con fuentes; depende de cuota, disponibilidad y revisión humana | Implementado para el MVP |
| Otro proveedor o modelo local | Requiere adaptador, recursos y evaluación equivalente antes de asegurar compatibilidad | Fuera de esta entrega; no existe fallback Groq funcional |

La aprobación formal del equipo y la configuración exacta del despliegue se registran por separado de esta justificación técnica; ver [decisiones](09-decisiones.md).

## Objetivo general

Construir y validar una aplicación reproducible que ayude a identificar riesgos frecuentes de seguridad en código Python mediante análisis asistido por IA, con validación de entradas, citas verificables y evidencia de su comportamiento.

## Objetivos específicos

1. Validar código, archivos, proyectos ZIP y URLs antes de procesarlos.
2. Evitar la ejecución del código no confiable.
3. Proteger claves, registros y mensajes de error.
4. Fundamentar los hallazgos con documentación RAG.
5. Abstenerse ante evidencia insuficiente o referencias inválidas.
6. Probar el sistema con escenarios unitarios, de integración y producción.
7. Empaquetar frontend, backend e índice documental en un despliegue reproducible.

## Usuarios y valor esperado

- Desarrolladores: revisión inicial y explicación de posibles riesgos.
- QA y seguridad: evidencia reproducible de validaciones y regresiones.
- Docentes o evaluadores: trazabilidad entre requisitos, código, pruebas y resultados.

CODEGUARD es una herramienta de apoyo. No reemplaza una auditoría profesional ni garantiza que el código sea seguro.

## Alcance del MVP

Incluye análisis de Python, `.py`, ZIP y repositorios públicos; frontend; Gemini; RAG; citas; abstención; agente AST; Docker; volumen persistente; pruebas automatizadas y documentación.

No incluye autenticación, organizaciones, repositorios privados, ejecución aislada de código, corrección automática, almacenamiento de informes de usuarios ni escalamiento horizontal de ChromaDB embebido.

## Criterios de éxito de la Entrega 4

- Al menos 15 escenarios reproducibles contra la URL publicada.
- Regresiones para prompt injection, entradas maliciosas y errores del proveedor.
- Citas recuperadas antes y después de reiniciar el contenedor.
- Auditoría de secretos sin valores expuestos.
- README y documentación base coherentes con el producto real.
- Evidencias fechadas que distingan pruebas locales de pruebas públicas.

## Riesgos

- Consumo de cuota de Gemini: existen límites de peticiones y concurrencia por proceso, pero no autenticación ni cuotas individuales de tokens.
- Diferencias entre mocks y comportamiento real del proveedor.
- Pérdida del índice si la plataforma no monta `/data` como volumen.
- Resultados generativos variables y limitaciones de las heurísticas AST.
- Dependencia de servicios externos: Gemini, GitHub y plataforma de hosting.

## Ética, privacidad y uso responsable

No se debe enviar código confidencial sin autorización. Las evidencias no deben contener claves, código privado ni datos personales. Los hallazgos requieren revisión humana antes de modificar software real.
