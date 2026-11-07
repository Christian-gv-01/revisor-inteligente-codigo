# Paquete candidato e instalación pendiente

El PR 37 ya se integró en `2888dea8740e2ef0331e2edafeeff2d9a0bfccb8`.
La revisión inicial localizó un PowerPoint de doce minutos bajo `docs/presentacion/`,
todavía sin PDF y con frases anteriores a la integración. La actualización de Ronald
incorpora los resultados del PR 37 al [PowerPoint y guion](presentacion/README.md),
y añade el [PDF de doce minutos](presentacion/CODEGUARD-12-minutos.pdf).
El paquete debe regenerarse desde un commit que incluya esta actualización.

## Paquete reproducible

Desde un checkout real, con Git y Python disponibles:

```sh
python scripts/empaquetar_entrega.py --ref HEAD --output dist/entrega/CODEGUARD_Semana4.zip
```

El script lee los objetos Git de la revisión resuelta, sin copiar el `.env`,
dependencias ni cambios del directorio de trabajo. Si Git contiene un entorno,
caché, base de datos, ZIP previo, clave privada, enlace simbólico o submódulo,
bloquea la construcción. No elimina archivos versionados silenciosamente.

El paquete contiene el repositorio y dos archivos generados: un manifiesto con
revisión, blobs, tamaños y hashes, y un estado que identifica pendientes. Se
verifican los bytes de todas las entradas, CRC y tamaño inferior o igual a
20.000.000 bytes. El reporte externo incluye el hash del ZIP.

El workflow de paquete crea el artefacto `CODEGUARD-Semana4-candidato`, disponible
para descargar en su corrida de Actions. Es un candidato para revisión: el manifiesto
indica si el commit empaquetado incluye el PDF. El ZIP anterior no lo contiene.
La presencia del PDF no resuelve los demás puntos del cierre documental ni acredita
la instalación humana cronometrada.
Las pruebas de empaquetado no certifican ausencia de secretos; el escaneo
Gitleaks del repositorio constituye una verificación independiente.

## Instalación cronometrada: evidencia humana necesaria

Preparación actual desde `384ffaf`: [checkout limpio, requisitos y medición](30-instalacion-checkout-limpio.md).
Es una prueba automatizada en equipo existente, no el ensayo humano independiente.

Debe probarla un integrante que no haya preparado ese entorno. Un directorio
nuevo sobre una instalación existente no equivale necesariamente a un equipo
limpio: registrar Git, Python, Node, cachés y dependencias ya presentes.

1. Anotar nombre del integrante, equipo/sistema, revisión Git y hora inicial.
2. Clonar la revisión acordada o descomprimir el ZIP verificado en otra carpeta.
3. Seguir los comandos del README, creando un entorno Python nuevo e instalando
   las dependencias del backend y `npm ci` en frontend.
4. Completar las variables privadas localmente; no pegarlas en evidencias ni chat.
5. Preparar el índice siguiendo el README e iniciar backend y frontend.
6. Comprobar `/health`, carga de interfaz y un análisis. Indicar si el proveedor
   fue real o simulado y si solo se comprobó el modo demo.
7. Anotar hora final, minutos, errores y pasos adicionales. El objetivo de diez
   minutos solo se marca como cumplido si lo demuestra esa ejecución.

No se aporta un tiempo inventado ni se presenta el entorno de CI como una prueba
humana de instalación. Las correcciones siguen deshabilitadas por defecto en el
frontend público; este trabajo de empaquetado no activa esa función ni despliega.
