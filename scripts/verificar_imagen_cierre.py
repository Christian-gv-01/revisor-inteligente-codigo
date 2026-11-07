"""Smoke local del contenedor sin llamar al proveedor ni ejecutar código recibido."""
import io
import json
import os
from http.cookies import SimpleCookie
from urllib.request import Request, urlopen
from zipfile import ZipFile


def comprobar(base_url):
    memoria = io.BytesIO()
    with ZipFile(memoria, "w") as z:
        z.writestr("ejemplo.py", "print(1)\n")
    limite = "codeguard-smoke-cierre"
    cuerpo = (f"--{limite}\r\nContent-Disposition: form-data; name=\"archivo\"; filename=\"ejemplo.zip\"\r\n"
              "Content-Type: application/zip\r\n\r\n").encode() + memoria.getvalue() + f"\r\n--{limite}--\r\n".encode()
    solicitud = Request(base_url + "/api/v1/proyectos/previsualizar/zip", data=cuerpo,
                        headers={"Content-Type": f"multipart/form-data; boundary={limite}"})
    with urlopen(solicitud, timeout=10) as r:
        assert r.status == 200
        propuesta = json.load(r)
        cookie = SimpleCookie(r.headers["Set-Cookie"])
        assert cookie["codeguard_proyectos"]["httponly"]
        assert cookie["codeguard_proyectos"]["samesite"].lower() == "strict"
    assert propuesta["estado"] == "pendiente_confirmacion"
    assert propuesta["total_archivos"] == 1
    assert propuesta["presupuesto"]["analisis_previstos"] == 1
    datos = {"decision": "rechazar", "confirmar": False, "sha256_manifiesto": propuesta["sha256_manifiesto"]}
    rechazo = Request(base_url + f"/api/v1/proyectos/{propuesta['presupuesto_id']}/decision",
                      data=json.dumps(datos).encode(), headers={"Content-Type": "application/json",
                      "Cookie": "; ".join(f"{k}={v.value}" for k, v in cookie.items())})
    with urlopen(rechazo, timeout=10) as r:
        assert r.status == 200
        assert json.load(r)["estado"] == "rechazado"
        consumo = json.loads(r.headers["X-Codeguard-Consumo-IA"])
        assert consumo["intentos"] == 0
    return {"presupuesto_visible": True, "rechazo_sin_proveedor": True}


if __name__ == "__main__":
    print(json.dumps(comprobar("http://127.0.0.1:" + os.getenv("PORT", "8000"))))
