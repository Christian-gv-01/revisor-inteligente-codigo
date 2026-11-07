# Cierre de agente y presupuesto: revisión de Ronald

7 de noviembre de 2026. Base `467d00e0d56a98cd758f382a5c713737eb490845`, PR #48.
Rama `docs/cierre-agente-presupuesto-ronald`, independiente del acceso del PR #50.
El commit probado y el PR de entrega identifican los ajustes de esta rama.

## Trazabilidad de lo solicitado

| Solicitud | Entrega / comprobación |
|---|---|
| Documento principal del agente | [08-agente.md](../../../08-agente.md): propósito, herramientas v2, bucle, límites, evidencia, confirmaciones, evaluación y riesgos |
| Evitar descripciones contradictorias | [17-agente-integrado.md](../../../17-agente-integrado.md) remite al 08; original archivado sin cambios |
| Presupuesto visible antes de ejecutar | Archivos, caracteres, análisis previstos, intentos máximos incluidos reintentos y plazo coinciden con respuesta del backend en cada previsualización ZIP/GitHub |
| Aprobar, rechazar y caducar | 12 escenarios aprobados en navegador, con contadores del proveedor simulado |
| Ocho historias Dado/Cuando/Entonces | Se conservan HU-01 a HU-08 y cuatro adicionales, sin reescribir requisitos correctos |
| Inventario vigente | Ocho copias HTML y seis IDs de fragmentos, concordantes con corpus/manifiesto; sin cambios en fuentes ni ingesta |
| Preparar comparación final | [Plantilla de resultados](../../../presentacion/comparacion-final-pendiente.md), guion y presentación de doce minutos; sin afirmar mejora de precisión |

## Pruebas ejecutadas

Desde la raíz, con dependencias, índice local y navegador disponibles:

```powershell
python qa/run_project_budget_browser.py --output tmp/cierre-presupuesto-20261107
```

El fixture ya existente configura únicamente procesos de prueba en loopback,
con SQLite aislado, FastAPI/RAG/Ruff/Bandit reales y Gemini/GitHub simulados. Sus
valores temporales se restauran al terminar. No se editó `.env`, no se cambiaron
flags persistentes ni se accedió a producción. Los controles para caducar
propuestas solo existen en el servidor fixture; no se añadieron a la aplicación.

Resultado: **12/12 comprobaciones de navegador aprobadas**. El script amplía las
nueve existentes con rechazo y caducidad ZIP, y bloqueo visual al vencer. En todas
las previsualizaciones verifica los valores visibles antes de aprobar. El plazo
es cooperativo, no una estimación de duración ni una cotización de coste.

- [Resultado estructurado](navegador-presupuesto.json) y [salida del runner](navegador-presupuesto.txt).
- [Presupuesto en escritorio](presupuesto-escritorio.png), [móvil](presupuesto-movil.png)
  y [ZIP caducado](presupuesto-zip-caducado.png).
- Frontend: **133 aprobadas y 24 HTTP omitidas**; ESLint aprobado. Las omitidas no
  se contabilizan como aprobadas. No cambió código de producto ni se repitió build.
- [Comprobación documental](revision-documental.json): historias, inventario y
  conservación del registro original del documento 17.
- Presentación y PDF: doce diapositivas, 720 segundos planificados; PPTX validado,
  PDF exportado con texto seleccionable y páginas revisadas. Ambos conservan
  la comparación final pendiente y las cifras históricas con su procedencia.

La aprobación inicia llamadas al proveedor simulado. Rechazar y caducar no añaden
llamadas. El navegador prueba la caducidad del servidor con HTTP 410 y la visual
con su reloj controlado. Se prueban además idempotencia, manifiesto alterado y
consentimiento invalidado al cambiar entrada. No mide consumo ni calidad de Gemini real.

La confirmación de presupuesto autoriza **analizar**. La de correcciones autoriza
**descargar una copia** tras revisar original y propuesta. No se ejecutan programas
ni se sobrescriben archivos originales. No se cambió ningún contrato.

## Alcance de la entrega

La documentación actual deja de presentar la política de prioridad del PR #48
como trabajo pendiente. La comparación real sigue a cargo de Christian. Las
métricas históricas y simuladas mantienen su procedencia; las pruebas anteriores
no se vuelven a contabilizar como nuevas. La presentación tiene tiempo planificado,
sin acreditar ensayo humano ni reparto. El presupuesto público continúa bajo
coordinación, fuera de esta validación local.
