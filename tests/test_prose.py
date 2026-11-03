"""문체 검사가 상투구는 차단하고, 사람도 쓰는 표현과 코드·URL은 오탐하지 않는지 확인합니다."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.prose import check, examine


ROOT = Path(__file__).resolve().parents[1]


def ids(text, severity=None):
    found, _ = examine("doc.md", text)
    return [f["id"] for f in found if severity in (None, f["severity"])]


class PhraseTests(unittest.TestCase):
    def test_korean_stock_phrases_block_and_their_lookalikes_pass(self):
        cases = {
            "결론적으로, 배포가 끝났습니다.": "ko-conclusion-signpost",
            "이 결과는 시사하는 바가 큽니다.": "ko-significance",
            "효과가 있다고 볼 수 있습니다.": "ko-hedged-copula",
            "이번 글에서는 설치 방법을 알아보겠습니다.": "ko-chatbot",
            "생성되어진 파일을 지웁니다.": "ko-double-passive",
            "개발의 새로운 지평을 엽니다.": "ko-hype-phrase",
        }
        for text, rule in cases.items():
            with self.subTest(text=text):
                self.assertIn(rule, ids(text, "block"))
        clean = ("논의를 결론적으로 정리하면 배포를 미룹니다. 로그에서 볼 수 있습니다. "
                 "설정되어 있는 값을 읽습니다. 패키지 무결성을 검사합니다. 새로운 지도를 그립니다.")
        self.assertEqual(ids(clean, "block"), [])
        self.assertNotIn("ko-overclaim", ids("패키지 무결성을 검사합니다."))
        self.assertIn("ko-overclaim", ids("무결점 코드입니다."))

    def test_english_stock_phrases_block_and_ordinary_words_pass(self):
        for text, rule in {
            "Let us delve into the cache.": "en-delve",
            "This is a testament to the design.": "en-cliche",
            "It's important to note that the cache expires.": "en-note-filler",
            "I hope this helps with the setup.": "en-chatbot",
            "In conclusion, the cache works.": "en-conclusion-signpost",
        }.items():
            with self.subTest(text=text):
                self.assertIn(rule, ids(text, "block"))
        self.assertEqual(ids("We deliver the conclusion of the test. The note is important.", "block"), [])

    def test_common_korean_connectors_are_flagged_only_when_they_pile_up(self):
        two = "데이터를 통해 확인합니다. 로그에 대해 설명합니다."
        three = two + " 설정을 통해 바꿉니다."
        self.assertNotIn("ko-translationese", ids(two))
        self.assertIn("ko-translationese", ids(three, "review"))
        self.assertNotIn("ko-translationese", ids(two + "\n\n설정을 통해 바꿉니다."), "문단이 다르면 따로 셉니다.")

    def test_code_urls_and_front_matter_are_not_prose(self):
        text = ("---\ndescription: delve into this\n---\n\n"
                "```\n결론적으로, 코드 안의 문장입니다.\n```\n\n"
                "나쁜 예는 `delve into`처럼 인라인 코드로 씁니다. 주소는 https://example.com/delve 입니다.\n")
        self.assertEqual(ids(text), [])

    def test_bold_dash_and_emoji_heading_are_format_reviews(self):
        self.assertIn("format-bold", ids("**하나** **둘** **셋** **넷** 굵게 씁니다."))
        self.assertNotIn("format-bold", ids("**하나** **둘** 굵게 씁니다."))
        self.assertIn("format-emoji-heading", ids("## 🚀 시작하기\n\n본문입니다."))
        body = "\n\n".join(f"문단 {i} — 덧붙인 말입니다." for i in range(4))
        self.assertIn("format-dash", ids(body))
        headings = "\n\n".join(f"# 3.{i} — 2026-10-0{i}" for i in range(4))
        self.assertNotIn("format-dash", ids(headings), "제목의 버전·날짜 줄표는 세지 않습니다.")


class RhythmTests(unittest.TestCase):
    def test_repeated_endings_are_flagged_from_five_in_a_row(self):
        four = " ".join(f"{word} 정리합니다." for word in ("설정을", "로그를", "결과를", "파일을"))
        self.assertNotIn("rhythm-same-ending", ids(four))
        self.assertIn("rhythm-same-ending", ids(four + " 값을 정리합니다."))

    def test_choppy_short_sentences_are_flagged_but_joined_text_is_not(self):
        choppy = "설치가 끝났습니다. 설정을 엽니다. 값을 바꿉니다. 저장합니다."
        joined = "설치가 끝나면 설정 파일을 열어 필요한 값을 바꾸고, 바꾼 내용을 저장한 뒤 서비스를 다시 시작합니다."
        self.assertIn("rhythm-choppy", ids(choppy))
        self.assertNotIn("rhythm-choppy", ids(joined))

    def test_lists_and_headings_are_not_counted_as_prose_rhythm(self):
        items = "\n".join(f"- {word} 정리합니다." for word in ("설정을", "로그를", "결과를", "파일을", "값을", "표를"))
        self.assertEqual([i for i in ids(items) if i.startswith("rhythm")], [])

    def test_uniform_documents_are_flagged_and_varied_ones_are_not(self):
        uniform = " ".join(f"{i}번 설정 값을 파일에 적어 둡니다." for i in range(16))
        self.assertIn("rhythm-monotone", ids(uniform))
        varied = uniform + (" 마지막으로 이 값들은 다음 배포 때 서버가 다시 읽으므로, 지금 바꾼 내용이 운영 환경에 언제"
                            " 반영되는지 배포 일정과 함께 확인해 두어야 나중에 원인을 찾느라 헤매지 않습니다.")
        self.assertNotIn("rhythm-monotone", ids(varied))


class FileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_unreadable_or_unsafe_paths_fail_the_check(self):
        (self.root / "image.md").write_bytes(b"\x00\x01binary")
        (self.root / ".env").write_text("SECRET=1")
        (self.root / "ok.md").write_text("배포를 마쳤고 시험도 통과했습니다.\n", encoding="utf-8")
        result = check(self.root, ["ok.md", "missing.md", "image.md", ".env", "../outside.md"])
        statuses = {f["path"]: f["status"] for f in result["files"]}
        self.assertEqual(statuses["ok.md"], "ok")
        self.assertEqual(statuses["missing.md"], "missing")
        self.assertEqual(statuses["image.md"], "binary_large_or_encoding")
        self.assertEqual(statuses[".env"], "denied")
        self.assertEqual(statuses["../outside.md"], "denied")
        self.assertFalse(result["passed"], "읽지 못한 문서가 있으면 통과로 보지 않습니다.")
        with self.assertRaises(ValueError):
            check(self.root, [])

    def test_cli_exit_code_follows_blocking_findings(self):
        (self.root / "bad.md").write_text("결론적으로, 끝났습니다.\n", encoding="utf-8")
        (self.root / "review.md").write_text("무결점 코드라고 적었습니다.\n", encoding="utf-8")

        def run(name):
            process = subprocess.run([sys.executable, "-m", "gtg", "prose", name, "--workspace", str(self.root)],
                                     cwd=ROOT, capture_output=True, text=True,
                                     env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            return process.returncode, json.loads(process.stdout)

        code, report = run("bad.md")
        self.assertEqual((code, report["blocking"]), (1, 1))
        self.assertEqual(report["findings"][0]["line"], 1)
        code, report = run("review.md")
        self.assertEqual((code, report["blocking"]), (0, 0))
        self.assertGreater(report["review"], 0)


class ShippedTextTests(unittest.TestCase):
    def test_shipped_instructions_contain_none_of_the_phrases_they_forbid(self):
        """모델이 읽는 규칙·스킬과 대표 안내문이 스스로 금지한 상투구를 쓰지 않게 합니다."""
        paths = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "profile").rglob("*.md"))
        paths += ["README.md", "docs/README.en.md", "docs/product/how-it-works.md", "docs/architecture/overview.md"]
        result = check(ROOT, paths)
        self.assertTrue(result["all_files_read"], result["files"])
        blocked = [(f["path"], f["line"], f["id"]) for f in result["findings"] if f["severity"] == "block"]
        self.assertEqual(blocked, [])


if __name__ == "__main__":
    unittest.main()
