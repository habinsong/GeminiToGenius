"""문체 검사 결과를 0~100점과 A~D 등급으로 바꿉니다.

점수는 찾은 신호를 글 분량으로 나눈 밀도입니다. 사람이 썼을 확률이 아니며, 검사 목록에 없는 버릇은 점수에
드러나지 않습니다. 사람 글에서 더 자주 나온 신호는 고칠 곳으로 알리기만 하고 감점하지 않습니다.
보정 자료와 한계는 docs/verification/3.3.0.md에 둡니다.
"""

from __future__ import annotations

import math


WEIGHTS = {"block": 3.0, "review": 1.0}
# 모든 갈래에서 점수에 넣지 않는 신호입니다. 고칠 곳일 수는 있어도 AI 문체의 근거는 아닙니다.
# register-mixed는 KatFish 에세이에서 사람 18.2%, LLM 5.1%였고, 맞춤법 오류는 사람 초안에만 흔합니다.
# 갈래별로 더 빼는 신호(시의 짧은 문장 연쇄 등)는 prose_registers의 Register.unscored에 있습니다.
UNSCORED = frozenset({"register-mixed", "ko-misspelling"})
# 문장 10개(목록·제목 줄 포함)마다 감점을 셉니다. 짧은 글은 10개로 봅니다.
UNIT = 10
# 문장 10개당 감점 1이면 92점, 3이면 79점, 6이면 62점, 10이면 45점입니다.
DECAY = 0.08
GRADES = ((90, "A"), (75, "B"), (60, "C"), (0, "D"))
LIMITATIONS = ("점수는 찾은 신호를 분량으로 나눈 밀도이며 AI가 썼을 확률이 아닙니다. 사람·LLM 한국어 글(KatFish)에서 "
               "에세이는 잘 갈랐고 초록은 그보다 약했으며 시는 약하게만 갈랐습니다. Gemini가 쓴 글로는 재 보지 않았습니다.")


def grade(value: int) -> str:
    return next(letter for floor, letter in GRADES if value >= floor)


def score(findings: list[dict], units: int, unscored: frozenset = UNSCORED) -> dict:
    """감점 내역이 붙은 점수입니다. 100점은 찾은 신호가 없다는 뜻이고 좋은 글이라는 보증은 아닙니다."""
    points = {}
    for item in findings:
        if item["id"] not in unscored:
            points[item["id"]] = points.get(item["id"], 0.0) + WEIGHTS[item["severity"]]
    penalty = sum(points.values())
    density = penalty / max(1.0, units / UNIT)
    value = round(100 * math.exp(-DECAY * density))
    deductions = sorted(points.items(), key=lambda item: (-item[1], item[0]))[:5]
    return {"value": value, "grade": grade(value), "penalty": penalty, "units": units,
            "deductions": [{"id": rule, "points": amount} for rule, amount in deductions]}
