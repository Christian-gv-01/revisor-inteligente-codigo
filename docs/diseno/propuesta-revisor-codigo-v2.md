# Propuesta visual: entorno de revisión de código seguro

Fecha: 30 de octubre de 2026.
Método: herramienta integrada de generación de imágenes.
Imagen: `propuesta-revisor-codigo-v2.png`.

La dirección visual responde a la corrección del usuario: priorizar el carácter técnico y académico del proyecto en lugar de la apariencia de un SaaS. El editor Python, los hallazgos, la corrección sugerida y el respaldo documental organizan toda la pantalla. La sección de trazabilidad hace visible la relación entre un hallazgo y su referencia. La imagen es un concepto visual con datos ilustrativos; sus etiquetas de etapas y trazabilidad son propuestas de interfaz.

## Prompt utilizado

+Use case: ui-mockup.
Generate ONE exceptionally polished high-fidelity design concept image for an academic software engineering project named "Revisor Inteligente de Código Seguro" (CodeGuard). IMPORTANT USER CORRECTION: the user REJECTED a generic SaaS / commercial dashboard appearance. This must feel purpose-built for inspecting Python source code and reasoning about security findings backed by retrieved documents. Design a serious, attractive, original security code analysis workbench for a university graduation project. Treat it like a thoughtfully designed developer tool crossed with an evidence-based technical report, NOT a SaaS dashboard, NOT a landing page.

Output: wide landscape desktop interface, approximately 16:10, front-on flat, crisp detailed legible Spanish typography, no laptop/device frame, no surrounding photograph, no browser chrome. Entire functional interface inside the image.

Visual direction: attractive technical clarity with restrained academic identity. Deep ink/slate top toolbar, off-white work surface, teal-green for analysis actions and source links, amber for an identified vulnerability, small thin technical dividers, precise line icons, restrained corner radii of 6–8 px, subtle grid alignment. Rich charcoal syntax-highlighted editor contrasts with the calm light reading/report column. Excellent spacing and careful typography. The working area should occupy most of the screen: no large promotional headlines or ornamental illustrations. This is a coherent dedicated tool, not floating dashboard cards. No neon hacker cliches, no padlocks sprinkled everywhere, no generic abstract blobs.

Composition:
1. Compact full-width dark top toolbar, about 72 px tall. On the left a simple shield-and-code mark and exact title "Revisor Inteligente de Código Seguro", with a small lighter secondary line "Python · Análisis asistido por IA". On the right understated academic attribution "UNIANDES" and "Proyecto de titulación". No avatar, profile, billing, subscription, business workspace, commercial logo strip, dashboard sidebar or marketing navigation.
2. Under that, a small light context strip: breadcrumb-like three phases "01  Código fuente" "02  Revisión de hallazgos" "03  Evidencia documental", with the middle phase subtly highlighted. At far right small neutral chip "Ejemplo de análisis". This is a process indicator, not three large metric cards.
3. Main workbench is two panes, left about 54% width, right 46%, with a neat vertical divider and 24 px outer margins, aligned headers. PANE LEFT header "Código Python" plus small file icon and a quiet "Cargar ejemplo" action. Under it an input switch using small rectangular text tabs "Pegar código", "Archivo .py", "Proyecto .zip". Then a light filename bar "usuarios.py" with small PYTHON badge.
Large charcoal code editor with clear monospace text, line numbers 1 through 9, syntax colors teal, lavender, warm yellow and gray. Render the following nine lines exactly, each on the corresponding numbered line, preserving the line count:
1 import sqlite3
2
3 conexion = sqlite3.connect("usuarios.db")
4 cursor = conexion.cursor()
5 nombre = input("Nombre de usuario: ")
6 consulta = "SELECT * FROM usuarios WHERE nombre = '" + nombre + "'"
7 cursor.execute(consulta)
8
9 print(cursor.fetchall())
Highlight line 6 in a translucent amber horizontal band and a small amber gutter marker; use correct line number 6 throughout. Tiny footer "9 líneas · Python · UTF-8". Below the editor a slim action bar: small text "El código se analiza sin ejecutarlo." and a clear teal primary button "Analizar código →". Do not give the editor an exaggerated rounded SaaS card border.
4. PANE RIGHT: header "Informe de revisión", with a quiet export icon/action "Exportar JSON". Below a compact readable indicator "1 hallazgo identificado" and an amber badge "Severidad alta". Then a finding report with small eyebrow "INYECCIÓN SQL" and a strong but compact title "Entrada de usuario dentro de una consulta". A precise clickable location "usuarios.py · Línea 6". A tiny annotated code extract for the highlighted line may appear if there is room, but prioritize readability.
A short section "Por qué es un riesgo" with the text "La concatenación permite que una entrada externa altere la estructura de la consulta SQL."
Next "Corrección sugerida" and a pale green monospace code block with exactly:
cursor.execute(
    "SELECT * FROM usuarios WHERE nombre = ?",
    (nombre,)
)
Use visually clear correct Python syntax; these are illustrative sample results, not live claims.
Next a compact report subsection "Respaldo documental", with a tidy document citation row and a thin teal vertical accent: "OWASP · SQL Injection Prevention", separate line "Regla 2: Consultas parametrizadas", a small monospace "seguridad_python-002" reference tag and an underlined "Consultar fuente ↗" link. Elegant readable evidence hierarchy with no run-together text.
5. Along the bottom, a slim full-width evidence drawer panel spanning both panes, integrated into the workbench. Heading "Trazabilidad del análisis". Two columns separated by a thin divider: on the left "Hallazgo" followed by "SQL · usuarios.py:6"; a small linking connector points to the right column "Fuente citada" followed by "seguridad_python-002 · OWASP". Below, a muted readable sentence "Cada hallazgo conserva su referencia documental." This visually expresses the specific RAG / citations purpose of the project, not generic analytics.
6. Final tiny footer line "Revisión asistida: valida las sugerencias en el contexto de tu proyecto." Include tiny "Concepto visual · Datos de ejemplo" to honestly identify this as a design concept.

Must feel specific to secure code review, static analysis, evidence and academic software research. All copy in Spanish. No payment or subscription language, no customer management, no business charts, no sidebar, no user avatar, no giant hero headline, no gamified security scores, no fake AI confidence percentage, no sales CTA. Keep interface labels accurate, beautiful, purposeful, readable and implementable in React. Distinctively different from a SaaS dashboard.
