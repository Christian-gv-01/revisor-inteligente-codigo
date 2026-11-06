# Entrega de Ronald para integración de frontend

Fecha: 6 de noviembre de 2026. Responsable: Ronald Yépez.

## Rama, base y alcance

Se conserva `feature/entrega4-frontend-producto`, como permite el mensaje del líder.
El destino de revisión es un PR **Draft hacia main**. No fusionar, hacer push
directo a `main` ni ejecutar un despliegue manual en Railway.

- Commit del que partió la rama: `578adee2af129da19a571792ffffe913c1657737`.
- Base del producto anterior a la documentación: `65675e27fd996a7e71a926336dba6dffb5e539e2`.
- Implementación frontend: `4c483dd`; contrato y ejemplos: `6c1f312`.
- Para obtener el commit actual exacto de esta entrega: `git rev-parse HEAD`.

La rama incluye el cierre documental del [PR #32](https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/32),
que seguía abierto al preparar esta entrega. Revisar esa dependencia para evitar
duplicar cambios. No se incorporaron mediante merge o rebase los cambios nuevos
de `main`; la consolidación corresponde a la rama de integración del equipo.

Incluye original y propuesta visibles, consentimiento explícito, cancelación,
descarga de copia con otro nombre, validación de integridad y caducidad, prioridad
visible y aviso de análisis parcial. Mantiene fuentes y proceso del agente.
Incluye ocho historias Dado/Cuando/Entonces, inventario de fuentes, arquitectura,
descripción del producto y borrador de presentación de doce minutos.

## Iniciar y probar

Desde `frontend/`, con Node/npm compatibles con el proyecto:

```powershell
npm ci
npm run dev -- --host 127.0.0.1
```

Abrir la URL local indicada por Vite. En modo Demo, conservar el ejemplo SQL
inicial, analizar y pulsar «Previsualizar propuesta». Es una propuesta fija de
demostración: no acredita una corrección generada por Gemini.

Desde `frontend/`, ejecutar las comprobaciones por separado:

```powershell
npm test -- --reporter=dot
npm run lint
npm run build
```

Para los ocho escenarios de navegador, desde la raíz y con Playwright y un
navegador de pruebas disponibles:

```powershell
node frontend/tests/correction-browser.mjs tmp/correction-browser
```

Las [instrucciones del navegador](evidencias/semana-4/frontend-producto-20261106/README.md)
explican las variables opcionales del ejecutor. No requiere cambiar dependencias
de producción. El script bloquea conexiones externas y usa un perfil aislado.

## Variables

| Variable | Ejemplo ficticio/local | Uso |
|---|---|---|
| `VITE_CORRECTIONS_API_ENABLED` — nueva | `0` | Ausente o distinto de `1`: API de correcciones deshabilitada. Usar `1` solo en la prueba acordada con el backend candidato |
| `VITE_API_BASE_URL` — existente | cadena vacía | Rutas `/api/...`; en desarrollo Vite redirige al backend local `http://127.0.0.1:8000` |

Son variables de Vite: reiniciar el servidor de desarrollo o reconstruir el
frontend cuando cambien. No agregar claves de Gemini ni secretos al frontend.
No es necesario modificar variables de Railway para revisar esta entrega.

## Contrato y prueba conjunta pendiente

Entregar a Christian el [contrato v1](20-contrato-confirmacion-humana.md) y
los [seis ejemplos JSON](contrato-confirmacion-v1/README.md). Son el contrato
propuesto y respuestas simuladas; los endpoints reales deben verificarse con su rama.

1. Previsualizar: verificar ID, archivo, hashes, código propuesto y caducidad.
2. Aprobar: exigir consentimiento y descargar exactamente la copia revisada.
3. Rechazar: registrar rechazo; no descargar ni ejecutar código.
4. Caducidad: comprobar respuesta HTTP 410 y necesidad de nueva propuesta.
5. Conflictos: comprobar HTTP 409, contenido cambiado y decisiones incompatibles.
6. Cambiar entrada o cancelar durante una respuesta: descartar resultados tardíos.
7. Alinear prioridad visible con los campos finales de priorización del backend.

Christian inicia el backend candidato con sus instrucciones y variables. Ronald
activa el adaptador únicamente en el entorno local acordado. La suite HTTP existente
se habilita con `INTEGRATION_API_BASE_URL` apuntando a ese backend local; no sustituye
las nuevas comprobaciones conjuntas de aprobación/rechazo. No apuntar estos
escenarios a producción ni mezclar resultados simulados con Gemini real.

## Evidencia disponible y límites

La [validación local registrada](evidencias/semana-4/frontend-producto-20261106/validacion.json)
contiene 91 pruebas frontend aprobadas, 17 HTTP omitidas, ESLint correcto y build
correcto con la advertencia existente de bundle mayor de 500 kB. Se registraron
ocho escenarios de navegador aprobados. Las evidencias conservan el estado local
original de su ejecución; publicarlas no convierte esas pruebas en pruebas remotas.

El PR permite revisar y ejecutar CI. No certifica la confirmación humana contra
backend real, una integración terminada ni un despliegue. La integración y sus
evidencias deberán completarse antes de considerar la funcionalidad lista para producción.
