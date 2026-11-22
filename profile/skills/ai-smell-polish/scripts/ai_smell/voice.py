"""필자 문체 표본을 수치로 요약한다. 윤문이 필자의 목소리에 가까운지 볼 수 있게 프롬프트에 싣는다.

blader/humanizer와 avoid-ai-writing은 필자 표본이 있으면 표본이 일반 규칙보다 앞선다고 정한다(대시 비율까지 표본을 따른다).
이 요약은 점수에 들어가지 않는다. 표본이 짧으면(문장 8개 미만) 수치가 불안정하다고 알린다.
"""
from __future__ import annotations

import re
import statistics
from collections import Counter
from typing import Dict, List

from . import cohesion, linkers
from .analyzers import _register
from .textutil import count_units, mask, paragraph_spans, protected_spans, sentence_spans

_FIRST = re.compile(r"\b(?:i|we|my|our|me|us)\b|(?<![가-힣])(?:저는|제가|나는|내가|우리는|우리가|저희)", re.I)


def profile(text: str) -> Dict[str, object]:
    masked = mask(text, protected_spans(text))
    sents = sentence_spans(masked)
    paras = paragraph_spans(masked)
    body = [re.sub(r"\x00+", "X", masked[a:b]) for a, b in sents]
    out: Dict[str, object] = {"sentences": len(body), "units": count_units(masked)}
    if not body:
        return out
    lang = linkers.detect(" ".join(body))
    lens = sorted(linkers.length_units(t, lang) for t in body)
    n = len(body)
    q = lambda p: lens[min(n - 1, int(p * (n - 1) + 0.5))]  # noqa: E731
    out.update({
        "language": lang, "paragraphs": len(paras), "sentences_per_paragraph": round(n / max(len(paras), 1), 1),
        "length_median": q(0.5), "length_p10": q(0.1), "length_p90": q(0.9),
        "length_mean": round(statistics.mean(lens), 1),
        "short_share": round(sum(1 for x in lens if x <= linkers.SHORT.get(lang, 9)) / n, 2),
        "commas_per_sentence": round(sum(t.count(",") + t.count("，") + t.count("、") for t in body) / n, 2),
        "dashes_per_1000_units": round(1000 * len(re.findall("[—―]", masked)) / max(out["units"], 1), 1),
        "questions_share": round(sum(1 for t in body if t.rstrip().endswith(("?", "？"))) / n, 2),
        "exclamations_share": round(sum(1 for t in body if t.rstrip().endswith(("!", "！"))) / n, 2),
        "link_initial_share": round(sum(1 for t in body if linkers.lead_link(t, lang)) / n, 2),
        "first_person_per_100_sentences": round(100 * len(_FIRST.findall(masked)) / n, 1),
    })
    _, prof = cohesion.signals(masked, sents, paras, "general")
    out["bridge_ratio"] = prof.get("bridge_ratio")
    if lang == "ko":
        reg = Counter(_register(t) for t in body if len(re.findall(r"[가-힣]", t)) >= 6)
        tot = sum(reg.values()) or 1
        out["register"] = {k: round(v / tot, 2) for k, v in reg.items()}
        out["ending_forms"] = dict(Counter(cohesion._ko_ending(t) for t in body))
    out["reliable"] = n >= 8
    return out


def render(p: Dict[str, object], ui: str = "ko") -> str:
    if "language" not in p:
        return ""
    ko = ui == "ko"
    unit = ("어절" if p["language"] == "ko" else "글자" if p["language"] in ("ja", "zh") else "낱말") if ko else "units"
    lines: List[str] = []
    lines.append((f"문장 {p['sentences']}개, 문단당 {p['sentences_per_paragraph']}문장. 문장 길이 중앙 {p['length_median']}{unit}"
                  f"(10~90% 구간 {p['length_p10']}~{p['length_p90']}), 짧은 문장 비율 {p['short_share']:.0%}") if ko else
                 (f"{p['sentences']} sentences, {p['sentences_per_paragraph']} per paragraph. Length median {p['length_median']} "
                  f"{unit} (10th-90th: {p['length_p10']}-{p['length_p90']}), short-sentence share {p['short_share']:.0%}"))
    lines.append((f"문장당 쉼표 {p['commas_per_sentence']}, 줄표 1천 단위당 {p['dashes_per_1000_units']}, 의문문 "
                  f"{p['questions_share']:.0%}, 감탄문 {p['exclamations_share']:.0%}, 1인칭 100문장당 {p['first_person_per_100_sentences']}")
                 if ko else (f"Commas per sentence {p['commas_per_sentence']}, dashes per 1,000 units "
                             f"{p['dashes_per_1000_units']}, questions {p['questions_share']:.0%}, exclamations "
                             f"{p['exclamations_share']:.0%}, first person per 100 sentences {p['first_person_per_100_sentences']}"))
    br = p.get("bridge_ratio")
    lines.append((f"문장 첫머리 이어지는 말 비율 {p['link_initial_share']:.0%}" + (f", 문장 사이 이음 비율 {br:.0%}" if br is not None else ""))
                 if ko else (f"Sentences opening with a linking word {p['link_initial_share']:.0%}" +
                             (f", joins carrying a link {br:.0%}" if br is not None else "")))
    if "register" in p:
        lines.append("말투 " + ", ".join(f"{ {'polite': '합니다·해요체', 'plain': '한다체', 'other': '기타'}[k]} {v:.0%}"
                                      for k, v in p["register"].items()))  # type: ignore[union-attr]
    if not p.get("reliable"):
        lines.append("표본이 짧아(문장 8개 미만) 수치가 불안정하다." if ko else "The sample is short (under 8 sentences); the numbers are unstable.")
    return "\n".join(f"- {x}" for x in lines)
