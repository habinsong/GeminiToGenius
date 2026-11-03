#!/usr/bin/env python3
"""문체 점수가 사람 글과 LLM 글을 얼마나 가르는지 재고, 모델이 쓴 글을 같은 잣대로 잽니다. 배포하지 않는 개발용 도구입니다.

  --dataset DIR        KatFish(https://github.com/Shinwoo-Park/katfishnet)의 katfish_dataset 폴더로 AUC와 등급 분포를 냅니다.
                       갈래마다 짝수 번째 글은 보정용, 홀수 번째 글은 확인용입니다. --rules는 규칙별 출현율, --bodies는 사람이
                       쓴 논문 본문 전체(규칙을 고르는 데 쓰지 않은 긴 성인 학술 글)의 오탐을 더합니다.
  --outputs DIR        evals/prose/prompts.json의 프롬프트로 모델이 쓴 글(<프롬프트 id>.md)의 점수를 냅니다. 윤문 프롬프트는
                       원문과 견줘 수치·인용이 남았는지도 봅니다. --reference에 KatFish 집계를 주면 나란히 보여 줍니다.
  --export-prompts DIR 프롬프트를 <id>.prompt.txt로 내보냅니다. 모델은 호출하지 않으며, 호출 방법은 evals/prose/README.md에 있습니다.

JSONL과 텍스트만 읽고 pickle은 열지 않습니다. 결과는 JSON으로 표준 출력에 냅니다.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gtg.prose import examine  # noqa: E402
from gtg.prose_fidelity import compare  # noqa: E402
from gtg.prose_score import UNIT, grade, score  # noqa: E402


GENRES = {"essay": "general", "abstract": "academic", "poetry": "literary"}
FLOORS = (90, 75, 60)
PROMPTS = ROOT / "evals/prose/prompts.json"
SUFFIXES = (".md", ".txt")


def auc(machine: list[float], human: list[float]) -> float:
    """LLM 글의 감점 밀도가 사람 글보다 클 확률입니다. 같으면 반으로 셉니다."""
    wins = sum(1.0 if m > h else 0.5 if m == h else 0.0 for m in machine for h in human)
    return round(wins / (len(machine) * len(human)), 3)


def passing(values: list[int]) -> dict:
    """기준 점수별로 그 이상인 글의 비율입니다. --min-score를 고를 때 사람 글이 얼마나 걸리는지 보는 표입니다."""
    return {f"ge_{floor}": round(sum(v >= floor for v in values) / len(values), 3) if values else None for floor in FLOORS}


def rated(text: str, register: str) -> tuple[list[dict], dict, dict]:
    found, measure = examine("text.md", text, register)
    return found, measure, score(found, measure["units"], measure["unscored"])


def side_of(row: dict) -> str:
    return "human" if row["written_by"] == "human" else "llm"


def read_rows(folder: Path, genre: str) -> list[dict]:
    with (folder / f"{genre}.jsonl").open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def genre_report(rows: list[dict], register: str, with_rules: bool = False) -> dict:
    density = {"calibration": defaultdict(list), "holdout": defaultdict(list)}
    values, models = defaultdict(list), defaultdict(list)
    flagged = {"calibration": defaultdict(Counter), "holdout": defaultdict(Counter)}
    totals = {"calibration": Counter(), "holdout": Counter()}
    for position, row in enumerate(rows):
        side, half = side_of(row), "calibration" if position % 2 == 0 else "holdout"
        found, measure, result = rated(row["text"], register)
        density[half][side].append(result["penalty"] / max(1.0, measure["units"] / UNIT))
        values[side].append(result["value"])
        models[row["written_by"]].append(result["value"])
        totals[half][side] += 1
        for rule in {item["id"] for item in found}:
            flagged[half][rule][side] += 1
    report = {
        "register": register,
        "auc": {half: auc(sides["llm"], sides["human"]) for half, sides in density.items()},
        "grades": {side: dict(sorted(Counter(grade(v) for v in items).items())) for side, items in values.items()},
        "pass": {side: passing(items) for side, items in sorted(values.items())},
        "median_score": {name: statistics.median(items) for name, items in sorted(models.items())},
        "texts": {side: len(items) for side, items in values.items()},
    }
    if with_rules:
        report["rules"] = {
            rule: {half: {side: round(100 * flagged[half][rule][side] / max(1, totals[half][side]), 1)
                           for side in ("human", "llm")} for half in flagged}
            for rule in sorted(set().union(*(flagged[half] for half in flagged)))}
    return report


def bodies_report(rows: list[dict]) -> dict:
    """사람이 쓴 논문 본문 전체의 점수입니다. 규칙을 고르는 데 쓰지 않은 긴 성인 학술 글이라 오탐 점검에 씁니다."""
    values, fired, sizes = [], Counter(), []
    papers = [row for row in rows if row["written_by"] == "human" and row.get("whole_paper_without_abstract")]
    for row in papers:
        found, measure, result = rated(row["whole_paper_without_abstract"], "academic")
        values.append(result["value"])
        sizes.append(measure["units"])
        fired.update({item["id"] for item in found})
    return {"papers": len(papers), "mean_sentences": round(statistics.mean(sizes)) if sizes else None,
            "grades": dict(sorted(Counter(grade(v) for v in values).items())), "median_score": statistics.median(values) if values else None,
            "flagged_share": {rule: round(count / len(papers), 3) for rule, count in fired.most_common(12)}}


def read_prompts(path: Path) -> list[dict]:
    document = json.loads(path.read_text(encoding="utf-8"))
    prompts = document["prompts"]
    ids = [item["id"] for item in prompts]
    if len(set(ids)) != len(ids):
        raise ValueError("프롬프트 id가 겹칩니다.")
    return prompts


def output_text(directory: Path, prompt_id: str) -> str | None:
    for suffix in SUFFIXES:
        path = directory / f"{prompt_id}{suffix}"
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return None


def outputs_report(directory: Path, prompts: list[dict], label: str, reference: dict | None = None) -> dict:
    """프롬프트마다 모델 출력 하나를 재서 갈래별로 모읍니다. 윤문 프롬프트는 원문과도 견줍니다."""
    by_register = defaultdict(list)
    missing, details = [], []
    for prompt in prompts:
        text = output_text(directory, prompt["id"])
        if text is None or not text.strip():
            missing.append(prompt["id"])
            continue
        found, measure, result = rated(text, prompt["register"])
        row = {"id": prompt["id"], "register": prompt["register"], "score": result["value"], "grade": result["grade"],
               "blocking": sum(1 for item in found if item["severity"] == "block"),
               "rules": sorted({item["id"] for item in found})}
        if prompt.get("kind") == "polish":
            source = rated(prompt["source"], prompt["register"])[2]
            summary, extra = compare(prompt["source"], text, prompt["id"])
            row["source_score"] = source["value"]
            row["fidelity_blocking"] = sum(1 for item in extra if item["severity"] == "block")
            row["changed_share"] = summary["changed_share"]
        details.append(row)
        by_register[prompt["register"]].append(row)
    registers = {}
    for register, rows in sorted(by_register.items()):
        values = [row["score"] for row in rows]
        flagged = Counter(rule for row in rows for rule in row["rules"])
        registers[register] = {
            "outputs": len(rows), "median_score": statistics.median(values), "lowest_score": min(values),
            "grades": dict(sorted(Counter(row["grade"] for row in rows).items())), "pass": passing(values),
            "blocked_outputs": sum(1 for row in rows if row["blocking"]),
            "top_rules": {rule: round(count / len(rows), 3) for rule, count in flagged.most_common(8)}}
        polished = [row for row in rows if "source_score" in row]
        if polished:
            registers[register]["polish"] = {
                "outputs": len(polished),
                "median_source_score": statistics.median(row["source_score"] for row in polished),
                "median_polished_score": statistics.median(row["score"] for row in polished),
                "fidelity_blocked": sum(1 for row in polished if row["fidelity_blocking"])}
        genre = {value: key for key, value in GENRES.items()}.get(register)
        if reference and genre in reference:
            registers[register]["katfish"] = {"human_median": reference[genre]["median_score"].get("human"),
                                              "human_pass": reference[genre]["pass"]["human"],
                                              "llm_pass": reference[genre]["pass"]["llm"]}
    return {"label": label, "prompts": len(prompts), "missing": missing, "registers": registers, "details": details,
            "note": "KatFish 사람·LLM 글과 견주는 값이며 Gemini가 사람처럼 쓰는지의 증거가 아닙니다. 점수는 목록에 있는 버릇의 밀도입니다."}


def export_prompts(directory: Path, prompts: list[dict]) -> list[str]:
    """프롬프트를 파일로 씁니다. 윤문 프롬프트는 원문을 붙입니다. 모델은 호출하지 않습니다."""
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    for prompt in prompts:
        body = prompt["prompt"] + (f"\n\n{prompt['source']}\n" if prompt.get("kind") == "polish" else "\n")
        (directory / f"{prompt['id']}.prompt.txt").write_text(body, encoding="utf-8")
        written.append(prompt["id"])
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dataset", type=Path, help="KatFish의 katfish_dataset 폴더입니다.")
    modes.add_argument("--outputs", type=Path, help="모델 출력 폴더입니다. 파일 이름은 <프롬프트 id>.md입니다.")
    modes.add_argument("--export-prompts", type=Path, help="프롬프트를 내보낼 폴더입니다.")
    parser.add_argument("--rules", action="store_true", help="--dataset: 규칙별 출현율을 더합니다.")
    parser.add_argument("--bodies", action="store_true", help="--dataset: 사람이 쓴 논문 본문 전체의 오탐을 더합니다.")
    parser.add_argument("--prompts", type=Path, default=PROMPTS, help="프롬프트 정의 JSON입니다.")
    parser.add_argument("--label", default="unlabeled", help="--outputs: 결과에 적을 모델·조건 이름입니다.")
    parser.add_argument("--reference", type=Path, help="--outputs: --dataset 결과를 저장한 JSON입니다. 나란히 보여 줍니다.")
    args = parser.parse_args()
    if args.dataset:
        report = {genre: genre_report(read_rows(args.dataset, genre), register, args.rules) for genre, register in GENRES.items()}
        if args.bodies:
            report["abstract"]["bodies"] = bodies_report(read_rows(args.dataset, "abstract"))
    elif args.outputs:
        reference = json.loads(args.reference.read_text(encoding="utf-8")) if args.reference else None
        report = outputs_report(args.outputs, read_prompts(args.prompts), args.label, reference)
    else:
        report = {"exported": export_prompts(args.export_prompts, read_prompts(args.prompts))}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
