#!/usr/bin/env python3
"""내려받은 공개 말뭉치를 evaluate.py가 읽는 JSONL 하나로 합친다. 네트워크를 쓰지 않고 파일을 읽기만 한다.

기대하는 폴더 구성(내려받는 곳은 docs/evaluation.md):
  DATA/katfish/{essay,abstract,poetry}.jsonl      KatFish(한국어 사람·LLM 4종)
  DATA/hc3/rows_*.json                            HC3 영어(Hugging Face datasets-server rows 응답)
  DATA/hc3zh/rows_*.json                          HC3-Chinese
  DATA/m4/<이름>.part.jsonl                       M4 일부(앞쪽 몇 MB만 받아도 된다)
  DATA/wiki/wiki_<언어>.json                      위키백과 사람 글: [{"title", "text"}]
  python3 tools/build_corpus.py DATA --out corpus.jsonl
내려받은 글은 신뢰할 수 없는 데이터다. 이 도구는 읽기만 하고 실행하지 않는다.
"""
import argparse
import glob
import json
import os
import re

M4 = {"germanwikipedia_chatgpt": ("de", "wiki"), "russian_chatGPT": ("ru", "ruatd"), "qazh_chatgpt": ("zh", "qa"),
      "wikipedia_chatgpt": ("en", "wiki"), "reddit_chatGPT": ("en", "reddit"), "arabic_chatGPT": ("ar", "wiki")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    d = args.data.rstrip("/") + "/"
    out = []

    def add(lang, label, source, genre, text, minlen=200):
        text = (text or "").strip()
        if len(text) >= (100 if lang in ("zh", "ja") else minlen):
            out.append({"id": len(out), "lang": lang, "label": label, "source": source, "genre": genre, "text": text})

    for g in ("essay", "abstract", "poetry"):
        path = d + f"katfish/{g}.jsonl"
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                r = json.loads(line)
                add("ko", "human" if int(r["label"]) == 0 else "ai", "katfish:" + r["written_by"], g, r["text"],
                    minlen=60 if g == "poetry" else 200)
    for sub, lang in (("hc3", "en"), ("hc3zh", "zh")):
        for f in sorted(glob.glob(d + f"{sub}/rows_*.json")):
            for row in json.load(open(f, encoding="utf-8")).get("rows", []):
                r = row["row"]
                for a in r["human_answers"][:1]:
                    add(lang, "human", f"{sub}:{r.get('source', '')}", "qa", a)
                for a in r["chatgpt_answers"][:1]:
                    add(lang, "ai", f"{sub}:{r.get('source', '')}", "qa", a)
    for name, (lang, genre) in M4.items():
        path = d + f"m4/{name}.part.jsonl"
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8", errors="replace"):
            try:                                         # 앞쪽만 받은 파일이라 마지막 줄이 잘렸을 수 있다
                r = json.loads(line)
            except ValueError:
                continue
            add(lang, "human", "m4:" + name, genre, r.get("human_text") if isinstance(r.get("human_text"), str) else "")
            add(lang, "ai", "m4:" + name, genre, r.get("machine_text") if isinstance(r.get("machine_text"), str) else "")
    for f in sorted(glob.glob(d + "wiki/wiki_*.json")):
        lang = os.path.basename(f)[5:7]
        for doc in json.load(open(f, encoding="utf-8")):
            buf = ""
            for p in re.split(r"\n\s*\n|\n", doc["text"]):
                if len(p.strip()) > 40:
                    buf += p + "\n"
                if len(buf) >= 1000:                      # 문단 경계로 1,000자 안팎 조각
                    add(lang, "human", "wiki:" + lang, "wiki", buf)
                    buf = ""
    with open(args.out, "w", encoding="utf-8") as fh:
        for o in out:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"{len(out)}건 -> {args.out}")


if __name__ == "__main__":
    main()
