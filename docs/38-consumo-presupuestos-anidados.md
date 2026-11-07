# Consumo y límites de presupuestos anidados

Base comprobada: c522c24, 7 de noviembre de 2026. Al aprobar un ZIP, la ruta
creaba un presupuesto interior para respetar la instantánea autorizada. El
middleware conservaba otro exterior y publicaba su contador vacío: la cabecera
podía indicar cero aunque el informe generativo se hubiera completado. No afecta
los contadores de las rutas directa y agente de la comparación de cuarenta casos,
que no crean ese presupuesto interior.

La corrección vincula cada presupuesto a su padre, comparte el contador SDK y
el lock raíz, y reserva los intentos en toda la cadena de forma atómica. El hijo
conserva su límite propio y no amplía el plazo ni las llamadas del padre. Si algún
límite está agotado, no se consume ninguna reserva. No suma dos veces tokens.

La aprobación idempotente devuelve el resultado guardado con cero llamadas de
esa nueva solicitud. No se le atribuye otra vez el consumo de la aprobación
original. Respuestas sin metadatos o intentos sin respuesta conservan null,
sin inventar uso conocido. La cabecera no es una factura.

Se reprodujeron cinco fallos antes del cambio: uso perdido, contador global
reiniciado, límite menor, plazo ampliado y cabecera HTTP cero. Se añadieron seis
regresiones, incluidas concurrencia de hijos e idempotencia HTTP. Suite local:
669 aprobadas (589 backend y 80 QA/evaluadores), proveedor simulado y red externa
bloqueada. CI y prueba pública se registran después de revisar e integrar.

No cambia el dataset, los prompts, la política de severidad ni las autorizaciones.
Los topes se mantienen; anidar ya no permite reiniciar un presupuesto superior.
