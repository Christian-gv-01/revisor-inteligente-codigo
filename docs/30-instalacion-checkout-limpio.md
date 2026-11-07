# Instalación desde checkout limpio y preparación del ensayo

Fecha: 6 de noviembre de 2026. Responsable documental: Ronald Yépez.
Referencia acordada: `384ffafba3b10886751260c15a944e2b24f110ab` (PR #41 integrado).
Se conserva la rama `docs/frontend-agente-v2-presupuesto` y los commits entregados.
La sincronización se hizo mediante merge `5b72b553da950697949356b6914b8c16056e8e70`,
sin conflictos, sin rebase ni modificaciones directas de `main`.

## Alcance de la preparación

La prueba automatizada usa otro worktree limpio del commit exacto, crea `.venv`
y `frontend/node_modules` desde cero e ingiere el corpus en un índice nuevo.
El equipo Windows, Git, Python, Node y las cachés ya existían. No se borraron
cachés ni se reutilizaron los paquetes de otro virtualenv.

**No equivale a la instalación humana independiente exigida en la guía de cierre.**
La [evidencia de preparación](evidencias/semana-4/instalacion-checkout-384ffaf/README.md)
registra comandos, duración y dificultades. El tiempo de checkout local no mide
una descarga completa desde GitHub. El ensayo oral sigue sin realizarse.

## Requisitos y diferencias del equipo usado

| Elemento | Requisito documentado | Entorno de esta preparación |
|---|---|---|
| Python | 3.13, como Docker/CI | 3.12.14 disponible; venv nuevo sin paquetes globales |
| Node | 22, como CI | 24.17.0 instalado |
| npm | Compatible con Node y lockfile | 11.13.0 |
| Git | Disponible para fijar revisión | 2.52.0.windows.1 |
| Modelo RAG | Disponible o descargable durante ingesta | Caché preexistente del equipo |
| Gemini | Clave solo para análisis real | Sin clave; pruebas locales/Demo/AST |
| Docker | Solo para la alternativa con contenedor | No utilizado en esta prueba |

Las diferencias de versión se informan, no se ocultan como reproducción exacta
de producción. Un integrante nuevo debe probar preferentemente Python 3.13 y
Node 22. No se modificaron las dependencias fijadas para facilitar la instalación.

## Procedimiento reproducible para un integrante

Antes de iniciar, registrar operador, Windows, versiones y cachés presentes.
Usar una carpeta nueva y el commit acordado, no una rama que siga cambiando.

```powershell
git clone https://github.com/Christian-gv-01/revisor-inteligente-codigo.git CODEGUARD-validacion
cd CODEGUARD-validacion
git checkout --detach 384ffafba3b10886751260c15a944e2b24f110ab
git status --short
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
cd frontend
npm ci
npm run build
cd ..
.\.venv\Scripts\python.exe scripts\ingest.py
.\.venv\Scripts\python.exe -m pip check
```

Estos comandos conservan valores predeterminados. No pegar claves en registros
ni activar presupuesto o correcciones. Se usa el ejecutable del venv directamente
para no depender de permisos de `Activate.ps1`. Si Python 3.13 o Node 22 no están
instalados, registrar el requisito faltante antes de medir una ejecución comparable.

Backend, desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Frontend, en otra terminal desde `frontend/`:

```powershell
npm run dev -- --host 127.0.0.1
```

Verificar `/health` en `http://127.0.0.1:8000`, cargar la URL indicada por Vite
y pulsar «Probar análisis» en modo Demo. Compilar React por sí solo no sirve
la interfaz desde FastAPI. La comprobación AST sin proveedor usa
`POST /api/v1/agente/previsualizar`; no sustituye el análisis con Gemini real.
Detener ambos procesos propios con Ctrl+C al finalizar.

## Registro humano todavía pendiente

| Dato | Valor |
|---|---|
| Integrante que no preparó el entorno | Pendiente |
| Equipo, versiones y cachés | Pendiente |
| Inicio/fin reales | Pendiente |
| Duración total, incluyendo dificultades | Pendiente |
| Comandos adicionales y errores | Pendiente |
| Salud, interfaz y modalidad probada | Pendiente |
| Evidencias y revisión exacta | Pendiente |

No marcar el objetivo de diez minutos como cumplido a partir del tiempo del
ejecutor automático ni excluir esperas o fallos de la medición humana.

## Exposición y resultados finales

Ronald indicó que primero deben consultar al ingeniero qué se expondrá el
7 de noviembre. Se preparó la [hoja de coordinación y ensayo](presentacion/ensayo-cronometrado.md)
sin asignar partes ni inventar una duración real. No se enviaron mensajes al equipo.

Las métricas, capturas y diapositivas permanecen identificadas con su revisión
histórica. Cuando Christian comparta la comparación final y Backend integre la
prioridad, actualizar solo lo afectado y registrar el nuevo commit. Esta tarea
no ejecuta la comparación real ni modifica flags o despliegues.
