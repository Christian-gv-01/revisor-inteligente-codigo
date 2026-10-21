
# 03. Arquitectura del sistema

**Proyecto:** Revisor Inteligente de Código Seguro
**Estado:** Borrador inicial pendiente de validación del equipo.
**Responsable:** QA, seguridad y documentación técnica.

## 1. Problema que resolvemos

Revisar código manualmente puede consumir tiempo y dificultar la
identificación sistemática de errores y posibles vulnerabilidades.

El proyecto busca facilitar la revisión de código Python mediante
un sistema que permita analizar entradas y utilizar inteligencia
artificial generativa para apoyar la identificación de riesgos.

## 2. Objetivo del sistema

Desarrollar un revisor inteligente que permita analizar código
Python y presentar resultados estructurados, considerando la
seguridad de las entradas, la protección de las credenciales y
el tratamiento controlado de los errores.

El código recibido no debe ejecutarse ni importarse como parte
del proceso de análisis.

## 3. Arquitectura C4: nivel 1, contexto

### Actores y sistemas externos

- Desarrollador: usuario que solicita la revisión del código.
- Aplicación web: interfaz prevista para interactuar con el sistema.
- Backend: API que recibe solicitudes y gestiona el análisis.
- Proveedor de IA: servicio generativo previsto para apoyar el análisis.

### Flujo general previsto

Desarrollador -> Aplicación web -> Backend -> Proveedor de IA

Este flujo representa la arquitectura objetivo. La integración
completa debe verificarse con el código y las decisiones del equipo.

## 4. Arquitectura C4: nivel 2, contenedores

### Backend

- Lenguaje: Python.
- Framework: FastAPI.
- Función: exponer endpoints HTTP y gestionar las solicitudes.
- Endpoint confirmado en el código revisado: GET /health.

### Frontend

Existe una carpeta `frontend` en el repositorio.
La tecnología, los componentes y la integración deben confirmarse
revisando los archivos de esa carpeta.

### Proveedor de IA generativa

La configuración de ejemplo contempla las variables
GEMINI_API_KEY y GEMINI_MODEL.

La integración efectiva, el modelo definitivo y su flujo de
llamadas deben confirmarse con el equipo de backend.

### Persistencia

No se ha confirmado una base de datos ni un mecanismo de
persistencia en el código revisado.

## 5. Tecnologías identificadas

- Python.
- FastAPI.
- pytest para pruebas automatizadas.
- TestClient para probar endpoints.
- Google Gemini como proveedor previsto en la configuración
  de ejemplo, pendiente de confirmar con el equipo.
- Git y GitHub para el control de versiones y la colaboración.

## 6. Endpoints principales

### GET /health

Estado: implementado en el código revisado.

Respuesta esperada:

{
  "status": "ok",
  "service": "revisor-inteligente-codigo",
  "version": "0.1.0"
}

Los endpoints de análisis, carga de archivos y consulta de
repositorios quedan pendientes de confirmar en el contrato
de la API del equipo.

## 7. Requisitos no funcionales y controles de seguridad

- Proteger las claves mediante variables de entorno.
- No registrar claves de API ni código sensible en los logs.
- Validar el contenido, tipo y tamaño de las entradas.
- Rechazar archivos y rutas de extracción inseguras.
- Restringir el acceso a los repositorios autorizados.
- No ejecutar ni importar el código recibido.
- Establecer límites de tiempo y recursos.
- Tratar los comentarios del código como datos no confiables,
  no como instrucciones que deban obedecerse.
- Controlar errores del proveedor de IA sin revelar información
  sensible.
- Ejecutar pruebas automatizadas sin consumir API ni depender
  de Internet mediante mocks.

Estos puntos son requisitos de seguridad; su implementación
debe verificarse mediante revisión de código y pruebas.

## 8. Componentes pendientes para la semana 3

- Confirmar el contrato del endpoint de análisis.
- Completar el flujo de análisis con IA.
- Validar la carga de archivos y el tratamiento de ZIP.
- Implementar o verificar las restricciones de seguridad.
- Completar el workflow controlado del agente.
- Integrar frontend y backend.
- Ejecutar pruebas de errores y recopilar evidencias.
- Actualizar la arquitectura según las decisiones aprobadas.

## 9. Validación del equipo

Antes de considerar definitiva esta arquitectura, se deben
confirmar las tecnologías del frontend, el proveedor y modelo
generativo, los endpoints previstos y las decisiones de diseño.

La documentación describe el estado conocido y distingue
los componentes implementados de los que siguen pendientes.
