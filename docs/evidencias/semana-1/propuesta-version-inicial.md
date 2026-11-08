# Primera versión localizada de la propuesta

Proyecto: CODEGUARD
Commit: 74817d5
Fecha registrada en Git: 2026-11-04

IMPORTANTE:
Esta es la primera versión localizada del archivo
docs/01-propuesta.md en el historial consultado.
No corresponde a una propuesta acreditada de la primera semana.

# 01. Propuesta del proyecto

## Identificaci├│n

- Proyecto: CODEGUARD ÔÇö Revisor Inteligente de C├│digo Seguro.
- Caso acad├®mico: Caso 10.
- Entrega: 4.
- Producto: aplicaci├│n web para revisi├│n asistida de c├│digo Python.

## Problema

La revisi├│n manual de seguridad consume tiempo, depende de la experiencia del revisor y puede producir resultados poco trazables. Las herramientas generativas, si se usan sin controles, tambi├®n pueden inventar referencias, obedecer instrucciones incluidas en el c├│digo o exponer informaci├│n sensible.

## Propuesta de soluci├│n

CODEGUARD recibe c├│digo Python como texto, archivo, ZIP o repositorio p├║blico de GitHub. El backend valida la entrada, recupera documentaci├│n de seguridad desde ChromaDB y solicita a Gemini un informe estructurado. Cada hallazgo debe citar fragmentos realmente recuperados. Si no existe respaldo documental suficiente, el sistema se abstiene.

El sistema incorpora una interfaz React y un Agent Lab limitado a herramientas AST de solo lectura. Ning├║n flujo ejecuta o importa el c├│digo recibido.

## Objetivo general

Construir y validar una aplicaci├│n reproducible que ayude a identificar riesgos frecuentes de seguridad en c├│digo Python mediante an├ílisis asistido por IA, con validaci├│n de entradas, citas verificables y evidencia de su comportamiento.

## Objetivos espec├¡ficos

1. Validar c├│digo, archivos, proyectos ZIP y URLs antes de procesarlos.
2. Evitar la ejecuci├│n del c├│digo no confiable.
3. Proteger claves, registros y mensajes de error.
4. Fundamentar los hallazgos con documentaci├│n RAG.
5. Abstenerse ante evidencia insuficiente o referencias inv├ílidas.
6. Probar el sistema con escenarios unitarios, de integraci├│n y producci├│n.
7. Empaquetar frontend, backend e ├¡ndice documental en un despliegue reproducible.

## Usuarios y valor esperado

- Desarrolladores: revisi├│n inicial y explicaci├│n de posibles riesgos.
- QA y seguridad: evidencia reproducible de validaciones y regresiones.
- Docentes o evaluadores: trazabilidad entre requisitos, c├│digo, pruebas y resultados.

CODEGUARD es una herramienta de apoyo. No reemplaza una auditor├¡a profesional ni garantiza que el c├│digo sea seguro.

## Alcance del MVP

Incluye an├ílisis de Python, `.py`, ZIP y repositorios p├║blicos; frontend; Gemini; RAG; citas; abstenci├│n; agente AST; Docker; volumen persistente; pruebas automatizadas y documentaci├│n.

No incluye autenticaci├│n, organizaciones, repositorios privados, ejecuci├│n aislada de c├│digo, correcci├│n autom├ítica, almacenamiento de informes de usuarios ni escalamiento horizontal de ChromaDB embebido.

## Criterios de ├®xito de la Entrega 4

- Al menos 15 escenarios reproducibles contra la URL publicada.
- Regresiones para prompt injection, entradas maliciosas y errores del proveedor.
- Citas recuperadas antes y despu├®s de reiniciar el contenedor.
- Auditor├¡a de secretos sin valores expuestos.
- README y documentaci├│n base coherentes con el producto real.
- Evidencias fechadas que distingan pruebas locales de pruebas p├║blicas.

## Riesgos

- Consumo de cuota de Gemini en una URL p├║blica sin rate limiting.
- Diferencias entre mocks y comportamiento real del proveedor.
- P├®rdida del ├¡ndice si la plataforma no monta `/data` como volumen.
- Resultados generativos variables y limitaciones de las heur├¡sticas AST.
- Dependencia de servicios externos: Gemini, GitHub y plataforma de hosting.

## ├ëtica, privacidad y uso responsable

No se debe enviar c├│digo confidencial sin autorizaci├│n. Las evidencias no deben contener claves, c├│digo privado ni datos personales. Los hallazgos requieren revisi├│n humana antes de modificar software real.
