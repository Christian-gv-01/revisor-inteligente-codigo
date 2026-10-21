
# Revisión de seguridad del sistema

**Proyecto:** Revisor Inteligente de Código Seguro
**Responsable:** Área de QA y seguridad
**Rama:** feature/qa-seguridad
**Estado:** Revisión inicial en curso

## 1. Protección de credenciales

**Riesgo:** exposición de claves de API y otros secretos.

**Controles que se deben verificar:**
- Obtener las claves mediante variables de entorno.
- Excluir los archivos `.env` del repositorio.
- Mantener `.env.example` sin credenciales reales.
- Evitar que las claves aparezcan en mensajes de error.

**Estado:** Pendiente de verificar la implementación completa.

## 2. Validación de archivos

**Riesgo:** recepción de archivos no permitidos o demasiado grandes.

**Controles que se deben verificar:**
- Permitir únicamente los tipos de archivo autorizados.
- Establecer un tamaño máximo.
- Validar el contenido del archivo.
- Rechazar archivos inválidos o no permitidos.

**Estado:** Pendiente de verificar.

## 3. Seguridad de archivos ZIP

**Riesgo:** archivos comprimidos maliciosos, rutas inseguras
y consumo excesivo de recursos.

**Controles que se deben verificar:**
- Impedir la extracción fuera del directorio autorizado.
- Limitar el tamaño total y la cantidad de archivos.
- Evitar la extracción de archivos peligrosos.
- Controlar errores durante el procesamiento.

**Estado:** Pendiente de verificar.

## 4. Repositorios autorizados

**Riesgo:** acceso a repositorios o recursos no autorizados.

**Controles que se deben verificar:**
- Permitir únicamente repositorios públicos autorizados.
- Validar el dominio y la URL recibida.
- Prevenir solicitudes hacia direcciones internas o privadas.

**Estado:** Pendiente de verificar.

## 5. Aislamiento del código recibido

**Riesgo:** ejecución accidental de código malicioso.

**Controles que se deben verificar:**
- Analizar el código como texto.
- No ejecutar ni importar el código recibido.
- No permitir que el código analizado acceda al sistema de archivos
  ni a otros recursos mediante su ejecución.

**Estado:** Pendiente de verificar.

## 6. Límites de tiempo y recursos

**Riesgo:** solicitudes bloqueadas o consumo excesivo de recursos.

**Controles que se deben verificar:**
- Establecer tiempos máximos de espera.
- Limitar el tamaño de las entradas.
- Gestionar los errores y las solicitudes agotadas por tiempo.
- Evitar procesamientos excesivamente grandes.

**Estado:** Pendiente de verificar.

## 7. Protección de registros (logs)

**Riesgo:** exposición de código sensible o credenciales.

**Controles que se deben verificar:**
- No registrar claves ni tokens.
- Evitar guardar el código completo sin necesidad.
- Registrar errores sin divulgar información sensible.

**Estado:** Pendiente de verificar.

## 8. Instrucciones maliciosas dirigidas a la IA

**Riesgo:** comentarios Python que intenten modificar las
instrucciones del sistema o revelar información confidencial.

**Controles que se deben verificar:**
- Tratar el código recibido como contenido no confiable.
- Separar las instrucciones del sistema del código analizado.
- No obedecer instrucciones incluidas en comentarios o cadenas
  del código recibido.
- Validar la salida generada por la IA.

**Estado:** Pendiente de verificar.

## 9. Evidencias y seguimiento

Se incorporarán capturas, pruebas automatizadas y resultados
reales a medida que se verifique cada control.

No se marcará ninguna protección como implementada o aprobada
hasta revisar el código correspondiente y realizar las pruebas
necesarias.

## 10. Observaciones

Esta revisión es inicial. Los controles pendientes deberán
contrastarse con la implementación real del backend y con
las decisiones acordadas por el equipo.
