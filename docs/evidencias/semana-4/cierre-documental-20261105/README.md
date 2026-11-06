# Validación del cierre documental

Realizada el 5 de noviembre de 2026, America/Bogota (6 de noviembre en UTC).
Base del producto: `65675e27fd996a7e71a926336dba6dffb5e539e2`.

[validacion.json](validacion.json) registra las comprobaciones automáticas y sus
límites. El verificador comprueba los Markdown nuevos/modificados respecto a la
base, existencia de enlaces relativos, codificación, cercas de código, doce
historias, dieciocho preguntas y hashes/tamaños de las ocho fuentes descargadas.
También verifica que las copias históricas mantienen el contenido original.

Reproducción desde la raíz del repositorio:

```powershell
python docs/evidencias/semana-4/cierre-documental-20261105/validar.py
git diff --check 65675e2 -- '*.md'
```

El verificador imprime su resultado. Para conservar una nueva corrida, utilizar
un archivo distinto y mantener la fecha original de esta evidencia. No ejecuta
el backend, no consulta Gemini ni Railway y no renderiza los diagramas Mermaid.
La existencia de un enlace no certifica la veracidad de su contenido.

## Comprobación visual que corrigió una conclusión previa

Se abrió [reinicio-railway-20261105.png](../reinicio-railway-20261105.png). La imagen
muestra el comando del comparador, «Continuidad de citas: True» y la ruta de su
JSON. No muestra apagado/arranque de Railway, volumen montado ni recuperación sin
reingesta. Se corrigieron README, cierre QA e índices; la imagen y los JSON
originales permanecen sin cambios. La continuidad HTTP sí está respaldada.

## Alcance de esta edición

No se añadieron entrevistas, firmas, aprobaciones ni resultados simulados como si
fueran reales. Las fuentes descargadas son documentos oficiales, no instrucciones
para el agente. No se modificó el corpus ingerido ni se desplegó la aplicación.
