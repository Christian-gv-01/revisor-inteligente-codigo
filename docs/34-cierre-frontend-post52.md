# Integración de acceso y documentación sobre el PR #52

Base de código: `4f41ebf64160edfac078a0028cfb727c2cc7fb95`, fusión del PR #52.
Este candidato reúne tres entregas pendientes sin cambiar producción:

| Entrega | Referencia conservada | Contenido |
|---|---|---|
| PR #50 | `09c09f5ab8c00c79a277ec4aa338279b3967f988` | Acceso visible al laboratorio y proxy local `/agente` |
| PR #51 | `47e9b526d8619318f28a5f77ee7853e043d5a750` | Documento 08 principal, presupuesto probado y preparación de presentación/PDF |
| PR #49 | `50c5702488527e2e36b413587a9834c3d737f6b6` | Evidencia histórica de 26/26 pruebas públicas sobre `467d00e` |

La evidencia de 26/26 conserva su revisión original; no se presenta como una
nueva corrida de esta combinación. Los PNG, PPTX y PDF de Ronald se conservan
por sus blobs Git originales. No se reexportaron ni se efectuó aquí una nueva
revisión visual independiente de esos binarios.

## Ajustes de integración

- Se combinan los enlaces aportados por #50 y #51 en el índice documental.
- `08-agente.md` refleja máximo de cuatro pasos en v2, radio de contexto seis,
  deserialización, conservación del cuarto resultado y telemetría de consumo.
- Se distingue la ordenación ya integrada de la severidad derivada y su herencia,
  que siguen pendientes del compañero de backend según el documento docente.
- El guion y las notas de presentación indican que el PDF/PPTX preparado requiere
  una actualización final. Sus métricas históricas permanecen etiquetadas.
- El recorrido de navegador incorpora acceso desde React por el proxy Vite, sin
  POST al abrir, conservación de modo y AST local sin llamadas al proveedor. Se
  ejecuta junto con los casos del agente v2, incluyendo sus cuatro pasos.

El revisor React sigue solicitando explícitamente tres pasos. El contrato v2 y
el laboratorio permiten cuatro, y el evaluador final solicita cuatro por defecto.
No se cambian contratos de presupuesto, flags ni límites de intentos o tiempo.

## Validación local

- 604 pruebas Python aprobadas, incluyendo backend, QA y evaluadores.
- 135 pruebas frontend aprobadas; 24 HTTP omitidas en la suite unitaria, sin
  contarlas como aprobadas.
- Lint y compilación correctos; persiste la advertencia previa de bundle grande.
- No se dispone de Chromium local. Las pruebas de navegador de la combinación
  quedan al CI del candidato; no se trasladan los resultados de ramas anteriores
  como si fueran una ejecución nueva.
- Dos lecturas públicas, salud y OpenAPI, respondieron 200 y el esquema anunció
  `max_pasos.maximum=4` y versiones 1/2. No se enviaron análisis ni se llamó a Gemini.
  `/health` solo informa `0.1.0`: esas lecturas no atestiguan el SHA activo.

## Cierre todavía pendiente

Primero debe incorporarse la política de severidad derivada y herencia, resolver
cualquier diferencia de contrato y congelar una única versión. Después verificar
el corpus/configuración efectivos y ejecutar las cuarenta solicitudes reales y
los seis pares del planificador, conservando fallos, parciales y consumo desconocido.

Finalmente actualizar presentación/PDF, revisar las citas, completar instalación
independiente y ensayo humano, y generar el ZIP de hasta 20 MB sin secretos ni
cachés. Esta integración no acredita por sí sola mejora de precisión, consumo
real de Gemini, activación pública del presupuesto ni entrega académica completa.
