# Integración de confirmación humana: PR 34 y PR 35

> Actualización: PR #36 fue fusionado en `caecd71` el 6 de noviembre.
> El despliegue y la evaluación posterior se registran en
> [24-validacion-real-postmerge.md](24-validacion-real-postmerge.md).
> El estado de candidata descrito a continuación corresponde a su preparación.

Estado: candidata aislada de QA, sin fusión en main ni despliegue. Base de producción
`089f7142f96f3ca261f9aabdee0ef862efea67d6`, frontend `3719437c3bc7f78da6c1fba4319b14db3d8faeef`,
backend `5644f9570058dfce4f8e2060652867b5511de449`. La rama conserva esos commits
como padres; las resoluciones se revisan en un PR de integración independiente.

## Resolución de diferencias

La rama backend parte de `563cc38`, anterior al main vigente. Su cifra de 213
pruebas no es comparable sin conservar las regresiones añadidas posteriormente.
La candidata conserva todas las pruebas de main, las 34 de configuración,
priorización y confirmación del PR 35 y añade regresiones de integración.

| Área | Resolución |
|---|---|
| main.py | Mantener sanitización 422, presupuesto y concurrencia de main; registrar correcciones y aplicar sus límites a previsualización y decisión |
| llm.py/agente.py | Mantener citas, anclaje literal, estado parcial y envío real de evidencia del PR 31; conectar configuración y priorización del PR 35 |
| RAG | Mantener filtros y procedencia actuales; centralizar ruta y distancia |
| Motor estático | Mantener la captura acotada y sus regresiones; no sustituir por una copia anterior |
| HomePage | Mantener la interfaz y cancelación del PR 34, con el agente actual |
| Requisitos/CI/Docker | Mantener versiones y controles del PR 33; extender el smoke para probar la base temporal de propuestas |
| Gitleaks | Mantener el escaneo completo de main; no duplicar el workflow antiguo secretos.yml |
| Documentos | Incorporar el cierre documental de PR 34 (incluye PR 32), manteniendo límites y registros históricos |

No se sustituyen el prompt activo ni el dataset congelado por las variantes de
la rama antigua. Tampoco se conecta su filtro SQL de allow-list: forma parte de
otra modificación y requiere revisión separada antes de suprimir hallazgos. Las
corridas históricas de esa rama se conservan en su commit original, sin presentarlas
como resultados de esta candidata. La revisión de prompts/datasets no se mezcla
con la prueba de confirmación.

## Contrato compatible y acceso

Se mantienen las rutas y cuerpos v1 de [20-contrato-confirmacion-humana.md](20-contrato-confirmacion-humana.md).
La previsualización establece una cookie de sesión aleatoria HttpOnly y SameSite
Strict, Secure al servir el frontend en producción. La decisión exige esa misma
sesión además del ID y los hashes. Solo se guarda el hash de la sesión: el ID de
la URL ya no funciona como credencial suficiente. No hay cuentas de usuario ni se
atribuye esa sesión a una identidad personal. El flujo requiere mismo origen o
el proxy de Vite; no se habilita CORS con credenciales a cualquier dominio.

La propuesta es inmutable. Aprobar devuelve exactamente el contenido revisado;
rechazar borra su contenido y no descarga. Repetir una decisión durante la vigencia
es idempotente; una decisión contraria devuelve 409. Otra sesión o un ID desconocido
devuelve 404. Caducidad devuelve 410 mientras exista su tombstone. Si la aprobación
se comprometió antes de cancelar, el rechazo puede recibir 409: la interfaz evita
la descarga tardía y comunica que el rechazo remoto no quedó registrado.

La propuesta caduca a los cinco minutos. La limpieza periódica retira su contenido
con hasta 60 segundos adicionales de desfase; al decidir se verifica inmediatamente
la vigencia. Se mantienen hasta 200 filas y diez propuestas vigentes por sesión.
Los tombstones pueden conservarse hasta 24 h y expulsarse antes para respetar el
límite de filas. SQLite se crea con permisos 0600 junto a ChromaDB, normalmente
`/data/correcciones.sqlite3`, y se usa secure_delete para limpiar el contenido
retirado de páginas SQLite. Esto no promete borrar copias de seguridad del volumen.

El generador de propuestas usa Gemini; las pruebas automatizadas sustituyen solo
ese proveedor. Se cierra su cliente en errores/éxito, se rechaza MAX_TOKENS y se
valida sintaxis sin ejecutar. Sintaxis válida y aprobación no certifican que la
corrección elimine la vulnerabilidad ni preserve toda la semántica del programa.

## Configuración y prioridad

Las lecturas del entorno de la aplicación están en app/config/settings.py (excepto
PATH del proceso aislado de herramientas). Los límites y umbrales de LLM, RAG,
concurrencia, presupuesto, herramientas y propuestas se centralizan allí. Los
límites de los contratos Pydantic/frontend siguen siendo contratos fijados, no
parámetros configurables independientemente que puedan romper su compatibilidad.
Se conserva STATIC_ANALYSIS_ENABLED=0 por defecto en las rutas directas, como en
main; Docker lo activa y el agente ejecuta analizadores obligatoriamente.

La política de orden v1 se centraliza en app/config/priorizacion.py: severidad,
categoría normalizada (seguridad, desconocida, calidad) y empate estable. Su segundo
criterio sí cambia el orden entre categorías de igual severidad; no recalifica
la severidad propuesta por el modelo ni prueba explotabilidad. El frontend mantiene
ese orden en empates y muestra las bandas de revisión derivadas de severidad.
No se presenta como una valoración independiente del impacto técnico.

## Cómo probar

Desde backend: `python -m pytest tests ../qa -q`.

Desde frontend: `npm ci`, `npm run lint`, `npm test -- --run`, `npm run build`.

Desde la raíz, con índice local preparado:

```bash
python scripts/ingest.py
python eval/run_integration.py --static-analysis --output tmp/http-estatico
python eval/run_integration.py --output tmp/http-sin-estatico
```

El runner inicia FastAPI real en loopback, usa ChromaDB/Ruff/Bandit/SQLite reales y
Gemini/GitHub simulados. Los siete casos HTTP de correcciones prueban aprobación,
rechazo, aislamiento de sesiones, hashes, caducidad, 422 seguro y timeout. El control
de caducidad de `/__integration__` existe exclusivamente en ese runner no incluido
en Docker, nunca en app.main ni en el servicio publicado.

Con Playwright instalado, establecer PLAYWRIGHT_MODULE_PATH si es necesario y usar
`--correction-browser`. Se recorren siete casos desde el HomePage real con cookies
y respuestas HTTP reales, incluida cancelación tras una decisión del backend. El
proveedor generativo sigue simulado. El workflow conserva además los ocho escenarios
de demostración del PR 34. El navegador local del entorno QA no está disponible;
la ejecución de navegador se verifica en Actions.

Para uso manual local: backend en 127.0.0.1:8000, `CORRECTIONS_COOKIE_SECURE=0` solo
para HTTP local; frontend con `VITE_CORRECTIONS_API_ENABLED=1`. VITE_API_BASE_URL vacía
usa el proxy y CODEGUARD_DEV_API_TARGET permite apuntarlo al backend candidato.
La versión publicada mantiene las correcciones deshabilitadas por defecto.

## Seguridad histórica

El fallo del workflow antiguo del PR 35 identifica el SHA-256 LLM documentado bajo
el rótulo API en docs/07-evaluacion.md, commit `11dd2f80e1ba377cf317961e1cc518a78db777d9`,
línea 232. Se contrastó ese valor con llm_sha256 de la evidencia API del 4 de noviembre.
Se exceptúa solo su fingerprint histórico completo. No es prueba de revocación de
credenciales ni una exclusión del documento o de las reglas de claves.

## Pendientes antes de producción

Revisar los resultados de CI de la candidata, aprobación del equipo y permiso de
fusión; después verificar la misma revisión desplegada, matriz pública y evaluación
generativa comparable. El borrador de presentación y las evidencias originales de
Semana 1 siguen requiriendo revisión del equipo. El archivo final no se construye
ni se declara listo a partir de estas pruebas simuladas.

## Validación local de la candidata

- Backend y QA: 296 pruebas aprobadas, incluidas las específicas; no se suman otra vez.
- Frontend unitario: 91 aprobadas; las 24 HTTP se ejecutan aparte. Lint y build correctos.
- HTTP con Ruff/Bandit: 24/24 aprobadas; sin estático: 19 aprobadas y cinco no aplicables.
- FastAPI, SQLite, AST, Ruff/Bandit y recuperación local se usan realmente en las pruebas HTTP; Gemini y GitHub externo están simulados.
- La comprobación de navegador con backend real se ejecuta en CI; su resultado y el smoke Docker deben comprobarse en el commit publicado.
- No se han fusionado cambios en main ni desplegado esta candidata. La evaluación de calidad con Gemini real sigue pendiente.
