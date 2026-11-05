"""API GitHub controlada para integración HTTP sin acceder a repositorios externos."""
import base64
from types import SimpleNamespace
from unittest.mock import patch

import httpx


def install_github_fixture(stack, sql_code):
    from app.services import github_repos

    tree_sha = "a" * 40
    routes = {}
    for repo, files in {
        "proyecto": {"usuarios.py": sql_code},
        "parcial": {"fallo.py": "# INTEGRACION_ERROR\neval(user_input)\n", "segundo.py": "eval(user_input)\n"},
    }.items():
        base = f"/repos/qa-fixture/{repo}"
        routes[base] = {"private": False, "default_branch": "main"}
        routes[f"{base}/commits/main"] = {"commit": {"tree": {"sha": tree_sha}}}
        entries = []
        for index, (name, code) in enumerate(files.items(), 1):
            sha = format(index, "040x")
            data = code.encode("utf-8")
            entries.append({"type": "blob", "path": name, "size": len(data), "sha": sha})
            routes[f"{base}/git/blobs/{sha}"] = {"encoding": "base64", "content": base64.b64encode(data).decode("ascii")}
        routes[f"{base}/git/trees/{tree_sha}"] = {"truncated": False, "tree": entries}

    def handler(request):
        if request.url.host != "api.github.com" or request.url.path not in routes:
            return httpx.Response(404, json={"message": "fixture no disponible"})
        return httpx.Response(200, json=routes[request.url.path])

    # Sustituye solo el transporte externo de GitHub; conserva el módulo httpx
    # global que usan FastAPI, el evaluador y ChromaDB.
    stack.enter_context(patch.object(github_repos, "httpx", SimpleNamespace(
        Client=lambda **kwargs: httpx.Client(transport=httpx.MockTransport(handler), **kwargs),
        Timeout=httpx.Timeout, TimeoutException=httpx.TimeoutException, RequestError=httpx.RequestError,
    )))
