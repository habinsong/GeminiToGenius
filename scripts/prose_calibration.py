#!/usr/bin/env python3
"""문체 점수가 사람 글과 LLM 글을 얼마나 가르는지 잽니다. 배포하지 않는 개발용 도구입니다.

KatFish(https://github.com/Shinwoo-Park/katfishnet)의 katfish_dataset 폴더를 주면 갈래마다 짝수 번째 글은
보정용, 홀수 번째 글은 확인용으로 나눠 AUC와 등급 분포를 JSON으로 출력합니다. JSONL만 읽고 pickle은 열지 않습니다.
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
from gtg.prose_score import UNIT, grade, score  # noqa: E402


GENRES = {"essay": "general", "abstract": "academic", "poetry": "literary"}


def auc(machine: list[float], human: list[float]) -> float:
    """LLM 글의 감점 밀도가 사람 글보다 클 확률입니다. 같으면 반으로 셉니다."""
    wins = sum(1.0 if m > h else 0.5 if m == h else 0.0 for m in machine for h in human)
    return round(wins / (len(machine) * len(human)), 3)


def rows(folder: Path, genre: str) -> list[dict]:
    with (folder / f"{genre}.jsonl").open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def genre_report(folder: Path, genre: str, register: str) -> dict:
    density = {"calibration": defaultdict(list), "holdout": defaultdict(list)}
    values, models = defaultdict(list), defaultdict(list)
    for position, row in enumerate(rows(folder, genre)):
        side = "human" if row["written_by"] == "human" else "llm"
        found, measure = examine("text.md", row["text"], register)
        result = score(found, measure["units"])
        half = "calibration" if position % 2 == 0 else "holdout"
        density[half][side].append(result["penalty"] / max(1.0, measure["units"] / UNIT))
        values[side].append(result["value"])
        models[row["written_by"]].append(result["value"])
    return {
        "register": register,
        "auc": {half: auc(sides["llm"], sides["human"]) for half, sides in density.items()},
        "grades": {side: dict(sorted(Counter(grade(v) for v in items).items())) for side, items in values.items()},
        "median_score": {name: statistics.median(items) for name, items in sorted(models.items())},
        "texts": {side: len(items) for side, items in values.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True, help="KatFish의 katfish_dataset 폴더입니다.")
    args = parser.parse_args()
    report = {genre: genre_report(args.dataset, genre, register) for genre, register in GENRES.items()}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
