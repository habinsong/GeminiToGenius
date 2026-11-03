"""변경 범위에 구조 기준을 적용해 차단·검토 신호를 만듭니다. 설계 품질의 판정이 아니라 확인할 신호입니다."""

from __future__ import annotations

from collections import Counter
import io
from pathlib import Path, PurePosixPath
import re
import tokenize

from .changes import EMPTY, collect, workspace_texts
from .code_shape import shape


CODE = {".py", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".kts", ".swift",
        ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".rb", ".php", ".scala", ".m", ".mm", ".sh", ".bash",
        ".lua", ".dart", ".vue", ".svelte"}
# 미완성 표식입니다. 대문자로 쓴 표식만 보므로 소문자 todo 목록 같은 이름은 잡지 않습니다.
WORDS = (r"(?:(?-i:\b(?:TODO|FIXME)\b)|\b(?:placeholder|stub) implementation\b|\bnot (?:yet )?implemented yet\b"
         r"|\bnot yet implemented\b|\bimplement (?:me|this|later)\b|구현\s?예정|추후\s?구현|나중에\s?구현|여기에\s?구현|임시\s?구현)")
COMMENT_WORDS = re.compile(WORDS, re.I)
# Python 밖에서는 주석 기호 뒤에 나온 표식만 봅니다. `placeholder="검색"` 같은 속성은 잡지 않습니다.
MARKER = re.compile(r"(?:#|//|/\*|<!--|^\s*\*|--\s)[^\n]*?" + WORDS, re.I)
# 이미 기준을 넘은 파일에서 이만큼 늘거나 새 최상위 정의가 생기면 기능을 쌓은 것으로 봅니다.
GROWTH = 30
LONG_FUNCTION = 80
# 분기·불리언 연산자·컴프리헨션 조건을 셉니다. radon 등급 D(21) 이상만 검토 신호로 알립니다.
COMPLEX_FUNCTION = 20
# Lanza·Marinescu의 God Class 전략(WMC 매우 높음·TCC 3분의 1 미만)을 Java 기준값으로 옮겼습니다. 검토 신호로만 씁니다.
GOD_WMC = 47
LOW_COHESION = 1 / 3
WORD = re.compile(r"\w+")
CLASS_BASES = re.compile(r"\bclass\s+\w+\s*\(([^)]*)\)")
LIMITATIONS = ("휴리스틱 신호입니다. 통과가 좋은 설계를 증명하지 않고 검토 신호가 결함을 뜻하지도 않습니다. "
               "Python 외 언어는 줄 수와 주석 표식만 봅니다. 문자열로 조합한 동적 호출과 다른 저장소의 구현은 찾지 못합니다.")


def finding(kind: str, severity: str, path: str, line: int | None, detail: str, symbol: str | None = None,
            **measure) -> dict:
    return {"kind": kind, "severity": severity, "path": path, "line": line, "symbol": symbol,
            "detail": detail, "measure": measure}


def is_test(name: str) -> bool:
    path = PurePosixPath(name)
    return (bool({"test", "tests", "__tests__", "spec", "specs"} & set(path.parts[:-1]))
            or path.name.startswith("test_") or path.name == "conftest.py"
            or path.stem.endswith(("_test", ".test", ".spec")))


def touched(item: dict, added: set[int]) -> bool:
    return any(item["line"] <= number <= item["end_line"] for number in added)


def python_comments(text: str) -> dict[int, str] | None:
    """Python 주석만 줄 번호별로 모읍니다. 문자열 속 `# TODO`는 주석이 아닙니다. 토큰화가 안 되면 None입니다."""
    comments = {}
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                comments[token.start[0]] = token.string
    except (tokenize.TokenError, SyntaxError):
        return None
    return comments


def markers(file: dict) -> list[dict]:
    lines = file["after"].splitlines()
    comments = python_comments(file["after"]) if file["path"].endswith(".py") else None
    found = []
    for number in sorted(file["added"]):
        if number > len(lines):
            continue
        hit = (COMMENT_WORDS.search(comments.get(number, "")) if comments is not None
               else MARKER.search(lines[number - 1]))
        if hit:
            found.append(finding("placeholder-marker", "block", file["path"], number,
                                 "새로 넣은 줄에 미완성 표식이 있습니다. 구현을 끝내거나, 남길 이유가 있으면 보고에 미완성으로 적으세요.",
                                 excerpt=lines[number - 1].strip()[:120]))
    return found


def size(file: dict, max_lines: int, new_definitions: bool) -> list[dict]:
    old = len(file["before"].splitlines()) if file["before"] is not None else None
    new = len(file["after"].splitlines())
    if new <= max_lines:
        return []
    if old is None:
        reason = "new"
    elif old <= max_lines:
        reason = "crossed"
    elif new - old >= GROWTH or new_definitions:
        reason = "grew"
    else:
        return []
    severity = "review" if is_test(file["path"]) else "block"
    return [finding("oversized-file", severity, file["path"], None,
                    f"파일이 {new}줄로 기준 {max_lines}줄을 넘었고 이번 변경으로 커졌습니다. 새 책임은 따로 모듈로 나누세요.",
                    before=old, after=new, reason=reason)]


def references(texts: dict[str, str] | None) -> dict | None:
    """작업공간 전체를 한 번만 훑어 식별자 등장 횟수와 클래스 상속 목록의 이름 횟수를 셉니다."""
    if texts is None:
        return None
    words, bases = Counter(), Counter()
    for text in texts.values():
        words.update(WORD.findall(text))
        for match in CLASS_BASES.finditer(text):
            bases.update(set(WORD.findall(match.group(1))))
    return {"words": words, "bases": bases}


def subclasses(refs: dict | None, name: str) -> int | None:
    return None if refs is None else refs["bases"][name]


def class_signals(path: str, info: dict, old: dict | None, added: set[int], refs, max_methods: int) -> list[dict]:
    found = []
    if not touched(info, added):
        return found
    new = old is None
    if info["methods"] > max_methods:
        grew = new or info["methods"] > old.get("methods", 0)
        found.append(finding("large-class", "block" if grew and not is_test(path) else "review", path, info["line"],
                             f"메서드가 {info['methods']}개로 기준 {max_methods}개를 넘습니다. 서로 다른 책임을 나누세요.",
                             info["name"], methods=info["methods"], grew=grew))
    if info["wmc"] >= GOD_WMC and info["tcc"] is not None and info["tcc"] < LOW_COHESION:
        found.append(finding("god-class-metrics", "review", path, info["line"],
                             "복잡도 합이 크고 메서드끼리 공유하는 속성이 적습니다. 관련 없는 책임이 한 클래스에 모였는지 확인하세요.",
                             info["name"], wmc=info["wmc"], tcc=info["tcc"]))
    if new and info["abstract"] and not info["protocol"]:
        count = subclasses(refs, info["name"])
        if count is not None and count <= 1:
            found.append(finding("single-implementation", "review", path, info["line"],
                                 f"추상 클래스의 구현이 {count}개입니다. 구현이 하나뿐이면 추상화 없이 구체 클래스를 쓰세요.",
                                 info["name"], implementations=count))
    if new and info["wrapper"]:
        found.append(finding("wrapper-class", "review", path, info["line"],
                             "모든 메서드가 받은 인자를 다른 호출에 그대로 넘깁니다. 감싼 객체를 직접 쓰면 되는지 확인하세요.",
                             info["name"]))
    return found


def function_signals(path: str, function: dict, classes: dict, added: set[int], refs) -> list[dict]:
    found = []
    if not touched(function, added):
        return found
    owner = classes.get(function["class"])
    if function["stub"] and not function["abstract_marker"] and not (owner and owner["protocol"]):
        base_class = owner is not None and owner["abstract"] and (subclasses(refs, owner["name"]) or 0) >= 1
        unknown = owner is not None and owner["abstract"] and refs is None
        if not base_class:
            found.append(finding("placeholder-body", "review" if unknown else "block", path, function["line"],
                                 "본문이 pass·...·NotImplementedError뿐인 함수입니다. 실제 동작을 구현하거나 함수를 지우세요.",
                                 function["qualname"]))
    if function["forwards_to"] and function["class"] is None and not function["decorated"]:
        found.append(finding("pass-through", "review", path, function["line"],
                             f"받은 인자를 그대로 {function['forwards_to']}에 넘기기만 합니다. 호출자가 원 함수를 직접 부르면 되는지 확인하세요.",
                             function["qualname"]))
    if function["lines"] > LONG_FUNCTION or function["complexity"] > COMPLEX_FUNCTION:
        found.append(finding("long-function", "review", path, function["line"],
                             f"함수가 {function['lines']}줄, 분기 복잡도 {function['complexity']}입니다. 나눌 수 있는지 확인하세요.",
                             function["qualname"], lines=function["lines"], complexity=function["complexity"]))
    return found


def python_signals(file: dict, refs, max_lines: int, max_methods: int) -> list[dict]:
    path = file["path"]
    try:
        after = shape(file["after"])
    except (SyntaxError, ValueError) as error:
        return [finding("syntax-error", "block", path, getattr(error, "lineno", None),
                        "구문 오류로 해석하지 못했습니다. 실행·빌드 전에 고치세요.")]
    try:
        before = shape(file["before"]) if file["before"] is not None else None
    except (SyntaxError, ValueError):
        before = None
    old = before["top_level"] if before else {}
    found = size(file, max_lines, bool(set(after["top_level"]) - set(old)))
    classes = {info["name"]: info for info in after["classes"]}
    for info in after["classes"]:
        found += class_signals(path, info, old.get(info["name"]), file["added"], refs, max_methods)
    for function in after["functions"]:
        found += function_signals(path, function, classes, file["added"], refs)
    if refs is not None and not is_test(path) and PurePosixPath(path).name != "__init__.py":
        for name, info in after["top_level"].items():
            if (name in old or name in after["exported"] or name == "main" or info.get("decorated")
                    or not touched(info, file["added"])):
                continue
            if refs["words"][name] <= 1:
                found.append(finding("unreferenced", "review", path, info["line"],
                                     "새 정의를 작업공간 어디서도 부르지 않습니다. 쓰지 않는 코드면 지우세요. "
                                     "문자열로 조합한 동적 호출은 찾지 못합니다.", name))
    return found


def validate(max_lines: int, max_methods: int):
    if type(max_lines) is not int or not 50 <= max_lines <= 100000:
        raise ValueError("파일 줄 수 기준은 50 이상 100000 이하의 정수여야 합니다.")
    if type(max_methods) is not int or not 3 <= max_methods <= 1000:
        raise ValueError("클래스 메서드 수 기준은 3 이상 1000 이하의 정수여야 합니다.")


def review(root: Path, base: str | None = None, paths: list[str] | None = None, *,
           max_lines: int = 400, max_methods: int = 20) -> dict:
    validate(max_lines, max_methods)
    scope = collect(root, base, paths or [], CODE)
    code = scope["files"]
    python = {f["path"] for f in code if f["path"].endswith(".py")}
    refs = references(workspace_texts(scope["root"], scope["git"], ".py")) if python else None
    findings = []
    for file in code:
        findings += markers(file)
        if file["path"] in python:
            findings += python_signals(file, refs, max_lines, max_methods)
        else:
            findings += size(file, max_lines, False)
    blocking = sum(1 for f in findings if f["severity"] == "block")
    baseline = ("none" if scope["base"] is None else "empty_repository" if scope["base"] == EMPTY
                else "git:" + scope["base"])
    return {"kind": "structure_check", "workspace": str(scope["root"]), "baseline": baseline,
            "checked_files": [f["path"] for f in code], "python_files": sorted(python),
            "structure_unanalyzed": [f["path"] for f in code if f["path"] not in python],
            "cross_file": "not_needed" if not python else "skipped_budget" if refs is None else "checked",
            "skipped": scope["skipped"], "limits": {"max_lines": max_lines, "max_methods": max_methods},
            "findings": findings, "blocking": blocking, "review": len(findings) - blocking,
            "passed": blocking == 0, "limitations": LIMITATIONS}
