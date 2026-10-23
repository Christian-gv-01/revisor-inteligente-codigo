# 05. Ingeniería de prompts — Comparación experimental

**Proyecto:** Revisor Inteligente de Código Seguro (CODEGUARD)  
**Universidad:** UNIANDES  
**Caso:** 10  
**Fecha:** 23 de octubre de 2026

## 1. Objetivo

Evaluar tres versiones de un system prompt para analizar estáticamente fragmentos de código Python mediante inteligencia artificial generativa, identificando diferencias en las instrucciones, el formato de salida, la detección de vulnerabilidades, la latencia y el consumo de tokens.

## 2. Configuración del experimento

- **Proveedor:** Google Gemini.
- **Modelo:** gemini-3.5-flash-lite.
- **Temperatura:** 0,2.
- **Límite máximo de salida:** 2048 tokens.
- **Formato:** JSON estructurado validado con Pydantic.
- **Método:** una solicitud independiente por versión, utilizando el mismo código Python.
- **Archivo de pruebas:** `backend/scripts/probar_analisis.py`.

### Fragmento evaluado

```python
usuario = input("Ingresa un valor: ")
resultado = eval(usuario)
print(resultado)
```

**Resultado esperado:** identificar el uso inseguro de `eval()` sobre una entrada no confiable, localizado en la línea 2.

## 3. Versiones evaluadas

### V1 — Prompt inicial

Archivo: `backend/app/prompts/system_v1.md`.

Instrucciones generales para la revisión estática de código Python, identificación de problemas sustentados en evidencia, corrección sugerida y prohibición de ejecutar código.

### V2 — Precisión y evidencia

Archivo: `backend/app/prompts/system_v2.md`.

Amplía las instrucciones para exigir evidencia concreta, distinguir problemas de estilo de vulnerabilidades y explicar las condiciones necesarias para que exista un riesgo.

### V3 — Seguridad frente a inyección de prompt

Archivo: `backend/app/prompts/system_v3.md`.

Introduce reglas explícitas de jerarquía de confianza y tratamiento de comentarios, cadenas y docstrings como datos no confiables. También instruye al modelo para identificar intentos explícitos de manipulación del analizador.

## 4. Resultados experimentales

| Métrica | V1 | V2 | V3 |
|---|---:|---:|---:|
| Hallazgos identificados | 1 | 1 | 1 |
| Línea detectada | 2 | 2 | 2 |
| Severidad reportada | Crítica | Crítica | Crítica |
| Respuesta JSON válida | Sí | Sí | Sí |
| Tiempo de respuesta | 1,49 s | 1,12 s | 38,14 s |
| Tokens de entrada | 235 | 297 | 406 |
| Tokens de salida | 145 | 165 | 157 |

## 5. Interpretación

Las tres versiones detectaron correctamente el uso inseguro de `eval()` en la línea 2, y produjeron una respuesta estructurada válida.

V1 consumió menos tokens de entrada y proporcionó una explicación suficiente para este caso.

V2 mantuvo la detección correcta y enfatizó la precisión del hallazgo. En esta ejecución presentó la menor latencia.

V3 incorporó restricciones más explícitas frente a instrucciones maliciosas presentes en el contenido analizado, pero esta primera prueba no permite medir su eficacia contra inyecciones de prompt.

El mayor tiempo registrado para V3 no demuestra que esa versión sea intrínsecamente más lenta, ya que solo se realizó una ejecución por versión.

## 6. Limitaciones

- Solo se evaluó un fragmento vulnerable.
- No se realizaron suficientes repeticiones para estimar tiempos medios ni variabilidad.
- No se evaluaron todavía archivos limpios para medir falsos positivos.
- No se ejecutó una prueba adversarial que permita comparar la resistencia a inyección de prompt.
- Las mediciones corresponden a un experimento exploratorio, no a la validación definitiva del producto.

## 7. Conclusiones y siguiente evaluación

Las tres versiones alcanzaron el resultado esperado para la vulnerabilidad analizada. V2 ofrece instrucciones más específicas y V3 incorpora controles adicionales de confianza, pero ninguna de estas diferencias demuestra por sí sola una mejora general en precisión o seguridad.

La siguiente evaluación debe incluir código limpio, vulnerabilidades de diferentes categorías e instrucciones maliciosas ocultas en comentarios para medir detecciones, falsos positivos y resistencia a inyección de prompt.

**Decisión provisional:** conservar V1 como prompt activo del backend estable hasta completar las pruebas comparativas. No sustituir el prompt de producción únicamente por los resultados de una prueba.
