# Herramientas contextuales v2 — evidencia del 6 de noviembre de 2026

Base exacta: `605d142ff8f643d755689e257c649e0a9e79a8ea`. Sus seis workflows
terminaron aprobados antes de publicar este bloque: backend
[42303489443](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/42303489443),
HTTP [42303489327](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/42303489327),
frontend 42303489351, Docker 42303489741, secretos 42303489371 y captura
estática Windows/Linux 42303489578.

## Verificaciones locales

| Comprobación | Resultado |
|---|---|
| Backend `python -m pytest tests -q` | 476 aprobadas; [JUnit](backend-junit.xml) |
| QA/eval `python -m pytest qa eval -q` | 23 aprobadas, una omitida: Windows no permite crear enlaces simbólicos; [JUnit](qa-eval-junit.xml) |
| `node qa/check_agent_lab_ui.cjs` | Aprobado |
| Frontend `npm test` | 91 aprobadas, 24 requieren integración y se omiten en ejecución aislada |
| Frontend `npm run lint` / `npm run build` | Aprobados; advertencia habitual de bundle mayor de 500 kB |
| Integración HTTP con Ruff/Bandit reales | [Aprobada](http-estatico.json): 24 pruebas frontend HTTP, RAG ChromaDB real |
| Integración HTTP sin análisis estático | [Aprobada](http-sin-estatico.json): 19 aprobadas y cinco omitidas por requerir análisis estático |
| Contrato JSON reproducible | Incluido en las 476 pruebas: regenera y compara los diez ejemplos |
| `git diff --check` | Aprobado |

Los proveedores IA y GitHub están simulados en integración. Cero llamadas IA
externas; estos resultados verifican contratos y regresiones, no calidad de Gemini.
El evaluador HTTP existente sigue usando v1. La cobertura nueva v2 está en las
pruebas de backend y los ejemplos FastAPI reproducibles; no se modificó el evaluador.

## Cobertura nueva y revisión

Se probaron argumentos estrictos, extras/URLs rechazados, categorías cerradas,
líneas inexistentes, ventanas y documentos acotados, procedencia e IDs exactos,
fallos de RAG, trazas, deduplicación por argumentos, finalización anticipada,
resultados en la siguiente decisión y síntesis y citas reutilizadas. Se verificó
que herramientas locales no agregan llamadas Gemini ni eluden el plazo total.
Se mantienen tres pasos, dos decisiones, una síntesis, nueve intentos máximos
y plazo cooperativo de 150 segundos del PR #42.

Revisión independiente general: sin bloqueos. La revisión del recuperador detectó
que `area` no debía prevalecer sobre la procedencia autoritativa RAG. Corregido
y cubierto con 21 casos adicionales: se rechazan fuentes de proyecto, valores
desconocidos o procedencias contradictorias. Revisión posterior aprobada.

Frontend, evaluador, priorización y módulos de presupuesto permanecen sin cambios
respecto de la base. Las herramientas se habilitan con `version_herramientas: "2"`;
por defecto se conserva v1. [Contrato y ejemplos](../../../contrato-agente-v2/README.md).

El auditor local de secretos no detectó valores en los archivos actuales. Señaló
un patrón JWT en el historial ya presente en la base; no imprime valores. La
verificación Gitleaks de CI se comprueba por separado en el PR.

Entrega en borrador para revisión; sin integración ni despliegue.
