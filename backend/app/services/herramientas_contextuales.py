"""Herramientas locales y acotadas; código y documentos son datos no confiables."""
from math import isfinite
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.services import presupuesto


CategoriaReferencia = Literal[
    "ejecucion_codigo", "inyeccion_sql", "inyeccion_comandos", "inyeccion",
    "credenciales", "rutas", "deserializacion",
]

CONSULTAS_CATEGORIA: dict[CategoriaReferencia, str] = {
    "ejecucion_codigo": "Python ejecución de código no confiable eval exec CWE-94 OWASP",
    "inyeccion_sql": "Python inyección SQL consultas parametrizadas CWE-89 OWASP",
    "inyeccion_comandos": "Python inyección de comandos subprocess shell CWE-78 OWASP",
    "inyeccion": "Python validación de entradas inyección CWE-74 OWASP",
    "credenciales": "Python credenciales secretos contraseñas incrustadas CWE-798 OWASP",
    "rutas": "Python recorrido de rutas path traversal CWE-22 OWASP",
    "deserializacion": "Python deserialización insegura pickle yaml load CWE-502 OWASP",
}


class ErrorHerramientaContextual(RuntimeError):
    """La recuperación local falló; no incluye detalles privados del proveedor."""


class ArgumentosLinea(BaseModel):
    model_config = ConfigDict(extra="forbid")
    linea: int = Field(strict=True, ge=1, le=12000)


class ArgumentosCategoria(BaseModel):
    model_config = ConfigDict(extra="forbid")
    categoria: CategoriaReferencia


class ArgumentosVacios(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LineaContexto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    numero: int = Field(strict=True, ge=1, le=12000)
    texto: str = Field(max_length=500)
    truncada: bool = Field(strict=True)


class ResultadoContexto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    linea_objetivo: int = Field(strict=True, ge=1, le=12000)
    linea_inicio: int = Field(strict=True, ge=1, le=12000)
    linea_fin: int = Field(strict=True, ge=1, le=12000)
    lineas: list[LineaContexto] = Field(min_length=1, max_length=13)

    @model_validator(mode="after")
    def validar_ventana(self):
        if not self.linea_inicio <= self.linea_objetivo <= self.linea_fin:
            raise ValueError("La ventana debe contener la línea objetivo.")
        if self.linea_objetivo - self.linea_inicio > 6 or self.linea_fin - self.linea_objetivo > 6:
            raise ValueError("La ventana no puede superar seis líneas por lado.")
        if [linea.numero for linea in self.lineas] != list(range(self.linea_inicio, self.linea_fin + 1)):
            raise ValueError("Las líneas deben coincidir con la ventana y estar ordenadas.")
        return self


def _url_corpus(valor: object) -> str:
    """Valida solo metadatos; no resuelve DNS ni descarga el recurso."""
    if not isinstance(valor, str) or len(valor) > 2048:
        return ""
    if any(ord(caracter) <= 32 or ord(caracter) == 127 for caracter in valor):
        return ""
    try:
        partes = urlsplit(valor)
        if (
            partes.scheme != "https"
            or partes.hostname not in {
                "cwe.mitre.org", "cheatsheetseries.owasp.org", "owasp.org", "www.owasp.org",
            }
            or partes.username is not None
            or partes.password is not None
            or partes.port not in (None, 443)
            or "\\" in valor
        ):
            return ""
    except ValueError:
        return ""
    return valor


class FragmentoReferencia(BaseModel):
    model_config = ConfigDict(extra="forbid")
    area: Literal["seguridad"] = "seguridad"
    id: str = Field(min_length=1, max_length=160)
    texto: str = Field(max_length=2000)
    documento: str = Field(default="", max_length=300)
    seccion: str = Field(default="", max_length=300)
    fuente: str = Field(default="", max_length=300)
    url: str = Field(default="", max_length=2048)
    distancia: float | None = Field(default=None, strict=True, allow_inf_nan=False)

    @field_validator("id")
    @classmethod
    def validar_identificador(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("El identificador no puede estar vacío.")
        return valor

    @field_validator("url", mode="before")
    @classmethod
    def validar_url(cls, valor: object) -> str:
        return _url_corpus(valor)


class ResultadoReferencia(BaseModel):
    model_config = ConfigDict(extra="forbid")
    categoria: CategoriaReferencia
    fragmentos: list[FragmentoReferencia] = Field(default_factory=list, max_length=2)


def ampliar_contexto(codigo: str, argumentos: ArgumentosLinea) -> ResultadoContexto:
    argumentos = ArgumentosLinea.model_validate(argumentos)
    presupuesto.comprobar_plazo()
    if not isinstance(codigo, str):
        raise ValueError("El código debe ser texto.")
    if len(codigo) > 12000 or "\x00" in codigo:
        raise ValueError("El código admite hasta 12000 caracteres y no admite NUL.")
    lineas = codigo.splitlines()
    if len(lineas) > 12000 or argumentos.linea > len(lineas):
        raise ValueError("La línea debe existir en código de hasta 12000 líneas.")
    inicio = max(1, argumentos.linea - 6)
    fin = min(len(lineas), argumentos.linea + 6)
    resultado = ResultadoContexto(
        linea_objetivo=argumentos.linea, linea_inicio=inicio, linea_fin=fin,
        lineas=[
            LineaContexto(numero=n, texto=lineas[n - 1][:500], truncada=len(lineas[n - 1]) > 500)
            for n in range(inicio, fin + 1)
        ],
    )
    presupuesto.comprobar_plazo()
    return resultado


def _texto_acotado(valor: object, limite: int) -> str:
    return valor[:limite] if isinstance(valor, str) else ""


def _distancia_valida(valor: object) -> bool:
    if valor is None:
        return True
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    try:
        return isfinite(valor)
    except OverflowError:
        return False


def _es_fuente_seguridad(candidato: dict, identificador: str) -> bool:
    # RAG fija estos campos según la colección real; area procede del documento.
    procedencia = {"coleccion": "seguridad_python", "tipo_fuente": "seguridad"}
    presentes = [campo for campo in procedencia if campo in candidato]
    if presentes:
        return all(candidato[campo] == procedencia[campo] for campo in presentes)
    # Compatibilidad con resultados locales antiguos sin procedencia explícita.
    return candidato.get("area") == "seguridad" or identificador.startswith("seguridad_python-")


def buscar_referencia(argumentos: ArgumentosCategoria) -> ResultadoReferencia:
    argumentos = ArgumentosCategoria.model_validate(argumentos)
    presupuesto.comprobar_plazo()
    try:
        # Mantener la inspección de código disponible sin ChromaDB ni SDK de IA.
        from app.services.rag import buscar_fragmentos

        candidatos = buscar_fragmentos(CONSULTAS_CATEGORIA[argumentos.categoria], limite=2)
        fragmentos = []
        vistos = set()
        for candidato in candidatos:
            if not isinstance(candidato, dict):
                continue
            identificador = candidato.get("id")
            texto = candidato.get("texto")
            if (
                not isinstance(identificador, str) or not identificador.strip()
                or len(identificador) > 160
                or not isinstance(texto, str) or not texto.strip()
            ):
                continue
            if not _es_fuente_seguridad(candidato, identificador):
                continue
            if identificador in vistos:
                continue
            distancia = candidato.get("distancia")
            if not _distancia_valida(distancia):
                continue
            fragmentos.append(FragmentoReferencia(
                id=identificador, texto=texto[:2000],
                documento=_texto_acotado(candidato.get("documento"), 300),
                seccion=_texto_acotado(candidato.get("seccion"), 300),
                fuente=_texto_acotado(candidato.get("fuente"), 300),
                url=_url_corpus(candidato.get("url")), distancia=distancia,
            ))
            vistos.add(identificador)
            if len(fragmentos) == 2:
                break
        presupuesto.comprobar_plazo()
        return ResultadoReferencia(categoria=argumentos.categoria, fragmentos=fragmentos)
    except presupuesto.PlazoAgotado:
        raise
    except Exception:
        presupuesto.comprobar_plazo()
        raise ErrorHerramientaContextual("No fue posible recuperar las referencias locales.") from None
