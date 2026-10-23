# Revisor Inteligente de Código Seguro

## 1. Descripción del proyecto

 Caso 10. El objetivo es desarrollar un sistema que ayude a identificar posibles vulnerabilidades en código Python mediante análisis automatizado e inteligencia artificial.

El proyecto se encuentra en desarrollo y sus funcionalidades se integrarán progresivamente mediante ramas de trabajo independientes.

## 2. Objetivos

- Identificar posibles problemas de seguridad en código Python.
- Validar las entradas recibidas por el sistema.
- Evitar la ejecución del código analizado.
- Proteger credenciales y datos sensibles.
- Proporcionar resultados estructurados.
- Verificar el funcionamiento mediante pruebas automatizadas.

## 3. Tecnologías

- Python.
- FastAPI para el backend.
- Pytest para las pruebas automatizadas.
- Google Gemini como proveedor de análisis asistido por inteligencia artificial, integrado mediante el servicio del backend. Las pruebas automatizadas utilizan mocks para evitar llamadas reales a la API.
- Git y GitHub para el control de versiones y la colaboración.

## 4. Estructura del proyecto

```text
revisor-inteligente-codigo/
├── backend/
│   ├── app/
│   │   └── main.py
│   └── tests/
│       └── test_health.py
├── docs/
│   ├── evidencias/
│   │   └── semana-2/
│   │       └── bitacora.md
│   ├── 03-arquitectura.md
│   ├── 09-decisiones.md
│   └── revision-seguridad.md
├── frontend/
├── .gitignore
└── README.md
```

## 5. Preparación del entorno

Desde la raíz del repositorio, abre PowerShell y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn pytest httpx
```

Si ya tienes el entorno virtual configurado, no necesitas crearlo nuevamente.

## 6. Iniciar el backend

Desde la raíz del repositorio:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Direcciones locales:

- Endpoint de salud: `http://127.0.0.1:8000/health`
- Documentación de FastAPI: `http://127.0.0.1:8000/docs`

El endpoint `/health` comprueba el estado básico de la API.

## 7. Ejecutar las pruebas

Desde la carpeta `backend`:

```powershell
python -m pytest tests -v
```

Los resultados deben registrarse como evidencias reales. Hasta el momento se ha comprobado una prueba inicial del endpoint de salud.

## 8. Variables de entorno y credenciales

La integración con el proveedor de inteligencia artificial contempla estas variables:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `LLM_TIMEOUT_SECONDS`
- `LLM_MAX_OUTPUT_TOKENS`

La configuración definitiva debe confirmarse con el equipo de backend.

No deben subirse claves reales al repositorio. Los archivos `.env` deben permanecer excluidos del control de versiones y `.env.example` debe contener únicamente valores de ejemplo.

## 9. Controles de seguridad

Se deben verificar los siguientes aspectos:

- Validación del código y las entradas recibidas.
- Restricciones de tipos y tamaños de archivos.
- Protección frente a archivos ZIP maliciosos y rutas inseguras.
- Restricción de acceso a repositorios autorizados.
- Prohibición de ejecutar o importar código recibido.
- Límites de tiempo y recursos.
- Protección de logs y mensajes de error.
- Tratamiento del código analizado como contenido no confiable, incluidas las instrucciones maliciosas dirigidas a la IA.

Los controles solo se considerarán aprobados cuando exista evidencia de su implementación y de las pruebas correspondientes.

## 10. Limitaciones actuales

La versión inicial dispone de una API básica y un endpoint de salud. Las funcionalidades de análisis de código, el tratamiento de errores del proveedor de IA, las validaciones avanzadas y la interfaz deben verificarse a medida que se integren los componentes del equipo.

## 11. Documentación y evidencias

La carpeta `docs/` contiene la documentación de arquitectura, las decisiones arquitectónicas, la revisión de seguridad y las evidencias de QA.

Se deben registrar los resultados de las pruebas, los problemas encontrados, las soluciones aplicadas y las capturas pertinentes sin inventar resultados.

## 12. Organización del equipo

El proyecto se divide en áreas de trabajo:

- Backend e integración de inteligencia artificial.
- Frontend e interfaz de usuario.
- QA, seguridad y documentación técnica.

Cada integrante debe trabajar en su rama asignada, registrar sus cambios mediante commits y coordinar la integración mediante Pull Requests.

**Entrega prevista:** viernes 23 de octubre de 2026.
