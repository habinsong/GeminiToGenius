"""Python 소스 하나의 정의·복잡도·응집도·빈 구현·단순 전달을 AST로 잽니다. IO는 하지 않습니다."""

from __future__ import annotations

import ast


ABSTRACT_DECORATORS = {"abstractmethod", "abstractproperty", "abstractclassmethod", "abstractstaticmethod", "overload"}
BRANCHES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp, ast.comprehension,
            getattr(ast, "match_case", ast.If))
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def name_of(node: ast.AST | None) -> str | None:
    """Name·Attribute·호출·첨자의 마지막 이름입니다. `abc.ABC`는 `ABC`가 됩니다."""
    if isinstance(node, ast.Call):
        node = node.func
    if isinstance(node, ast.Subscript):
        node = node.value
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def complexity(function: ast.AST) -> int:
    """McCabe 복잡도입니다. 안쪽에 정의한 함수·클래스·람다는 따로 셉니다."""
    count, stack = 1, list(ast.iter_child_nodes(function))
    while stack:
        node = stack.pop()
        if isinstance(node, (*FUNCTIONS, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(node, BRANCHES):
            count += 1
        if isinstance(node, ast.BoolOp):
            count += len(node.values) - 1
        if isinstance(node, ast.comprehension):
            count += len(node.ifs)
        stack.extend(ast.iter_child_nodes(node))
    return count


def statements(function: ast.AST) -> list[ast.stmt]:
    body = function.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    return body


def placeholder(statement: ast.stmt) -> bool:
    if isinstance(statement, ast.Pass):
        return True
    if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) \
            and statement.value.value is Ellipsis:
        return True
    return isinstance(statement, ast.Raise) and name_of(statement.exc) == "NotImplementedError"


def stub(function: ast.AST) -> bool:
    """본문이 docstring·pass·...·NotImplementedError뿐이면 참입니다. 아무 일도 하지 않는 함수입니다."""
    return all(placeholder(statement) for statement in statements(function))


def parameters(function: ast.AST, method: bool) -> list[str]:
    args = function.args
    ordered = [a.arg for a in args.posonlyargs + args.args]
    if method and ordered and not any(name_of(d) == "staticmethod" for d in function.decorator_list):
        ordered = ordered[1:]
    ordered += [a.arg for a in args.kwonlyargs]
    if args.vararg:
        ordered.append("*" + args.vararg.arg)
    if args.kwarg:
        ordered.append("**" + args.kwarg.arg)
    return ordered


def forwarded(function: ast.AST, method: bool) -> ast.Call | None:
    """받은 인자를 그대로 다른 호출 하나에 넘기기만 하면 그 호출을 돌려줍니다."""
    body = statements(function)
    if len(body) != 1 or not isinstance(body[0], (ast.Return, ast.Expr)):
        return None
    call = body[0].value
    if isinstance(call, ast.Await):
        call = call.value
    if not isinstance(call, ast.Call):
        return None
    passed = []
    for arg in call.args:
        if isinstance(arg, ast.Name):
            passed.append(arg.id)
        elif isinstance(arg, ast.Starred) and isinstance(arg.value, ast.Name):
            passed.append("*" + arg.value.id)
        else:
            return None
    for keyword in call.keywords:
        if keyword.arg is None and isinstance(keyword.value, ast.Name):
            passed.append("**" + keyword.value.id)
        elif isinstance(keyword.value, ast.Name) and keyword.value.id == keyword.arg:
            passed.append(keyword.arg)
        else:
            return None
    return call if sorted(passed) == sorted(parameters(function, method)) else None


def cohesion(node: ast.ClassDef) -> float | None:
    """TCC입니다. 같은 인스턴스 속성을 쓰는 메서드 쌍의 비율이며 메서드가 둘 미만이면 None입니다."""
    methods = [m for m in node.body if isinstance(m, FUNCTIONS)]
    names = {m.name for m in methods}
    used = []
    for method in methods:
        decorators = {name_of(d) for d in method.decorator_list}
        if method.name == "__init__" or decorators & {"staticmethod", "classmethod"}:
            continue
        args = method.args.posonlyargs + method.args.args
        if not args:
            continue
        own = args[0].arg
        used.append({n.attr for n in ast.walk(method)
                     if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == own} - names)
    if len(used) < 2:
        return None
    pairs = len(used) * (len(used) - 1) // 2
    connected = sum(1 for i in range(len(used)) for j in range(i + 1, len(used)) if used[i] & used[j])
    return round(connected / pairs, 3)


def start_line(node: ast.AST) -> int:
    return min([node.lineno, *(d.lineno for d in getattr(node, "decorator_list", []))])


def function_info(node: ast.AST, owner: str | None) -> dict:
    decorators = {name_of(d) for d in node.decorator_list}
    call = forwarded(node, owner is not None)
    return {"name": node.name, "qualname": f"{owner}.{node.name}" if owner else node.name, "class": owner,
            "line": start_line(node), "end_line": node.end_lineno, "lines": node.end_lineno - node.lineno + 1,
            "complexity": complexity(node), "stub": stub(node),
            "abstract_marker": bool(decorators & ABSTRACT_DECORATORS), "decorated": bool(node.decorator_list),
            "forwards_to": ast.unparse(call.func) if call else None}


def abstract(node: ast.ClassDef, methods: list, bases: list) -> bool:
    """ABC 상속·ABCMeta·추상 데코레이터·NotImplementedError만 던지는 메서드 가운데 하나라도 있으면 참입니다."""
    if "ABC" in bases:
        return True
    if any(k.arg == "metaclass" and name_of(k.value) == "ABCMeta" for k in node.keywords):
        return True
    if any({name_of(d) for d in m.decorator_list} & ABSTRACT_DECORATORS for m in methods):
        return True
    return any(stub(m) and any(isinstance(s, ast.Raise) for s in statements(m)) for m in methods)


def class_info(node: ast.ClassDef) -> dict:
    methods = [m for m in node.body if isinstance(m, FUNCTIONS)]
    bases = [name for name in map(name_of, node.bases) if name]
    others = [m for m in methods if m.name != "__init__"]
    return {"name": node.name, "line": start_line(node), "end_line": node.end_lineno,
            "decorated": bool(node.decorator_list), "bases": bases, "methods": len(methods),
            "wmc": sum(complexity(m) for m in methods), "tcc": cohesion(node),
            "abstract": abstract(node, methods, bases), "protocol": "Protocol" in bases,
            "wrapper": len(others) >= 2 and all(forwarded(m, True) is not None for m in others)}


def shape(source: str) -> dict:
    """모듈의 최상위 정의와 클래스·함수 측정값입니다. 구문 오류는 SyntaxError로 알립니다."""
    tree = ast.parse(source)
    functions, classes, top_level = [], [], {}
    exported = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets) \
                and isinstance(node.value, (ast.List, ast.Tuple)):
            exported |= {e.value for e in node.value.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)}
        if isinstance(node, FUNCTIONS):
            functions.append(function_info(node, None))
            top_level[node.name] = functions[-1]
        elif isinstance(node, ast.ClassDef):
            classes.append(class_info(node))
            top_level[node.name] = classes[-1]
            functions.extend(function_info(m, node.name) for m in node.body if isinstance(m, FUNCTIONS))
    return {"functions": functions, "classes": classes, "top_level": top_level, "exported": exported}
