# Checklist de integración local

- [ ] Extraer el ZIP en la raíz del repositorio.
- [ ] Ejecutar `.\APLICAR_EN_WINDOWS.ps1` desde la raíz.
- [ ] Revisar que `backend/app/main.py` incluya `correcciones_router`.
- [ ] Ejecutar `python -m pytest tests/test_correcciones.py -v --tb=short` desde `backend`.
- [ ] Ejecutar `python -m pytest -q --tb=short` desde `backend`.
- [ ] Probar previsualización real con Gemini configurado.
- [ ] Probar aprobar y comprobar que el contenido coincide exactamente.
- [ ] Probar rechazo y comprobar que no hay campo `contenido`.
- [ ] Probar caducidad (HTTP 410).
- [ ] Probar hash alterado y decisión contraria (HTTP 409).
- [ ] Coordinar con Frontend antes de activar `VITE_CORRECTIONS_API_ENABLED=1`.
- [ ] No hacer push, merge ni despliegue sin revisión conjunta.
