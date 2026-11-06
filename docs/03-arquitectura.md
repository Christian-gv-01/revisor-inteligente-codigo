# 03. Arquitectura vigente de CODEGUARD

Revisión documental: 5 de noviembre de 2026. Base: `main`, `65675e2` (PR #31).
La [arquitectura de revisión 2](historico/03-arquitectura-revision2.md) se conserva
como registro histórico. La revisión Git no identifica por sí sola la versión
que Railway tiene desplegada.

## Contexto — C4 nivel 1

```mermaid
flowchart LR
    U[Desarrollador o evaluador] -->|Código o proyecto público| C[CODEGUARD]
    C -->|Informe, fuentes, traza y JSON| U
    C -->|Código y contexto| G[Google Gemini]
    C -->|Descarga acotada| H[GitHub API]
    F[MITRE y OWASP] -->|Curación documental previa| C
```

Las páginas oficiales son referencias del conocimiento curado. El agente no
realiza navegación web libre ni admite URLs de documentación generadas por el
código recibido.

## Componentes — C4 nivel 2

```mermaid
flowchart TB
    B[Navegador: React, TypeScript y Monaco]
    B -->|HTTPS, mismo origen, /api/v1| API
    subgraph R[Contenedor CODEGUARD en Railway]
        API[FastAPI: validación, límites y errores seguros]
        UI[Frontend compilado servido en /]
        A[Coordinador del agente: código y .py]
        D[Coordinador directo: ZIP y GitHub]
        T[Herramientas AST de solo lectura]
        S[Ruff y Bandit]
        L[Adaptador Gemini y validación del informe]
        V[ChromaDB embebido]
        API --> UI
        API --> A
        API --> D
        API -->|Endpoint estático independiente| S
        A --> T
        A --> S
        A -->|Evidencia tipada| L
        D -->|Estático opcional| S
        D --> L
        L -->|Recuperación documental| V
    end
    L -->|API del proveedor| G[Gemini]
    D -->|HTTPS acotado| GH[api.github.com]
    V --> P[Volumen /data/chroma]
    K[knowledge/seguridad_python.md] --> I[scripts/ingest.py]
    I --> V
    F[Enlaces oficiales MITRE y OWASP] -->|Resumen revisado| K
```

React se compila al construir la imagen; Node no es un servidor adicional en
producción. FastAPI sirve frontend y API. `VITE_API_BASE_URL` puede quedar vacío
para utilizar rutas relativas. Agent Lab está en `/agente/demo`.

## Flujo de una consulta del agente

```mermaid
sequenceDiagram
    actor U as Usuario
    participant UI as React
    participant API as FastAPI
    participant A as Agente
    participant T as Ruff/Bandit y AST
    participant R as ChromaDB
    participant G as Gemini
    U->>UI: Código o .py, modo API
    UI->>API: POST /api/v1/agente/analizar
    API->>API: Validar entrada y aplicar controles
    API->>A: Solicitud validada
    A->>T: Estático una vez y AST inicial
    T-->>A: Resultados y estados reales
    loop Hasta dos inspecciones adicionales o finalizar antes
        A->>G: Elegir herramienta permitida
        G-->>A: Decisión estructurada
        A->>T: Inspección si corresponde
        T-->>A: Evidencia acotada
    end
    A->>R: Consultas por categorías
    R-->>A: Hasta seis fuentes únicas
    A->>G: Síntesis con código, evidencia y contexto
    G-->>A: Informe estructurado
    A->>A: Validar citas, fragmento y ubicación
    A-->>API: Informe, estático y traza
    API-->>UI: Respuesta tipada
    UI-->>U: Paneles separados y exportación
```

El diagrama describe el recorrido exitoso. Un fallo del proveedor puede conservar
evidencia local y devolver estado parcial; no implica que todas las etapas se
hayan ejecutado. Las trazas identifican decisiones realmente realizadas.

## Modalidades y límites de confianza

| Modalidad | Flujo actual | Respaldo y citas |
|---|---|---|
| Código / `.py` desde React en API | Agente integrado | Estático obligatorio, AST y síntesis con hasta seis fuentes |
| `/analizar` y `/archivos` directos | Compatibilidad del análisis directo | Estático según `STATIC_ANALYSIS_ENABLED`; límite tres para recuperación de seguridad |
| ZIP / GitHub | Directo por archivo | Citas aisladas por informe; límites de entrada y corte del proveedor tras fallo parcial |
| `/estatico/analizar` | Ruff/Bandit sin Gemini | Reglas y documentación de cada herramienta, sin citas RAG inventadas |
| `/agente/previsualizar` | AST sin Gemini | Inspección sintáctica, no generación |
| Demo React | Respuestas ilustrativas locales | No acredita análisis del proveedor ni recuperación documental |

Entradas, documentos y resultados de herramientas son datos no confiables,
serializados aparte de las instrucciones. La lista de herramientas es cerrada;
el modelo no ejecuta órdenes arbitrarias. Ruff/Bandit leen texto para analizarlo,
sin ejecutar ni importar el programa recibido.

Un ID válido y una coincidencia literal no prueban pertinencia semántica ni
explotabilidad. El agente descarta hallazgos inválidos individualmente y conserva
los válidos con estado parcial; el flujo directo conserva su validación global
de referencias.

## Datos y despliegue

- Fuente curada: seis reglas en `knowledge/seguridad_python.md`. Ver
  [inventario](04-fuentes.md) y enlaces de origen en `data/raw/`.
- Colección obligatoria: `seguridad_python`. `contexto_proyecto` es complementaria
  y no sustituye las fuentes de seguridad.
- Docker/Railway: `CHROMA_PATH=/data/chroma`, volumen en `/data`. El arranque
  recupera un índice no vacío o realiza ingesta inicial si hace falta.
- Imagen: build frontend Node 22 y ejecución Python 3.13. El entrypoint prepara
  permisos del volumen y la aplicación se ejecuta como UID 10001.
- API key solo en backend. No utilizar variables `VITE_*` para secretos.
- Un proceso y una réplica para ChromaDB embebido y límites en memoria. No se
  afirma alta disponibilidad ni recuperación de backups probada.
- No hay historial persistente de informes de usuarios. El código se procesa
  en memoria/temporales y se envía al proveedor en modo API; esto no acredita
  ausencia de retención por servicios externos.

## Evidencia y alcance

La validación local está en [17-agente-integrado.md](17-agente-integrado.md).
La comparación de citas y la falta del log independiente se explican en
[cierre QA](12-cierre-qa-entrega4.md). Una corrida pública previa no valida
automáticamente una versión posterior del agente.

Contratos: [RAG](06-rag.md), [estático](10-analisis-estatico.md),
[resiliencia](11-resiliencia-gemini.md) y [despliegue](despliegue.md).
