#!/usr/bin/env python3
"""2024~26년 모델 글 말뭉치를 evaluate.py가 읽는 JSONL로 합친다. 네트워크를 쓰지 않고 읽기만 한다.

기대하는 폴더 구성(받는 곳은 docs/evaluation.md 2차 평가):
  DATA/artn/rows.json        artnitolog/llm-generated-texts   Hugging Face datasets-server rows의 row 목록
  DATA/beemo/rows.json       toloka/beemo
  DATA/dactyl/rows.json      ShantanuT01/DACTYL(test)
  DATA/hape/rows.json        browndw/human-ai-parallel-corpus-mini
  DATA/cringe/rows.json      av-codes/cringebench (model, question, answer)
  DATA/arena/<언어>_<오프셋>.json   lmarena-ai/arena-human-preference-140k를 {model, text, is_code}로 푼 것
  DATA/human2/{ko_wiki,ru_news,ja_wiki}.json   ChatGPT 이전 사람 글 [{"text"}]
  python3 tools/build_recent.py DATA --out recent.jsonl
출력 한 줄: {id, lang, label, source, genre, gen, text}. `gen`은 생성기 이름이고 사람 글은 "human"이다.
Arena 답변은 마크다운이 거의 없으면 genre가 chat-prose, 있으면 chat-md다.
(네이버 뉴스 요약 자료는 쉼표가 제거돼 있어 문장 부호 신호를 왜곡하므로 넣지 않는다.)
"""
import argparse
import glob
import json
import os
import re


def family(model):
    m = model.lower()
    for key, fam in (("claude", "claude"), ("gemini", "gemini"), ("gemma", "gemini"), ("grok", "grok"),
                     ("llama", "llama"), ("deepseek", "deepseek"), ("qwq", "deepseek"), ("qwen", "qwen")):
        if key in m:
            return fam
    return "gpt" if re.match(r"(gpt|chatgpt|o3|o4)", m) else "other"


def markdown_share(text):
    lines = [x for x in text.split("\n") if x.strip()]
    if not lines:
        return 1.0
    return sum(1 for x in lines if re.match(r"^\s*(#{1,6}\s|[-*+•]\s|\d+[.)]\s|\|)", x)) / len(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    d = args.data.rstrip("/") + "/"
    out = []

    def add(lang, label, source, genre, gen, text, minlen=200, maxlen=2500):
        text = (text if isinstance(text, str) else "").strip()
        if len(text) >= minlen:
            out.append({"id": len(out), "lang": lang, "label": label, "source": source, "genre": genre,
                        "gen": gen, "text": text[:maxlen]})

    def load(name):
        path = d + name
        return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []

    for r in load("artn/rows.json"):
        add("en", "human", "artn:human", r["dataset_name"], "human", r["human"])
        for m in ("GPT4 Turbo 2024-04-09", "GPT4 Omni", "Claude 3 Opus", "Llama3 70B", "Command R+"):
            add("en", "ai", "artn:" + m, r["dataset_name"], m, r.get(m))
    for r in load("beemo/rows.json"):
        add("en", "human", "beemo:human", r["category"], "human", r["human_output"], minlen=150)
        add("en", "ai", "beemo:" + r["model"], r["category"], r["model"].split("/")[-1], r["model_output"], minlen=150)
    for r in load("dactyl/rows.json"):
        if r["domain"] == "tweets":
            continue
        human = r["model"] == "human"
        gen = "human" if human else ("cpt-small" if "fine-tuned" in r["model"] else r["model"])
        add("en", "human" if human else "ai", "dactyl:" + gen, r["domain"], gen, r["text"])
    for r in load("hape/rows.json"):
        who, dom = r["doc_id"].split("_")[:2]
        gen = {"human": "human", "gpt4": "gpt-4o", "llama": "llama-3-8b"}[who]
        add("en", "human" if who == "human" else "ai", "hape:" + gen, dom, gen, r["text"])
    for r in load("cringe/rows.json"):
        if "haiku" not in r["question"].lower():
            add("en", "ai", "cringe:" + r["model"], "selfdesc", r["model"].split("/")[-1], r["answer"])
    for path in sorted(glob.glob(d + "arena/*_*.json")):
        if not re.match(r"^[a-z]{2}_\d+\.json$", os.path.basename(path)):
            continue                                     # 오류 응답이나 시험 파일은 건너뛴다
        lang = os.path.basename(path).split("_")[0]
        for r in json.load(open(path, encoding="utf-8")):
            t = r.get("text", "")
            if r.get("is_code") in (True, "True") or len(t) < 300:
                continue
            prose = markdown_share(t) == 0 and t.count("**") <= 2 * max(1, len(t) // 1000)
            form = "chat-prose" if prose else "chat-md"
            add(lang, "ai", "arena:" + r["model"], form, form + ":" + family(r["model"]), t, minlen=300)
    for name, lang in (("ko_wiki", "ko"), ("ru_news", "ru"), ("ja_wiki", "ja")):
        for r in load(f"human2/{name}.json"):
            add(lang, "human", name, "wiki" if name != "ru_news" else "news", "human", r["text"])
    with open(args.out, "w", encoding="utf-8") as fh:
        for o in out:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"{len(out)}건 -> {args.out}")


if __name__ == "__main__":
    main()
