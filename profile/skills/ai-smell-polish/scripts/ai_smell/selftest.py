"""설치 직후 돌리는 내장 시험. 외부 파일이나 네트워크가 필요 없다.

종료 코드 0이면 이 설치본에서 규칙, 점수, 교정, 대조, 명령줄이 모두 동작한다는 뜻이다.
(표본이 작고 직접 쓴 것이라, 통과한 뒤에도 윤문 품질은 글을 읽어 판단해야 한다.)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import List, Tuple

from .detect import analyze
from .fix import polish
from .model import VERSION
from .rules import load_rules
from .samples import AI_MID, AI_STRONG, CHOPPY, CONNECTED, GOLDEN, HUMAN, STAGED
from .verify import verify

Check = Tuple[str, bool, str]


def _rules() -> Check:
    rules = load_rules()
    ids = {r.id for r in rules}
    ko = sum(r.lang == "ko" for r in rules)
    en = sum(r.lang == "en" for r in rules)
    ok = len(ids) == len(rules) and ko >= 25 and en >= 60 and all(r.note for r in rules)
    return "규칙 로딩", ok, f"규칙 {len(rules)}개 (ko {ko}, en {en}), id 중복 없음"


def _scores() -> List[Check]:
    out: List[Check] = []
    for lang, text in AI_STRONG.items():
        s = analyze(text).score
        out.append((f"강한 AI풍 {lang} >= 60", s >= 60, f"점수 {s}"))
    for lang, text in AI_MID.items():
        s = analyze(text).score
        out.append((f"중간 AI풍 {lang} >= 30", s >= 30, f"점수 {s}"))
    for name, text in HUMAN.items():
        s = analyze(text).score
        out.append((f"사람 글 {name} < 8", s < 8, f"점수 {s}"))
    return out


def _cohesion() -> List[Check]:
    def cut(text: str) -> int:
        return sum(1 for f in analyze(text).findings if f.category == "cohesion" and not f.shadowed and f.weight > 0)
    missed = [k for k, t in CHOPPY.items() if cut(t) == 0]
    flagged = [k for k, t in CONNECTED.items() if cut(t) > 0]
    return [("끊긴 단문 표본을 8개 언어에서 연결 단절로 잡음", not missed, ", ".join(missed) or "이상 없음"),
            ("이어 쓴 표본은 연결 단절로 잡지 않음", not flagged, ", ".join(flagged) or "이상 없음")]


def _voice() -> List[Check]:
    from .rules import en_voice, ko_voice
    mine = {r.id for r in en_voice.RULES + ko_voice.RULES}
    weak = [k for k, t in STAGED.items()
            if len({f.rule_id for f in analyze(t).findings if f.rule_id in mine}) < 3]
    v = verify("The cache stores responses for 60 seconds.",
               "In my experience, the cache stores responses for 60 seconds. Now more than ever, that matters.")
    ok = any("관점" in m or "perspective" in m for _, m in v.messages)
    return [("연출형 표지 표본이 새 규칙 셋 이상에 걸림", not weak, ", ".join(weak) or "이상 없음"),
            ("대조 검증이 지어 넣은 관점·경험 표지를 알림", ok, v.status)]


def _golden() -> List[Check]:
    out: List[Check] = []
    for name, src, tier, want in GOLDEN:
        got = polish(src, tier=tier).text
        out.append((f"교정 정답 {name}", got == want, "일치" if got == want else f"기대 {want!r} / 실제 {got!r}"))
    return out


def _properties() -> List[Check]:
    out: List[Check] = []
    for tier in ("safe", "standard", "strong"):
        bad = []
        for key, text in list({**{f"strong-{k}": v for k, v in AI_STRONG.items()},
                               **{f"mid-{k}": v for k, v in AI_MID.items()}}.items()):
            once = polish(text, tier=tier)
            twice = polish(once.text, tier=tier)
            if twice.text != once.text:
                bad.append(f"{key}:멱등")
            if once.after.score > once.before.score:
                bad.append(f"{key}:점수상승")
            if verify(text, once.text).status == "FAIL":
                bad.append(f"{key}:사실훼손")
        out.append((f"교정 성질({tier}): 멱등, 점수 비상승, 사실 보존", not bad, ", ".join(bad) or "이상 없음"))
    changed = [n for n, t in HUMAN.items() if polish(t, tier="standard").text != t]
    out.append(("사람이 쓴 글은 standard 단계에서 그대로", not changed, ", ".join(changed) or "이상 없음"))
    v = verify("Revenue grew 38% in 2025.", "Revenue grew 83% in 2025.")
    out.append(("대조 검증이 숫자 변경을 FAIL로 잡음", v.status == "FAIL", v.status))
    v2 = verify("See https://a.example/x now.", "See the link now.")
    out.append(("대조 검증이 주소 누락을 FAIL로 잡음", v2.status == "FAIL", v2.status))
    return out


def _cli() -> Check:
    launcher = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai-smell")
    if not os.path.exists(launcher):
        return "명령줄 실행", True, "실행 파일 없음(패키지로 설치됨): 생략"
    proc = subprocess.run([sys.executable, "-I", launcher, "analyze", "--text", "Certainly! I hope this helps!",
                           "--format", "json"], capture_output=True, text=True, encoding="utf-8", timeout=60)
    ok = proc.returncode == 0 and '"score"' in proc.stdout
    return "명령줄 실행", ok, "정상" if ok else (proc.stderr or proc.stdout)[:200]


def collect() -> List[Check]:
    checks: List[Check] = [_rules()]
    for fn in (_scores, _cohesion, _voice, _golden, _properties):
        checks += fn()  # type: ignore[operator]
    checks.append(_cli())
    return checks


def run(fmt: str = "text") -> int:
    checks = collect()
    failed = [c for c in checks if not c[1]]
    if fmt == "json":
        sys.stdout.write(json.dumps({"version": VERSION, "ok": not failed, "passed": len(checks) - len(failed),
                                     "total": len(checks),
                                     "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks]},
                                    ensure_ascii=False, indent=2) + "\n")
    else:
        for name, ok, detail in checks:
            sys.stdout.write(f"{'통과' if ok else '실패'}  {name} — {detail}\n")
        sys.stdout.write(f"\nselftest {'통과' if not failed else '실패'}: {len(checks) - len(failed)}/{len(checks)}"
                         f" (ai-smell {VERSION})\n")
        if not failed:
            sys.stdout.write("이 시험은 동작 확인용이다. 윤문 품질은 글을 읽어 판단하고, 한계는 docs/limits.md에 적혀 있다.\n")
    return 0 if not failed else 1

