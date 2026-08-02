#!/usr/bin/env python3
"""Check the required design, implementation, and verification plan contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PLAN_FILES = ("design-plan.md", "implementation-plan.md", "verification-plan.md")
SECTION_PATTERNS = {
    "design-plan.md": ("goal|목표", "user|사용자", "task|행동|작업", "content hierarchy|정보 위계|콘텐츠 위계|information architecture|구조", "route|page|경로|페이지", "loading|empty|error|success|disabled|selected|상태", "responsive|mobile|320|반응형|모바일", "motion|animation|애니메이션|움직임", "reduced motion|prefers-reduced-motion|감속", "accessib|접근성|focus|키보드", "evidence|근거|source|출처"),
    "implementation-plan.md": ("file|파일|변경 범위|scope", "responsib|책임|boundary|경계|god object", "state|data flow|상태|데이터 흐름", "route|page|경로|페이지", "dependency|의존|interface|계약", "step|순서|단계|command|명령", "rollback|복구|risk|위험"),
    "verification-plan.md": ("command|명령|검증 절차|check", "320|mobile|좁은|모바일", "1280|desktop|wide|넓은|데스크톱", "keyboard|focus|키보드|포커스", "reduced motion|prefers-reduced-motion|감속", "overflow|잘림|스크롤", "performance|inp|cls|성능", "evidence|screenshot|스크린샷|증거", "pass|fail|통과|실패|expected|기대"),
}


def check(root: Path, require_multi_page: bool) -> dict:
    failures: list[str] = []
    texts: dict[str, str] = {}
    for name in PLAN_FILES:
        path = root / "docs" / "plans" / name
        if not path.is_file():
            failures.append(f"missing:{path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8")
        texts[name] = text
        if not text.strip():
            failures.append(f"empty:{path.relative_to(root)}")
        for index, pattern in enumerate(SECTION_PATTERNS[name], start=1):
            if not re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                failures.append(f"section:{name}:{index}")
    design = texts.get("design-plan.md", "")
    route_count = len(re.findall(r"^\s*(?:[-*]\s*)?(?:route|page|경로|페이지)\s*[:：]", design, re.IGNORECASE | re.MULTILINE))
    if require_multi_page and route_count < 2:
        failures.append("routes:at-least-two")
    result = {"ok": not failures, "root": str(root), "routes": route_count, "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--require-multi-page", action="store_true")
    args = parser.parse_args()
    try:
        result = check(Path(args.root).expanduser().resolve(), args.require_multi_page)
    except (OSError, UnicodeDecodeError) as error:
        print(json.dumps({"ok": False, "failures": [str(error)]}, ensure_ascii=False))
        return 1
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
