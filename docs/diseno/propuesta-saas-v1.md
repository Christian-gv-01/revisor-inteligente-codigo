# Propuesta visual SaaS — CodeGuard

Fecha: 30 de octubre de 2026.
Método: herramienta integrada de generación de imágenes.
Imagen: `propuesta-saas-v1.png`.
Uso: concepto visual para decidir el rediseño del frontend. Los datos son ilustrativos; no representan una ejecución del analizador. Los detalles de código y números de línea se validarán al implementar la interfaz.

## Dirección visual

Barra lateral grafito, superficie clara, acentos esmeralda, tipografía de mayor jerarquía, editor oscuro y tarjetas de referencias legibles. Se conserva el nombre CodeGuard y el flujo de entrada de código, hallazgos, correcciones y fuentes.

## Prompt utilizado

+Use case: ui-mockup.
Create ONE exceptionally polished, high-fidelity desktop web application design concept for the existing project CODEGUARD, an AI-assisted Python security code reviewer. The user wants a striking, elegant, credible SaaS interface they can later implement in React. This is a design proposal, not a photograph. Landscape 16:10 composition, straight-on flat interface, crisp typography and pixel-perfect spacing, full application viewport, no laptop frame, no perspective, no external mockup background.

Visual direction: sophisticated developer SaaS with an editorial feel. Warm near-white main canvas, a deep graphite/navy sidebar, refined emerald accent drawn from the existing project, delicate gray-green hairline borders, restrained shadows, generous negative space, small precise outline icons. Beautiful professional sans-serif with a strong typographic hierarchy; tasteful monospace in the code editor. Selectively use subtle tonal gradients ONLY on the small brand symbol or the primary button; avoid excessive gradients. Calm, premium, clean, memorable, realistic and implementable. Do not make a generic admin dashboard full of charts and metrics. The working code and cited evidence are the focus.

Layout:
A slim, carefully proportioned left sidebar, about 210 px wide, full height. At the top the existing brand "CODEGUARD" with a small shield-and-code-brackets mark, and tiny subtitle "REVISOR DE CÓDIGO SEGURO". Navigation section label "ESPACIO DE TRABAJO". Active navigation "Analizador" in an emerald tinted selection; other navigation items "Historial", "Evaluación", "Fuentes". Bottom a quiet workspace card "Proyecto de grado" and "UNIANDES", with a small profile/settings area.
The main area has a thin topbar with breadcrumb "Espacio de trabajo / Analizador"; on the right a subtle "Modo demostración" pill and a small round CG avatar.
Below, a spacious but compact editorial heading with small eyebrow "SEGURIDAD CON EVIDENCIA", the large headline "Revisa tu código.
Comprende cada riesgo." in dark graphite, and supporting text "Analiza Python y consulta las fuentes detrás de cada hallazgo." To the right, an understated secondary action "Exportar informe". No oversized decorative illustrations.
Below the heading, a compact inline result summary with colored dots and readable labels "1 hallazgo", "Alta", "2 fuentes consultadas"; these describe a single illustrative result and should not look like a cluttered row of large statistic cards.
The primary workspace is two balanced panels, left slightly wider than right, aligned at their upper edges:
LEFT PANEL: white panel with rounded 14px corners, a neat header with small green code icon and label "Código fuente". Input type segmented tabs "Código", "Archivo .py", "Proyecto .zip" and a visually muted "GitHub" with a tiny "Próximamente" note. A filename row "ejemplo.py" and a small "PYTHON" tag. Large rich dark graphite code editor with syntax highlighting, line numbers, subtle indentation guides and one restrained amber line highlight. Show a plausible short Python SQLite example with import sqlite3, nombre = input("Nombre: "), conexion = sqlite3.connect("usuarios.db"), cursor = conexion.cursor(), consulta = "SELECT * FROM usuarios WHERE nombre = '" + nombre + "'", cursor.execute(consulta), print(cursor.fetchall()). Keep clear code legibility; use comfortably spaced lines. Highlight the SQL concatenation line. Editor footer "Python · UTF-8". Under the editor: a small green check "Análisis completado" on the left and a handsome emerald primary button "Analizar código" with right arrow on the right.
RIGHT PANEL: white panel "Resultados del análisis" with subtle "1" count badge and severity filter "Todas las severidades". A well-designed finding displays small amber pill "Alta", subdued category "Inyección SQL", bold title "Consulta SQL sin parametrizar", a small file and line link "ejemplo.py · Línea 5", and a short explanation "La entrada del usuario puede modificar la estructura de la consulta." Then a light sage code snippet under "Corrección sugerida": cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre,)).
Under the finding, clearly distinguish the section "Fuente citada" with a beautifully composed citation card: tiny document icon, bold title "OWASP SQL Injection Prevention", separate secondary line "Regla 2 · Consultas parametrizadas", subtle monospace identifier "seguridad_python-002", and an accessible emerald "Consultar fuente ↗" link. This card must have ample spacing so none of the title, section, ID or link run together. At the bottom a compact collapsible row "Ver las 2 fuentes consultadas". Include a small muted note "Las fuentes consultadas se vinculan por hallazgo." Everything aligns meticulously.

Make the interface visually compelling through typography, composition, proportion, clear content, premium whitespace and precise details, not visual clutter. All user-facing interface text must be Spanish, proofread and highly readable, retain CODEGUARD brand spelling. No English marketing copy, no fake graphs, no extraneous pricing, no billing, no exaggerated security guarantees, no neon hacker motifs, no stock photos, no watermark. This is a proposed SaaS design for an academic software project.
