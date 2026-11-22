"""윤문이 필자에게 없던 것을 주입했는지 보는 표지. 윤문기가 '사람 같게' 만들려고 지어 넣기 쉬운 것들이다.

conorbronsdon/avoid-ai-writing의 'Never inject these' 목록(지어낸 화자의 관점, 만들어 낸 걸림돌, 억지 반론, 연출된 솔직함,
대시 연출, 쪼개기, 지어낸 구체값)을 옮겼다. 쪼개기는 cohesion.py가, 지어낸 구체값은 verify.py가 이미 본다.
verify는 원문과 윤문본의 개수를 견주고, 윤문본이 더 많을 때만 알린다(원문에 이미 있던 것은 필자의 문체다).
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List

KINDS_KO = {"perspective": "필자의 관점·경험", "stakes": "만들어 낸 중요성", "contrarian": "억지 반론",
            "candor": "연출된 솔직함", "props": "극적 장치"}
KINDS_EN = {"perspective": "speaker perspective or experience", "stakes": "manufactured stakes",
            "contrarian": "forced contrarianism", "candor": "performed candor", "props": "dramatic props"}

_P = {
    "perspective": re.compile(
        r"\b(?:in my experience|i['’]ve seen (?:this|it|that)|i['’]ll admit|i have to admit|i can tell you|"
        r"in my (?:view|opinion)|personally,? i|i['’]ve (?:found|learned|noticed) that)\b|"
        r"제\s*경험(?:상|으로는)|제가\s*(?:보기에는|겪어\s*보니|써\s*보니)|개인적으로(?:는)?|제\s*생각(?:에는|으로는)", re.I),
    "stakes": re.compile(
        r"\b(?:now more than ever|the stakes have never been higher|in a world where|"
        r"in today['’]s (?:fast-paced|digital|ever-changing) world)\b|그\s*어느\s*때보다|지금처럼\s*중요한\s*적은\s*없", re.I),
    "contrarian": re.compile(
        r"\beveryone (?:says|thinks|believes)\b[^.!?\n]{1,60}\b(?:but|however)\b|"
        r"\bthe conventional wisdom is (?:backwards|wrong)\b|\bthey(?:['’]re| are) (?:all )?wrong\b|"
        r"다들\s*[^.!?\n]{1,30}(?:라고|이라고)\s*(?:하지만|말하지만)|통념과\s*달리", re.I),
    "candor": re.compile(
        r"\b(?:let['’]s be honest|real talk|to be fully transparent|i want to be upfront|honestly\?)\b|"
        r"솔직하게\s*말씀드리면|솔직히\s*말(?:하면|해서)", re.I),
    "props": re.compile(
        r"\b(?:the (?:catch|kicker|twist|punchline)\?|plot twist:|let that sink in|read that again|sit with that)|"
        r"\*(?:checks notes|chef['’]s kiss|mic drop)\*", re.I),
}


def counts(text: str) -> Counter:
    return Counter({k: len(p.findall(text)) for k, p in _P.items()})


def added(original: str, revised: str) -> Dict[str, int]:
    """윤문본에서 원문보다 늘어난 종류와 늘어난 개수."""
    a, b = counts(original), counts(revised)
    return {k: b[k] - a[k] for k in _P if b[k] > a[k]}


def message(extra: Dict[str, int], ui: str = "ko") -> str:
    names: List[str] = [(KINDS_KO if ui == "ko" else KINDS_EN)[k] for k in extra]
    if ui == "ko":
        return ("원문에 없던 " + ", ".join(names) + " 표지가 생겼다. 필자가 하지 않은 말(경험, 의견, 반전, 솔직함)을 "
                "지어 넣지 않는다. 필자에게 묻거나 뺀다.")
    return ("Markers absent from the original appeared: " + ", ".join(names) + ". Do not invent the writer's "
            "experience, opinion, reversal or candor; ask the writer or remove them.")
