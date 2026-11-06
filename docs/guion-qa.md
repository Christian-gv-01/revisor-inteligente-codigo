# Guion de Ronald Yépez — QA, seguridad y documentación

Duración orientativa: tres minutos dentro de la presentación grupal. Basado en
la evidencia consolidada el 5 de noviembre de 2026; no sustituye el PDF de Andy.

## Intervención

«Mi responsabilidad en CODEGUARD es QA, seguridad y documentación. Mi trabajo
consiste en comprobar que el comportamiento de la aplicación corresponda con
los requisitos y que cada resultado que presentamos tenga evidencia.

CODEGUARD ayuda a revisar código Python. Combina herramientas estáticas como
Ruff y Bandit con un análisis de Gemini apoyado en documentación recuperada.
Estas dos clases de resultados se muestran por separado: una regla estática no
se convierte automáticamente en un hallazgo con fuentes OWASP o MITRE.

Desde QA revisé entradas válidas e inválidas, archivos Python, ZIP, URLs GitHub y
límites de tamaño. La matriz pública documentada obtuvo 26 de 26 escenarios
aprobados. Ese resultado corresponde a los escenarios y a la versión de la
ejecución; no significa que el producto esté libre de vulnerabilidades.

También revisamos el tratamiento de errores y resultados parciales. Si Gemini
falla y ya hay resultados estáticos, la aplicación puede conservarlos indicando
que el análisis está incompleto. Es importante no mostrar “sin hallazgos” como si
fuera una garantía de seguridad.

En persistencia, el equipo conservó dos análisis que mantuvieron las mismas tres
fuentes. La comparación respalda esa continuidad. Al revisar la captura detecté
que mostraba el comparador y no el log de Railway, por lo que dejé pendiente la
evidencia independiente del reinicio y del volumen.

En documentación consolidé la propuesta, los requisitos, doce historias de
usuario, la arquitectura actual y el inventario de fuentes. Además, organicé
las evidencias y diferencié pruebas simuladas de ejecuciones reales. Los
documentos históricos se conservan para mostrar cómo evolucionó el proyecto.

El mayor reto fue integrar componentes que avanzaban en ramas diferentes y
verificar que interfaz, API y documentación describieran el mismo comportamiento.
Mi aporte es que el equipo pueda explicar qué está comprobado, con qué evidencia
y cuáles son todavía sus límites.»

## Si preguntan por pendientes

«El cierre documental identifica los respaldos originales de Semana 1 que aún no
se han aportado, la conclusión de una observación histórica de secretos y las
validaciones finales del equipo. No presentamos una plantilla como entrevista
real ni una prueba simulada como evidencia de precisión de Gemini.»

## Si preguntan qué fue lo más difícil

«Lo más difícil fue garantizar coherencia entre lo implementado, lo probado y lo
documentado, especialmente cuando Gemini falla o el informe es parcial. Resolverlo
exigió separar fuentes, estados y tipos de evidencia, además de coordinar ramas
y revisiones entre los tres integrantes.»

## Evidencias que conviene tener abiertas

- [Matriz de pruebas](08-pruebas.md) y [ejecución pública propia](15-verificacion-publica-integrada.md).
- [Arquitectura](03-arquitectura.md) para explicar las modalidades.
- [Cierre QA](12-cierre-qa-entrega4.md) para citas y reinicio.
- [Aportes](11-aportes-ia.md) y [pendientes reales](19-cierre-documental.md).
