#!/usr/bin/env python3
"""라벨이 붙은 글 묶음으로 신호별 오탐·검출 비율을 구한다. 엔진을 고친 뒤 다시 돌려 전후를 견주는 용도다.

입력은 JSONL이다. 한 줄에 {"id", "lang", "label": "human"|"ai", "source", "genre", "text"}.
출력은 (1) 언어·장르별 점수 분포와 AUROC, (2) 규칙·신호별 '사람 글에서 걸린 비율'과 'AI 글에서 걸린 비율'(Wilson 95% 구간)이다.
말뭉치는 이 저장소에 없다(KatFish, HC3, M4, 위키백과를 직접 내려받아 합친다. docs/research.md 10절).
이 도구는 글을 실행하지 않고 읽어서 통계만 낸다. 표준 라이브러리만 쓴다.

  python3 tools/evaluate.py corpus.jsonl [--out result.json] [--min-n 30] [--jobs 4]
"""
import argparse
import collections
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-smell-polish", "scripts"))

from ai_smell.detect import analyze  # noqa: E402


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def auroc(pos, neg):
    """pos(AI) 점수가 neg(사람)보다 높을 확률. 같으면 0.5."""
    if not pos or not neg:
        return None
    allv = sorted([(s, 1) for s in pos] + [(s, 0) for s in neg])
    rank, i, sum_pos = 0.0, 0, 0.0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        avg = (i + j) / 2 + 1
        sum_pos += avg * sum(1 for k in range(i, j + 1) if allv[k][1] == 1)
        i = j + 1
    return (sum_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


CATS_ALL = ("residue", "sycophancy", "markup", "placeholder", "puffery", "vocab", "structure", "hedging", "transition",
            "cohesion", "signpost", "attribution", "translationese", "emotion", "rhythm", "format")


def run_one(row):
    a = analyze(row["text"])
    fired = sorted({f.rule_id for f in a.findings if f.weight > 0 and not f.shadowed})
    return {"id": row["id"], "lang": row["lang"], "label": row["label"], "source": row.get("source", ""),
            "genre": row.get("genre", ""), "gen": row.get("gen", ""), "score": a.score, "units": a.units, "fired": fired,
            "cats": a.categories}


def summarize(results, min_n, group="genre"):
    groups = collections.defaultdict(list)
    for r in results:
        groups[(r["lang"], r.get(group, "") or "-")].append(r)
        groups[(r["lang"], "*")].append(r)
    out = {"groups": {}, "rules": {}}
    for key, rows in sorted(groups.items()):
        h = [r for r in rows if r["label"] == "human"]
        m = [r for r in rows if r["label"] == "ai"]
        if len(h) < 10 or len(m) < 10:
            continue
        out["groups"]["/".join(key)] = {
            "n_human": len(h), "n_ai": len(m),
            "mean_human": round(sum(r["score"] for r in h) / len(h), 1), "mean_ai": round(sum(r["score"] for r in m) / len(m), 1),
            "human_ge35": round(sum(1 for r in h if r["score"] >= 35) / len(h), 3),
            "ai_ge35": round(sum(1 for r in m if r["score"] >= 35) / len(m), 3),
            "auroc": round(auroc([r["score"] for r in m], [r["score"] for r in h]) or 0, 3)}
    cats = collections.defaultdict(lambda: {"human": [], "ai": []})
    for r in results:
        if r["lang"] in ("ko", "en"):
            for c in set(k for x in results[:0] for k in x) | set(r["cats"]) | set(CATS_ALL):
                cats[(r["lang"], c)][r["label"]].append(r["cats"].get(c, 0.0))
    out["categories"] = {}
    for (lang, c), v in sorted(cats.items()):
        if len(v["human"]) < 30 or len(v["ai"]) < 30:
            continue
        fh = sum(1 for x in v["human"] if x > 0) / len(v["human"])
        fa = sum(1 for x in v["ai"] if x > 0) / len(v["ai"])
        if fh == 0 and fa == 0:
            continue
        out["categories"][f"{c}|{lang}"] = {"fire_human": round(fh, 3), "fire_ai": round(fa, 3),
                                            "auroc": round(auroc(v["ai"], v["human"]) or 0, 3)}
    per_rule = collections.defaultdict(lambda: collections.Counter())
    totals = collections.Counter()
    for r in results:
        totals[(r["lang"], r["label"])] += 1
        for rid in r["fired"]:
            per_rule[(rid, r["lang"])][r["label"]] += 1
    for (rid, lang), c in per_rule.items():
        nh, nm = totals[(lang, "human")], totals[(lang, "ai")]
        if nh < min_n or nm < min_n:
            continue
        ph, pm = c["human"] / nh, c["ai"] / nm
        out["rules"][f"{rid}|{lang}"] = {
            "human": c["human"], "ai": c["ai"], "n_human": nh, "n_ai": nm, "p_human": round(ph, 3), "p_ai": round(pm, 3),
            "ci_human": [round(x, 3) for x in wilson(c["human"], nh)], "ci_ai": [round(x, 3) for x in wilson(c["ai"], nm)],
            "lift": round(pm / ph, 2) if ph > 0 else None}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("corpus")
    ap.add_argument("--out")
    ap.add_argument("--min-n", type=int, default=30, help="언어마다 사람·AI 글이 이만큼 있을 때만 규칙 통계를 낸다")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--limit", type=int, default=0, help="앞에서 N건만(빠른 시험)")
    ap.add_argument("--match", choices=("genre", "all"), default="genre",
                    help="--group gen에서 사람 글을 같은 장르로만 견줄지(genre), 같은 언어 전체로 견줄지(all)")
    ap.add_argument("--group", choices=("genre", "gen", "source"), default="genre",
                    help="묶는 기준. gen이면 AI 글은 생성기 이름별로, 사람 글은 같은 언어의 사람 글 전체와 견준다")
    args = ap.parse_args()
    rows = []
    with open(args.corpus, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    if args.limit:
        rows = rows[:args.limit]
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        results = list(ex.map(run_one, rows, chunksize=64))
    if args.group == "gen":                      # 생성기별 비교: 사람 글은 모든 생성기 묶음에 같이 넣는다
        humans = [r for r in results if r["label"] == "human"]
        by = collections.defaultdict(list)
        for r in results:
            if r["label"] == "ai":
                by[(r["lang"], r["gen"] or "-")].append(r)
        rows_out = []
        for (lang, g), ai_rows in by.items():
            genres = {r["genre"] for r in ai_rows}          # 기본은 같은 영역의 사람 글과만 견준다
            hs = [dict(r, gen=g) for r in humans if r["lang"] == lang and (args.match == "all" or r["genre"] in genres)]
            rows_out += [dict(r, gen=g) for r in ai_rows] + hs
        res = summarize(rows_out, args.min_n, "gen")
    else:
        res = summarize(results, args.min_n, args.group)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"items": results, **res}, fh, ensure_ascii=False)
    print("언어/장르      사람n   AI n  사람평균 AI평균  사람>=35 AI>=35  AUROC")
    for k, v in res["groups"].items():
        print(f"{k:14} {v['n_human']:6} {v['n_ai']:6} {v['mean_human']:7} {v['mean_ai']:7} {v['human_ge35']:8.1%} {v['ai_ge35']:7.1%} {v['auroc']:6}")
    print("\n범주별(점수 기여 단독 AUROC, 걸린 비율):")
    for k, v in res["categories"].items():
        print(f"  {k:22} 사람 {v['fire_human']:6.1%} AI {v['fire_ai']:6.1%}  AUROC {v['auroc']}")
    print("\n규칙별(사람 글에서 3% 이상 걸린 것, 오탐 후보):")
    rows_ = sorted(((k, v) for k, v in res["rules"].items() if v["p_human"] >= 0.03), key=lambda kv: -kv[1]["p_human"])
    for k, v in rows_[:40]:
        print(f"  {k:42} 사람 {v['p_human']:5.1%} {tuple(v['ci_human'])}  AI {v['p_ai']:5.1%}  lift {v['lift']}")


if __name__ == "__main__":
    main()
