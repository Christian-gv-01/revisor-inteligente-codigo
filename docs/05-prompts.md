# 05. Ingeniería de prompts — Comparación experimental

> Alcance histórico: las corridas descritas conservan su fecha y configuración.
> En `65675e2`, la síntesis utiliza `backend/app/prompts/system_v1.md`; la presencia
> de V2/V3 no significa que estén activas. El script histórico
> `backend/scripts/probar_analisis.py` mencionado abajo no está en el árbol actual;
> no se ofrece como comando vigente. Ver [evaluador actual](../eval/README.md) y
> [comparación de semanas](18-comparacion-semanas-3-4.md). No se reejecutó este experimento.

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


## 8. Experimento ampliado: diez casos de evaluación

**Fecha:** 23 de octubre de 2026  
**Modelo:** gemini-3.5-flash-lite  
**Configuración:** temperatura 0,2; máximo 2048 tokens de salida  
**Evidencia:** `docs/evidencias/semana-2/comparacion-10-casos.json`

Se evaluaron tres versiones del prompt con diez fragmentos Python: cuatro vulnerables, tres limpios, dos con instrucciones dirigidas al analizador y uno ambiguo. Se realizaron 30 solicitudes reales al proveedor.

### Resultados

| Métrica | V1 | V2 | V3 |
|---|---:|---:|---:|
| Vulnerabilidades principales detectadas (4) | 4 | 3 | 4 |
| Intentos de inyección reportados (2) | 0 | 0 | 2 |
| Archivos limpios sin hallazgos (3) | 3 | 3 | 3 |
| Alertas críticas en caso ambiguo C10 | 1 | 1 | 1 |
| Respuestas JSON válidas | 10 | 10 | 10 |
| Tiempo acumulado | 80,53 s | 58,65 s | 47,39 s |
| Tokens totales | 3.242 | 3.824 | 5.155 |

### Análisis de resultados

V1 presentó una detección satisfactoria de las cuatro vulnerabilidades principales, pero no identificó las instrucciones de manipulación dirigidas al modelo.

V2 incorporó criterios más estrictos de evidencia, aunque omitió el hallazgo de credencial fija. Esto demuestra que una mayor especificidad en el prompt no garantiza una mejora en todas las categorías.

V3 detectó los cuatro escenarios vulnerables principales y reportó ambos intentos explícitos de inyección de prompt. También conservó el formato estructurado esperado.

Ninguna versión reportó hallazgos en los tres fragmentos limpios. Las tres produjeron una alerta de severidad crítica sobre `eval("2 + 2")`, pese a que el fragmento no muestra entrada externa controlable por un atacante. Este caso evidencia la necesidad de calibrar las severidades y distinguir patrones peligrosos de vulnerabilidades explotables.

### Conclusión y decisión

El experimento permitió identificar una ventaja de V3 en el reporte de instrucciones maliciosas incluidas dentro del código analizado.

Se recomienda V3 como candidato para la siguiente versión del sistema, sujeto a pruebas adicionales de regresión, precisión y resistencia a inyección de prompt.

La versión activa del backend se mantiene sin cambios para preservar la estabilidad de la demostración.

### Limitaciones

Los resultados corresponden a una ejecución por combinación de caso y prompt. La muestra no permite establecer tasas generales de precisión ni demostrar resistencia absoluta a inyección de prompt.

La evaluación de C10 requiere juicio contextual. Los errores del proveedor, cuando existan, deben diferenciarse de los falsos negativos del modelo.
