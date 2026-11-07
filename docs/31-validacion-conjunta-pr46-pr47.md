# Candidato conjunto: frontend/documentación y severidad × confianza

Validación automatizada asistida para Christian. No acredita instalación humana,
ensayo oral, evaluación Gemini real ni versión activa en Railway.

## Entradas inmutables

- Main de partida: `384ffafba3b10886751260c15a944e2b24f110ab`.
- Frontend/documentación PR #46: `403ee68f06116ea41cad30ce6408af33b7999906`.
- Backend/prioridad PR #47: `0863d494868d45de7bec8c151743f630c4b4b23f`.

Ambos PR parten de la misma base y no modifican archivos en común. El candidato
conserva ambos commits como ancestros; incorpora los blobs completos de cada
propuesta, incluidos PDF, presentación y evidencias históricas del PR #46. La
revisión de comportamiento no constituye una revisión final de esas diapositivas.

## Comportamiento contrastado

- Bandit usa exclusivamente su `issue_confidence`; los valores ausentes o
  desconocidos permanecen `None`. No se asigna su confianza a los hallazgos de IA.
- Se conservan severidad original, dominancia de severidad, factores 8/4/2/1 y
  1.0/0.8/0.6, desconocidos detrás dentro de la misma severidad y empates estables.
- La corrección frontend del PR #46 presenta «Solicitud no completada» para un
  presupuesto caducado; mantiene el detalle y evita anunciar integración pendiente.
- No se activan flags, no se cambia configuración pública ni se modifica Railway.

Se añade una regresión entre componentes, no una nueva funcionalidad de producto:

1. `qa/fixture_prioridad_integrada.py` obtiene la respuesta del endpoint real
   `/api/v1/analizar`, sustituyendo las salidas de Ruff/Bandit y el proveedor.
   El fallo 503 del proveedor es sintético y verifica el informe parcial estático.
2. `backend/tests/test_prioridad_contrato_frontend.py` compara lo regenerado con
   el fixture versionado; detecta que API y frontend no estén usando lo mismo.
3. `frontend/tests/priority-integration.test.tsx` consume esa respuesta a través
   del parser real, el panel real y el exportador. Comprueba orden, estabilidad,
   severidad dominante, confianza ausente y conservación de estado parcial.

El fixture es sintético y no demuestra precisión de Bandit ni Gemini.

## Validación local

Entorno Linux, Python 3.12.14, Node 24.22.1. Es diferente del Python 3.13/Node 22
de CI; no se presenta como instalación independiente ni reproducción de Railway.
Los bytes de código se contrastaron con los blobs Git de entrada y se normalizó
un salto LF adicional introducido al materializar algunos archivos. Las suites
se ejecutaron después sobre esos bytes, conservando aparte el fixture añadido.

| Comprobación | Resultado observado |
|---|---|
| Backend | 510 aprobadas: 509 de la propuesta más la nueva regresión API/fixture |
| QA/evaluador | 64 aprobadas: 14 QA, 40 comparador y 10 evaluador base |
| Total Python del comando conjunto | 574 aprobadas |
| Frontend unitario | 133 aprobadas; 24 HTTP omitidas en esa suite aislada |
| ESLint y build | Aprobados; permanece advertencia previa de tamaño del bundle |
| HTTP con estático | 24/24 aprobadas |
| HTTP sin estático | 19/19 aplicables aprobadas; cinco requieren estático |

Las dos integraciones HTTP emplean FastAPI, RAG/ChromaDB y, cuando corresponde,
Ruff/Bandit reales. Gemini y transporte GitHub están simulados; cero llamadas IA
externas. El fixture específico de prioridad sustituye también los analizadores,
como indica su propio metadato. No mezclar estas dos clases de comprobación.

Comandos desde raíz:

```sh
python -m pytest backend/tests qa eval/test_comparar_rutas.py eval/test_contrato_agente_evaluacion.py eval/test_run_eval.py -q
python eval/run_integration.py --static-analysis --output tmp/conjunto-http-estatico-git-lf
python eval/run_integration.py --output tmp/conjunto-http-sin-estatico
```

Desde frontend: `npm test`, `npm run lint`, `npm run build`. Usar el entorno con
las dependencias instaladas. Los resultados HTTP locales quedan en las carpetas
indicadas; el CI genera y adjunta sus propios JSON, logs y capturas.

El navegador local sigue sin Chromium disponible. Los runners de presupuesto y
agente v2 se ejecutan en CI; confirmar sus estados y los artefactos antes de
considerar terminada la revisión visual del candidato.

## Lo que sigue pendiente

- Revisar el candidato y sus verificaciones, y acordar la integración en main.
- Identificar el SHA realmente desplegado y la configuración efectiva, no inferir
  despliegue de una fusión ni del esquema OpenAPI.
- Congelar una versión y ejecutar los mismos veinte casos por ambas rutas con
  Gemini real; conservar errores/parciales y revisar pertinencia de las citas.
- Decidir la activación coordinada de presupuesto y correcciones en la interfaz.
- Instalación por otro integrante, ensayo humano cronometrado y revisión final
  de PDF/presentación con las métricas definitivas; regenerar después el paquete.

Las observaciones «pendiente» de los documentos de Ronald conservan la referencia
histórica que él revisó. Este registro identifica qué se incorporó al candidato;
no convierte el material histórico en evidencias de evaluación real ni cierra
por sí solo la entrega académica.
