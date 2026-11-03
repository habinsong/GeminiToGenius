#!/usr/bin/env python3
"""문체 검사 코드를 일부러 망가뜨린 변형을 만들어, 시험이 그 변형을 실패로 잡는지 확인합니다. 배포하지 않는 개발용 도구입니다.

시험이 통과한다는 사실만으로는 시험이 불변식을 지키는지 알 수 없습니다. 변형마다 소스의 한 곳을 바꾼 복사본에서 시험을 돌려
실패하면 잡힌 것(killed), 통과하면 살아남은 것(survived)입니다. 살아남은 변형은 시험이 비어 있거나 변형이 동치라는 뜻이므로
시험을 더하거나 목록에서 근거와 함께 뺍니다. 작업 트리는 건드리지 않고 임시 복사본에서만 고칩니다.

  python3 scripts/mutation_check.py              전체 변형을 돌리고 JSON을 냅니다. 살아남은 변형이 있으면 종료 코드 1입니다.
  python3 scripts/mutation_check.py --list       변형 목록과 각 변형이 지키는 불변식을 보입니다.
  python3 scripts/mutation_check.py --only fidelity   id에 이 글자가 든 변형만 돌립니다.

변형의 old는 파일에서 정확히 한 번 나와야 합니다. 코드가 바뀌어 대상을 못 찾으면 낡은 목록으로 통과시키지 않고 오류로 끝냅니다.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
COPY = ("gtg", "tests", "scripts", "evals/prose", "profile", "README.md", "docs/README.en.md", "docs/product",
        "docs/architecture", "VERSION")
TESTS = ("tests.test_prose", "tests.test_prose_registers", "tests.test_prose_score", "tests.test_prose_scaling",
         "tests.test_prose_fidelity", "tests.test_prose_input", "tests.test_prose_calibration")


def m(id_: str, file: str, old: str, new: str, guards: str) -> dict:
    return {"id": id_, "file": file, "old": old, "new": new, "guards": guards}


MUTATIONS = [
    # 길이에 맞춘 기준과 갈래별 예외
    m("scale-document-off", "gtg/prose.py", "units / DOCUMENT_REFERENCE if rule.scope", "1.0 if rule.scope",
      "문서 전체 횟수 기준이 글 분량에 비례해 늘어난다"),
    m("scale-paragraph-off", "gtg/prose.py", "sizes.get(key, 0) / PARAGRAPH_REFERENCE", "1.0",
      "문단 안 횟수 기준이 문단 문장 수에 비례해 늘어난다"),
    m("scale-verse-on", "gtg/prose.py", "    if verse or rule.severity == \"block\":\n        return rule.minimum",
      "    if rule.severity == \"block\":\n        return rule.minimum", "시는 길이로 기준을 늘리지 않는다"),
    m("paragraphs-merge-items", "gtg/prose.py", "            if current and ITEM.match(line):\n                groups.append(current)\n                current = []\n", "",
      "목록 항목과 표 행은 각각 따로 센다(서로 다른 불릿을 대구 연쇄로 차단하지 않는다)"),
    m("scale-block-rules", "gtg/prose.py", "    if verse or rule.severity == \"block\":\n        return rule.minimum", "    if verse:\n        return rule.minimum",
      "차단 규칙은 긴 문단에서도 기본 횟수로 막는다"),
    m("scale-never-lowers", "gtg/prose.py", "return max(rule.minimum, math.floor(", "return (math.floor(",
      "짧은 글은 규칙의 기본 횟수보다 기준을 낮추지 않는다"),
    m("scale-rounding", "gtg/prose.py", "* scale + 0.5))", "* scale + 1.5))", "환산은 반올림이다"),
    m("scale-threshold-strict", "gtg/prose.py", "len(items) >= required(", "len(items) > required(",
      "기준 횟수에 닿으면 걸린다"),
    m("verse-flag-lost", "gtg/prose_registers.py", "frozenset({\"rhythm-repeated-opening\", \"rhythm-choppy\"}), True)",
      "frozenset({\"rhythm-repeated-opening\", \"rhythm-choppy\"}), False)", "문학 갈래는 시로 분량을 센다"),
    # 분량 계산
    m("volume-always-by-line", "gtg/prose_rhythm.py", "by_line = not ended or (verse and verse_like(lines, run))",
      "by_line = True", "접어 쓴 산문은 줄이 아니라 문장으로 센다"),
    m("volume-verse-by-sentence", "gtg/prose_rhythm.py", "total += max(len(items), len(run)) if by_line else len(items)",
      "total += len(items)", "마침표 없는 시는 행 수로 센다"),
    m("volume-verse-any-width", "gtg/prose_rhythm.py", "return widths[len(widths) // 2] <= VERSE_LINE",
      "return widths[len(widths) // 2] > VERSE_LINE", "행이 긴 산문은 문학 갈래에서도 시로 세지 않는다"),
    m("volume-ignores-lists", "gtg/prose_rhythm.py", "total = sum(1 for line in lines if line.strip() and NOT_PROSE.match(line))",
      "total = 0", "제목·목록 줄도 분량이다"),
    # 점수와 갈래별 제외
    m("score-deducts-unscored", "gtg/prose_score.py", "if item[\"id\"] not in unscored:", "if True:",
      "점수에서 뺄 신호는 알리기만 한다"),
    m("score-block-weight", "gtg/prose_score.py", "WEIGHTS = {\"block\": 3.0, \"review\": 1.0}",
      "WEIGHTS = {\"block\": 2.0, \"review\": 1.0}", "차단 하나는 검토 셋과 같다"),
    m("score-decay", "gtg/prose_score.py", "DECAY = 0.08", "DECAY = 0.01", "점수는 신호 밀도에 따라 충분히 내려간다"),
    m("examine-drops-register-unscored", "gtg/prose.py", "\"unscored\": UNSCORED | settings.unscored}",
      "\"unscored\": UNSCORED}", "갈래마다 점수에서 빼는 신호가 다르다"),
    m("everyday-scores-openings", "gtg/prose_registers.py", "                         frozenset({\"rhythm-repeated-opening\"})),\n    # 문학",
      "                         frozenset()),\n    # 문학", "구어에서는 같은 첫머리 반복을 감점하지 않는다"),
    m("literary-scores-choppy", "gtg/prose_registers.py", "frozenset({\"rhythm-repeated-opening\", \"rhythm-choppy\"}), True)",
      "frozenset({\"rhythm-repeated-opening\"}), True)", "시의 짧은 문장 연쇄는 감점하지 않는다"),
    m("general-rules-dropped", "gtg/prose_registers.py", "\"general\": Register(frozenset(), {}, GENERAL,",
      "\"general\": Register(frozenset(), {}, (),", "일반 갈래 전용 규칙이 일반 갈래에서 켜진다"),
    m("general-rules-everywhere", "gtg/prose_registers.py", "\"academic\": Register(frozenset(), {\"ko-hedged-copula\": (\"review\", \"document\", 3)}, ACADEMIC,",
      "\"academic\": Register(frozenset(), {\"ko-hedged-copula\": (\"review\", \"document\", 3)}, ACADEMIC + GENERAL,",
      "일반 갈래 전용 규칙은 학술 갈래에서 꺼져 있다"),
    # 규칙의 강도
    m("hedge-blocks-again", "gtg/prose_patterns.py", "pattern(\"ko-hedged-copula\", \"review\", \"document\", 2,",
      "pattern(\"ko-hedged-copula\", \"block\", \"document\", 2,", "완곡은 차단이 아니라 반복될 때만 검토한다"),
    m("hedge-once", "gtg/prose_patterns.py", "pattern(\"ko-hedged-copula\", \"review\", \"document\", 2,",
      "pattern(\"ko-hedged-copula\", \"review\", \"document\", 1,", "완곡 한 번은 지적하지 않는다"),
    m("misspelling-blocks", "gtg/prose_patterns.py", "pattern(\"ko-misspelling\", \"review\", \"match\", 1,",
      "pattern(\"ko-misspelling\", \"block\", \"match\", 1,", "맞춤법 오류는 차단하지 않는다"),
    m("misspelling-drops-a-form", "gtg/prose_patterns.py", "r\"되요|됬|", "r\"됬|", "대표 맞춤법 오류를 찾는다"),
    m("misspelling-too-broad", "gtg/prose_patterns.py", "(?:할|갈|볼|줄|올|알|드릴|보낼|올릴|먹을|그럴|있을|없을)께요?",
      "[가-힣]께요?", "'5일께', '말께', '함께'를 오탐하지 않는다"),
    m("misspelling-scored", "gtg/prose_score.py", "UNSCORED = frozenset({\"register-mixed\", \"ko-misspelling\"})",
      "UNSCORED = frozenset({\"register-mixed\"})", "맞춤법 오류는 AI 문체 점수에 넣지 않는다"),
    m("mixed-register-scored", "gtg/prose_score.py", "UNSCORED = frozenset({\"register-mixed\", \"ko-misspelling\"})",
      "UNSCORED = frozenset({\"ko-misspelling\"})", "높임 혼용은 점수에 넣지 않는다"),
    # 입력과 판정
    m("empty-passes", "gtg/prose_input.py", "if status == \"ok\" and not text.strip():", "if False:",
      "빈 글은 통과가 아니라 실패다"),
    m("stdin-too-big", "gtg/prose_input.py", "if len(data) > MAX_BYTES or b\"\\0\" in data:", "if b\"\\0\" in data:",
      "표준 입력은 크기 상한이 있다"),
    m("stdin-binary", "gtg/prose_input.py", "if len(data) > MAX_BYTES or b\"\\0\" in data:", "if len(data) > MAX_BYTES:",
      "바이너리 입력은 거부한다"),
    m("given-empty-passes", "gtg/prose_input.py", "return (label, text, \"ok\") if text.strip() else (label, None, \"empty\")",
      "return (label, text, \"ok\")", "빈 표준 입력과 빈 --text도 통과가 아니라 실패다"),
    m("dash-stays-a-path", "gtg/__main__.py", "[path for path in args.paths if path != \"-\"]", "args.paths",
      "-는 파일이 아니라 표준 입력이다"),
    m("dash-ignored", "gtg/__main__.py", "if \"-\" in args.paths:", "if False:", "-를 주면 표준 입력을 읽는다"),
    m("original-needs-one", "gtg/prose.py", "if original is not None and len(paths) + len(texts) != 1:", "if False:",
      "윤문 비교는 문서 하나와만 쓴다"),
    m("fidelity-not-gating", "gtg/prose.py", "blocking = sum(1 for f in findings + extra if f[\"severity\"] == \"block\")",
      "blocking = sum(1 for f in findings if f[\"severity\"] == \"block\")", "충실도 차단이 통과 여부에 반영된다"),
    m("fidelity-status-ignored", "gtg/prose.py", " and (fidelity is None or fidelity[\"status\"] == \"ok\")", "",
      "읽지 못한 원문은 통과로 보지 않는다"),
    m("fidelity-lowers-score", "gtg/prose.py", "\"score\": score(findings, units, frozenset(unscored)) if scored else None",
      "\"score\": score(findings + extra, units, frozenset(unscored)) if scored else None", "충실도 발견은 문체 점수에 넣지 않는다"),
    # 윤문 충실도
    m("fidelity-block-share", "gtg/prose_fidelity.py", "BLOCK_SHARE = 0.80", "BLOCK_SHARE = 0.50",
      "절반을 넘는 것만으로는 막지 않고 거의 새로 쓴 글만 막는다"),
    m("fidelity-strong-share", "gtg/prose_fidelity.py", "STRONG_SHARE = 0.50", "STRONG_SHARE = 0.90",
      "절반을 넘으면 지운 문장을 보고하게 한다"),
    m("fidelity-review-share", "gtg/prose_fidelity.py", "REVIEW_SHARE = 0.30", "REVIEW_SHARE = 0.60",
      "30%를 넘으면 지나치게 손댔는지 알린다"),
    m("fidelity-short-text-blocks", "gtg/prose_fidelity.py", "MIN_WORDS_TO_BLOCK = 40", "MIN_WORDS_TO_BLOCK = 5",
      "짧은 글은 분량만으로 막지 않는다"),
    m("fidelity-all-numbers-significant", "gtg/prose_fidelity.py", "return \"%\" in token or \".\" in token or len(re.sub(r\"\\D\", \"\", token)) >= 3",
      "return True", "'세 가지'를 '3가지'로 쓴 정도는 막지 않는다"),
    m("fidelity-no-significant-numbers", "gtg/prose_fidelity.py", "return \"%\" in token or \".\" in token or len(re.sub(r\"\\D\", \"\", token)) >= 3",
      "return False", "퍼센트·소수·세 자리 수가 바뀌면 막는다"),
    m("fidelity-zero-padding", "gtg/prose_fidelity.py", "number = re.sub(r\"^0+(?=\\d)\", \"\", match.group(\"n\").replace(\",\", \"\"))",
      "number = match.group(\"n\").replace(\",\", \"\")", "03월과 3월은 같은 수다"),
    m("fidelity-thousands", "gtg/prose_fidelity.py", "number = re.sub(r\"^0+(?=\\d)\", \"\", match.group(\"n\").replace(\",\", \"\"))",
      "number = re.sub(r\"^0+(?=\\d)\", \"\", match.group(\"n\"))", "1,624와 1624는 같은 수다"),
    m("fidelity-list-numbers", "gtg/prose_fidelity.py", "    text = LIST_MARK.sub(\"\", text)\n", "",
      "목록·제목 번호는 사실이 아니다"),
    m("fidelity-quote-length", "gtg/prose_fidelity.py", "QUOTE_LENGTH = 8", "QUOTE_LENGTH = 1",
      "짧은 강조 따옴표는 인용문이 아니다"),
    m("fidelity-quote-blind", "gtg/prose_fidelity.py", "if len(re.sub(r\"\\s\", \"\", inner)) >= QUOTE_LENGTH:", "if False:",
      "인용문이 바뀌면 막는다"),
    m("fidelity-terms-in-english", "gtg/prose_fidelity.py", "korean = len(HANGUL.findall(old_text)) >= len(LATIN.findall(old_text))",
      "korean = True", "영문 표기 비교는 한국어 문서에서만 한다"),
    m("fidelity-literal-lenient", "gtg/prose_fidelity.py", "report(\"fidelity-literal-lost\", \"block\"", "report(\"fidelity-literal-lost\", \"review\"",
      "URL·코드가 바뀌면 막는다"),
    m("fidelity-lost-added-swapped", "gtg/prose_fidelity.py", "\"numbers\": (old_numbers - new_numbers, new_numbers - old_numbers)",
      "\"numbers\": (new_numbers - old_numbers, old_numbers - new_numbers)", "사라진 수치와 새로 생긴 수치를 구분한다"),
    m("fidelity-fence-unindented", "gtg/prose_fidelity.py", "FENCE = re.compile(r\"^[ \\t]{0,3}(?P<mark>", "FENCE = re.compile(r\"^(?P<mark>",
      "들여쓴 코드 펜스도 코드로 본다"),
    # 보정 스크립트
    m("auc-tie", "scripts/prose_calibration.py", "1.0 if m > h else 0.5 if m == h else 0.0", "1.0 if m > h else 0.0",
      "AUC에서 같은 값은 반으로 센다"),
    m("pass-boundary", "scripts/prose_calibration.py", "sum(v >= floor for v in values)", "sum(v > floor for v in values)",
      "기준 점수와 같은 점수는 통과다"),
    m("calibration-uses-llm-for-bodies", "scripts/prose_calibration.py", "row[\"written_by\"] == \"human\" and row.get(\"whole_paper_without_abstract\")",
      "row.get(\"whole_paper_without_abstract\")", "논문 본문 점검은 사람이 쓴 본문만 쓴다"),
]


def copy_project(root: Path, target: Path, names: tuple) -> None:
    for name in names:
        source, destination = root / name, target / name
        if not source.exists():
            raise FileNotFoundError(f"복사할 대상이 없습니다: {name}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(source, destination)


def passes(directory: Path, tests: tuple, timeout: int) -> str:
    """시험을 한 번 돌립니다. passed, failed, timeout 가운데 하나를 돌려줍니다. 첫 실패에서 멈춥니다."""
    try:
        process = subprocess.run([sys.executable, "-m", "unittest", "-f", *tests], cwd=directory, capture_output=True,
                                 timeout=timeout, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except subprocess.TimeoutExpired:
        return "timeout"
    return "passed" if process.returncode == 0 else "failed"


def run(root: Path, mutations: list, tests: tuple, copy: tuple, timeout: int = 180) -> dict:
    """변형마다 복사본의 소스를 고쳐 시험을 돌립니다. 기준 시험이 먼저 통과해야 하고, 대상이 없거나 둘 이상이면 오류입니다."""
    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        copy_project(root, work, copy)
        baseline = passes(work, tests, timeout)
        if baseline != "passed":
            raise RuntimeError(f"변형하지 않은 복사본에서 시험이 통과하지 않아 중단합니다: {baseline}")
        results = []
        for mutation in mutations:
            path = work / mutation["file"]
            original = path.read_text(encoding="utf-8")
            count = original.count(mutation["old"])
            if count != 1:
                raise ValueError(f"{mutation['id']}: {mutation['file']}에서 대상이 {count}번 나옵니다. 정확히 한 번이어야 합니다.")
            path.write_text(original.replace(mutation["old"], mutation["new"]), encoding="utf-8")
            try:
                outcome = passes(work, tests, timeout)
            finally:
                path.write_text(original, encoding="utf-8")
            results.append({"id": mutation["id"], "guards": mutation["guards"], "outcome": outcome,
                            "killed": outcome != "passed"})
    survived = [item["id"] for item in results if not item["killed"]]
    return {"baseline": "passed", "total": len(results), "killed": len(results) - len(survived), "survived": survived,
            "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="변형과 각 변형이 지키는 불변식을 보입니다.")
    parser.add_argument("--only", default="", help="id에 이 글자가 든 변형만 돌립니다.")
    parser.add_argument("--timeout", type=int, default=180, help="시험 한 번의 제한 시간(초)입니다.")
    args = parser.parse_args()
    chosen = [item for item in MUTATIONS if args.only in item["id"]]
    if args.list:
        print(json.dumps([{"id": item["id"], "file": item["file"], "guards": item["guards"]} for item in chosen],
                         ensure_ascii=False, indent=2))
        return 0
    report = run(ROOT, chosen, TESTS, COPY, args.timeout)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(bool(report["survived"]))


if __name__ == "__main__":
    raise SystemExit(main())
