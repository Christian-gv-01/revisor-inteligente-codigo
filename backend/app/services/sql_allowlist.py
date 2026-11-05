"""Filtro AST conservador para identificadores SQL de allow-list."""
import ast
import re
import unicodedata

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _name(node, value):
    return isinstance(node, ast.Name) and node.id == value


def _writes(target, value):
    if isinstance(target, ast.Name):
        return target.id == value
    if isinstance(target, ast.Subscript):
        return _name(target.value, value)
    if isinstance(target, (ast.Tuple, ast.List)):
        return any(_writes(item, value) for item in target.elts)
    return False


def _targets(node):
    if isinstance(node, ast.Assign):
        return node.targets
    if isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
        return [node.target]
    if isinstance(node, ast.Delete):
        return node.targets
    if isinstance(node, (ast.For, ast.AsyncFor)):
        return [node.target]
    return []


def _literal_map(node):
    if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
        return False
    if not node.value.keys:
        return False
    for key, value in zip(node.value.keys, node.value.values):
        if not (
            isinstance(key, ast.Constant) and isinstance(key.value, str)
            and isinstance(value, ast.Constant) and isinstance(value.value, str)
            and _IDENT.fullmatch(key.value)
            and _IDENT.fullmatch(value.value)
        ):
            return False
    return True


def _immutable(tree, initial, name):
    for node in ast.walk(tree):
        if node is initial:
            continue
        # Una referencia directa crea un alias mutable del diccionario.
        value = getattr(node, "value", None)
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(value, ast.Name) and value.id == name:
            return False
        if any(_writes(target, name) for target in _targets(node)):
            return False
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and _name(node.func.value, name):
                return False
            if any(_name(arg, name) for arg in node.args):
                return False
            if any(kw.value is not None and _name(kw.value, name) for kw in node.keywords):
                return False
    return True


def _sql_expr_safe(node, mapping, option):
    if isinstance(node, ast.Constant):
        return isinstance(node.value, str)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return (
            _sql_expr_safe(node.left, mapping, option)
            and _sql_expr_safe(node.right, mapping, option)
        )
    if isinstance(node, ast.Subscript):
        return _name(node.value, mapping) and _name(node.slice, option)
    return False


def _inside(target, statements):
    return any(child is target for stmt in statements for child in ast.walk(stmt))


def _option_unchanged(tree, option, start, end):
    for node in ast.walk(tree):
        line = getattr(node, "lineno", -1)
        if start <= line <= end:
            if any(_writes(target, option) for target in _targets(node)):
                return False
    return True


def lineas_sql_con_lista_permitida(codigo):
    """Devuelve solo líneas demostrablemente protegidas; ante duda, devuelve vacío."""
    try:
        tree = ast.parse(codigo)
    except (SyntaxError, ValueError, TypeError):
        return set()

    maps = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    maps.setdefault(target.id, []).append(node)

    safe_lines = set()
    for call in ast.walk(tree):
        if not (
            isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
            and call.func.attr == "execute" and call.args
            and isinstance(call.args[0], ast.BinOp)
            and isinstance(call.args[0].op, ast.Add)
        ):
            continue

        expr = call.args[0]
        pairs = {
            (node.value.id, node.slice.id)
            for node in ast.walk(expr)
            if isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and isinstance(node.slice, ast.Name)
        }

        for mapping, option in pairs:
            candidates = maps.get(mapping, [])
            if len(candidates) != 1:
                continue
            initial = candidates[0]
            if initial.lineno >= call.lineno or not _literal_map(initial):
                continue
            if not _immutable(tree, initial, mapping):
                continue
            if not _sql_expr_safe(expr, mapping, option):
                continue

            for guard in ast.walk(tree):
                test = getattr(guard, "test", None)
                valid_guard = (
                    isinstance(guard, ast.If)
                    and guard.lineno < call.lineno
                    and isinstance(test, ast.Compare)
                    and _name(test.left, option)
                    and len(test.ops) == 1 and isinstance(test.ops[0], ast.In)
                    and len(test.comparators) == 1
                    and _name(test.comparators[0], mapping)
                )
                if not valid_guard or not _inside(call, guard.body):
                    continue
                if not _option_unchanged(tree, option, guard.lineno, call.lineno):
                    continue
                safe_lines.add(call.lineno)
                break

    return safe_lines


def es_hallazgo_inyeccion_sql(categoria):
    text = unicodedata.normalize("NFKD", str(categoria)).casefold()
    text = "".join(c for c in text if not unicodedata.combining(c))
    return "inyeccion sql" in text or "sql injection" in text
