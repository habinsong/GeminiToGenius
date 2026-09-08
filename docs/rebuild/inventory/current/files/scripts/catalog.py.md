# `scripts/catalog.py`

- 형식: `100644`
- 바이트: 8438
- SHA-256: `d45943c59007e9190dbefe71ec6c5a894f272477e260b37ff37e126c2561e0e3`
- 인코딩: `utf-8`

````
#!/usr/bin/env python3
"""저장소 파일 전체의 원문과 해시를 문서화하고 변경 누락을 검사합니다."""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess


OUTPUT = "docs/rebuild/inventory"
SENSITIVE_DIRS = {".ssh", ".aws", ".kube"}


def generated(name: str) -> bool:
    return any(name.startswith(OUTPUT + "/" + part + "/") for part in ("baseline", "current"))


def sensitive(name: str) -> bool:
    path = Path(name)
    parts = tuple(part.casefold() for part in path.parts)
    return (any(p in SENSITIVE_DIRS for p in parts)
            or any(a == ".config" and b == "gh" for a, b in zip(parts, parts[1:]))
            or any(part == ".env" or part.startswith(".env.") or Path(part).suffix in {".pem", ".key"}
                   or part in {"id_rsa", "id_ed25519"} for part in parts))


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args])


def source_files(root: Path, revision: str | None):
    if revision:
        for entry in git(root, "ls-tree", "-rz", revision).split(b"\0"):
            if not entry:
                continue
            header, raw_name = entry.split(b"\t", 1)
            mode, kind, oid = header.decode().split()
            name = os.fsdecode(raw_name)
            if generated(name):
                continue
            if sensitive(name):
                yield name, mode, None, "민감 경로: 내용 접근 제외"
            elif kind != "blob":
                yield name, mode, None, "외부 Git 하위 모듈: 내용 접근 제외"
            else:
                yield name, mode, git(root, "cat-file", "blob", oid), None
    else:
        names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
        for name in sorted(set(os.fsdecode(n) for n in names.split(b"\0") if n)):
            if generated(name):
                continue
            path = root / name
            if not path.exists() and not path.is_symlink():
                continue
            # 부모 심볼릭 링크도 따라가지 않습니다.
            if sensitive(name) or any(p.is_symlink() for p in path.parents if p != root):
                yield name, "", None, "민감 경로 또는 외부 링크: 내용 접근 제외"
                continue
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                yield name, "120000", os.fsencode(os.readlink(path)), None
            elif stat.S_ISREG(mode):
                yield name, "100755" if mode & 0o111 else "100644", path.read_bytes(), None
            else:
                yield name, "", None, "일반 파일 아님: 내용 접근 제외"


def symbols(name: str, text: str) -> list[dict]:
    if not name.endswith(".py"):
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return [{"name": node.name, "kind": type(node).__name__, "line": node.lineno,
             "end_line": node.end_lineno}
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]


def render(root: Path, revision: str | None = None) -> dict[str, bytes]:
    files = {}
    entries = []
    for name, mode, data, excluded in source_files(root, revision):
        item = {"path": name, "mode": mode}
        if excluded:
            item["excluded"] = excluded
            entries.append(item)
            continue
        digest = hashlib.sha256(data).hexdigest()
        item.update(bytes=len(data), sha256=digest)
        try:
            text = data.decode("utf-8")
            if "\0" in text:
                raise UnicodeError("binary")
            item.update(encoding="utf-8", lines=len(text.splitlines()), symbols=symbols(name, text))
            fence = "`" * max(3, max((len(m) + 1 for m in re.findall(r"`+", text)), default=3))
            body = f"{fence}\n{text}" + ("" if text.endswith("\n") else "\n") + f"{fence}\n"
            # 원문 코드 블록의 마지막 개행 표시를 복원할 때 사용할 메타데이터입니다.
            item["trailing_newline"] = text.endswith("\n")
        except UnicodeError:
            item.update(encoding="base64", lines=None, symbols=[])
            body = "```base64\n" + base64.encodebytes(data).decode("ascii") + "```\n"
        item["document"] = "files/" + name + ".md"
        intro = (f"# `{name}`\n\n- 형식: `{mode}`\n- 바이트: {len(data)}\n"
                 f"- SHA-256: `{digest}`\n- 인코딩: `{item['encoding']}`\n\n")
        if mode == "120000":
            intro += "심볼릭 링크의 대상 문자열입니다. 대상 파일을 중복 순회하지 않습니다.\n\n"
        files[item["document"]] = (intro + body).encode("utf-8")
        entries.append(item)
    manifest = {"schema_version": 1, "revision": revision, "files": sorted(entries, key=lambda i: i["path"]),
                "excluded_roots": {".git/": "Git 내부 데이터베이스", OUTPUT + "/baseline/": "기준 원본 생성 산출물",
                                   OUTPUT + "/current/": "현재 원본 생성 산출물"},
                "ignored_paths": "Git ignore 대상은 코드 목록에서 제외합니다. 로컬 관찰 목록은 별도 기록합니다."}
    if revision:
        # 이미 보존한 v1 기준 문서의 포맷도 재현합니다.
        manifest["excluded_roots"] = {".git/": "Git 내부 데이터베이스", OUTPUT + "/": "재귀 복제를 막기 위한 생성 산출물"}
        manifest["ignored_paths"] = []
    files["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    lines = ["# 전체 파일 목록", "", f"총 {len(entries)}개 경로. 원문 생략 없이 파일별로 기록합니다.", "",
             "바이너리는 Base64, 심볼릭 링크는 링크 문자열로 보존합니다. 민감 경로는 읽지 않고 제외 사유를 기록합니다.", "",
             "| 파일 | 바이트 | 코드·내용 |", "| --- | ---: | --- |"]
    for item in sorted(entries, key=lambda i: i["path"]):
        from urllib.parse import quote
        link = f"[원문]({quote(item['document'])})" if "document" in item else item["excluded"]
        lines.append(f"| `{item['path']}` | {item.get('bytes', '-')} | {link} |")
    footer = ("제외 범위와 ignored 파일명은 manifest.json에 명시합니다." if revision else
              "제외 범위는 manifest.json, 로컬 ignored 관찰은 상위 조사 문서에 명시합니다.")
    lines += ["", footer, ""]
    files["README.md"] = "\n".join(lines).encode()
    return files


def sync(root: Path, target: Path, revision: str | None, check: bool) -> list[str]:
    expected = render(root, revision)
    actual = {p.relative_to(target).as_posix(): p for p in target.rglob("*") if p.is_file()}
    differences = [name for name, data in expected.items()
                   if name not in actual or actual[name].read_bytes() != data]
    differences.extend(name for name in actual if name not in expected)
    if not check:
        for name in actual.keys() - expected.keys():
            actual[name].unlink()
        for name, data in expected.items():
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    return sorted(differences)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--baseline", metavar="REVISION")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    revision = git(root, "rev-parse", "--verify", args.baseline + "^{commit}").decode().strip() if args.baseline else None
    target = root / OUTPUT / ("baseline" if revision else "current")
    if revision and target.exists() and not args.check:
        parser.error("기준 원본은 덮어쓰지 않습니다. --check로 확인하세요.")
    differences = sync(root, target, revision, args.check)
    print(json.dumps({"ok": not differences if args.check else True, "checked": args.check,
                      "changed_documents": len(differences), "path": str(target)}, ensure_ascii=False))
    return int(args.check and bool(differences))


if __name__ == "__main__":
    raise SystemExit(main())
````
