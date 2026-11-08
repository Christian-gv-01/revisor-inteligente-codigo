# Primera versión localizada de la propuesta — procedencia

**Proyecto:** CODEGUARD.  
**Commit de procedencia:** [`74817d5`](https://github.com/Christian-gv-01/revisor-inteligente-codigo/commit/74817d5a570eedde32089b8ce5acf59c6fe06aa0).  
**Fecha de ese commit:** 4 de noviembre de 2026.  
**Alcance:** primera versión localizada de `docs/01-propuesta.md` en el historial examinado. **No** acredita propuesta redactada durante Semana 1. El texto se conserva desde el objeto Git original, sin atribuirle fecha anterior.

---

# 01. Propuesta del proyecto

## Identificación

- Proyecto: CODEGUARD — Revisor Inteligente de Código Seguro.
- Caso académico: Caso 10.
- Entrega: 4.
- Producto: aplicación web para revisión asistida de código Python.

## Problema

La revisión manual de seguridad consume tiempo, depende de la experiencia del revisor y puede producir resultados poco trazables. Las herramientas generativas, si se usan sin controles, también pueden inventar referencias, obedecer instrucciones incluidas en el código o exponer información sensible.

## Propuesta de solución

CODEGUARD recibe código Python como texto, archivo, ZIP o repositorio público de GitHub. El backend valida la entrada, recupera documentación de seguridad desde ChromaDB y solicita a Gemini un informe estructurado. Cada hallazgo debe citar fragmentos realmente recuperados. Si no existe respaldo documental suficiente, el sistema se abstiene.

El sistema incorpora una interfaz React y un Agent Lab limitado a herramientas AST de solo lectura. Ningún flujo ejecuta o importa el código recibido.

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

- Consumo de cuota de Gemini en una URL pública sin rate limiting.
- Diferencias entre mocks y comportamiento real del proveedor.
- Pérdida del índice si la plataforma no monta `/data` como volumen.
- Resultados generativos variables y limitaciones de las heurísticas AST.
- Dependencia de servicios externos: Gemini, GitHub y plataforma de hosting.

## Ética, privacidad y uso responsable

No se debe enviar código confidencial sin autorización. Las evidencias no deben contener claves, código privado ni datos personales. Los hallazgos requieren revisión humana antes de modificar software real.
