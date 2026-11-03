"""윤문 전후 비교가 수치·인용·URL·코드·영문 표기의 보존과 고친 분량을 지키는지 확인합니다.

윤문 스킬이 요구하는 불변식(수치와 인용은 고치지 않고, 원문에 없던 사실을 보태지 않고, 새로 쓰지 않는다)을 모델의 자기 보고가
아니라 두 글의 직접 비교로 확인합니다. 읽기 좋게 만들려고 쓴 표기 변경(날짜 형식, 천 단위 쉼표, 문장 결합)은 막지 않습니다.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.prose import check
from gtg.prose_fidelity import canonical, compare, numbers, quotes, NUMBER


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ("2026년 11월 3일 기준으로 사용자 1,624명이 참여했다. 응답자의 73.5%는 만족한다고 답했다. "
            "담당자는 \"다음 분기에 다시 점검하겠다고 약속했다\"라고 말했다. 자세한 내용은 https://example.com/report 에서 볼 수 있다. "
            "설정은 `max_retries=3`으로 두었다. KatFish 자료를 썼다.")


def found(original, polished):
    summary, items = compare(original, polished, "doc.md")
    return summary, {item["id"]: item for item in items}


class PreservedFactsTests(unittest.TestCase):
    def test_reformatting_that_keeps_every_fact_passes(self):
        polished = ("2026-11-03 기준으로 사용자 1624명이 참여했고, 응답자의 73.5%가 만족한다고 답했다. "
                    "담당자는 \"다음 분기에 다시 점검하겠다고 약속했다\"라고 말했다. 자세한 내용은 https://example.com/report 에서 볼 수 있다. "
                    "설정은 `max_retries=3`으로 두었다. KatFish 자료를 썼다.")
        summary, items = found(ORIGINAL, polished)
        self.assertEqual(items, {})
        self.assertEqual(summary["numbers"], {"lost": [], "added": []})
        self.assertLess(summary["changed_share"], 0.3)

    def test_number_spellings_are_compared_by_value(self):
        for before, after in (("2026-11-03", "2026년 11월 3일"), ("1,624명", "1624명"), ("20퍼센트", "20%"), ("03월", "3월"),
                              ("3퍼센트포인트", "3%p")):
            with self.subTest(before=before):
                self.assertEqual(numbers(before), numbers(after))
        self.assertNotEqual(numbers("1,624"), numbers("1,642"))
        self.assertNotEqual(numbers("3.2.0"), numbers("3.2.1"), "버전의 마지막 자리가 바뀐 것도 놓치지 않습니다.")
        self.assertEqual(numbers("3,4,5번"), numbers("3, 4, 5번"), "나열한 숫자를 천 단위 쉼표로 오인하지 않습니다.")

    def test_list_and_heading_numbering_are_not_facts(self):
        listed = "1. 설치\n2. 설정\n\n## 3.1 실행\n\n본문입니다."
        prose = "설치하고 설정한 뒤 실행한다. 본문입니다."
        self.assertEqual(numbers(listed), numbers(prose))
        self.assertEqual(dict(numbers("## 2026 전망")), {"2026": 1}, "연도는 제목에 있어도 사실입니다.")


class LostAndInventedFactsTests(unittest.TestCase):
    def test_a_transposed_digit_is_both_a_lost_and_an_added_number_and_blocks(self):
        summary, items = found(ORIGINAL, ORIGINAL.replace("1,624", "1,642"))
        self.assertEqual(summary["numbers"], {"lost": ["1624"], "added": ["1642"]})
        self.assertEqual(items["fidelity-number-lost"]["severity"], "block")
        self.assertEqual(items["fidelity-number-added"]["severity"], "block")

    def test_a_dropped_statistic_blocks(self):
        summary, items = found(ORIGINAL, ORIGINAL.replace("73.5%는", "대다수는"))
        self.assertEqual(summary["numbers"]["lost"], ["73.5%"])
        self.assertEqual(items["fidelity-number-lost"]["severity"], "block")

    def test_small_whole_numbers_are_only_reviewed(self):
        """'세 가지'를 '3가지'로 쓰는 정도의 변화까지 막지는 않습니다. 퍼센트·소수·세 자리 이상은 사실이므로 막습니다."""
        before, after = "항목은 세 가지이고 2번 항목이 중요하다.", "항목은 3가지이고 4번 항목이 중요하다."
        _, items = found(before, after)
        self.assertEqual(items["fidelity-number-lost-minor"]["severity"], "review")
        self.assertEqual(items["fidelity-number-added-minor"]["severity"], "review")
        self.assertNotIn("fidelity-number-lost", items)
        self.assertNotIn("fidelity-number-added", items)

    def test_a_paraphrased_quote_blocks_but_a_dropped_scare_quote_does_not(self):
        _, items = found(ORIGINAL, ORIGINAL.replace("다음 분기에 다시 점검하겠다고 약속했다", "다음 분기에 점검할 예정이라고 밝혔다"))
        self.assertEqual(items["fidelity-quote-lost"]["severity"], "block")
        self.assertEqual(items["fidelity-quote-added"]["severity"], "review")
        scare_before = "이 기능은 \"편리\"하다. 설치는 쉽다. 값은 3이다."
        scare_after = "이 기능은 편리하다. 설치는 쉽다. 값은 3이다."
        self.assertEqual(found(scare_before, scare_after)[1], {}, "짧은 강조 따옴표는 문체 선택입니다.")
        self.assertEqual(quotes("“가나다라마바사아”와 「자차카타파하거너」"), quotes("\"가나다라마바사아\" 그리고 『자차카타파하거너』"))

    def test_a_changed_url_or_code_value_blocks(self):
        _, items = found(ORIGINAL, ORIGINAL.replace("example.com/report", "example.com/summary").replace("max_retries=3", "max_retries=5"))
        self.assertEqual(items["fidelity-literal-lost"]["severity"], "block")
        self.assertEqual(items["fidelity-literal-added"]["severity"], "review")
        fenced_before = "실행:\n\n```bash\nmake test\n```\n\n끝."
        _, items = found(fenced_before, fenced_before.replace("make test", "make check"))
        self.assertEqual(items["fidelity-literal-lost"]["severity"], "block", "코드 블록은 통째로 비교합니다.")
        self.assertEqual(found(fenced_before, fenced_before.replace("실행:", "이렇게 실행한다:"))[1], {})
        indented = "실행:\n\n  ```bash\n  make test\n  ```\n\n끝."
        _, items = found(indented, indented.replace("make test", "make check"))
        self.assertEqual(items["fidelity-literal-lost"]["severity"], "block", "들여쓴 코드 펜스도 코드 블록입니다.")

    def test_english_terms_are_compared_only_in_korean_documents(self):
        _, items = found(ORIGINAL, ORIGINAL.replace("KatFish 자료를 썼다", "카트피시 자료를 썼다"))
        self.assertEqual(items["fidelity-term-lost"]["severity"], "review")
        english_before = "The Kafka cluster handles 3 topics."
        self.assertNotIn("fidelity-term-lost", found(english_before, "The queue handles 3 topics.")[1])


class EditAmountTests(unittest.TestCase):
    @staticmethod
    def words(count, changed=0):
        return " ".join([f"바뀜{i}" if i < changed else f"단어{i}" for i in range(count)])

    def test_thresholds(self):
        original = self.words(60)
        summary, items = found(original, original)
        self.assertEqual(summary["changed_share"], 0)
        self.assertEqual(items["fidelity-unchanged"]["severity"], "review")
        self.assertEqual(found(original, self.words(60, 12))[1], {}, "20%는 정상 범위입니다.")
        self.assertEqual(found(original, self.words(60, 21))[1]["fidelity-over-edit"]["severity"], "review")
        strong = found(original, self.words(60, 36))[1]["fidelity-over-edit"]
        self.assertEqual(strong["severity"], "review", "절반을 넘는 것만으로는 막지 않고 지운 문장을 보고하게 합니다.")
        self.assertIn("보고", strong["hint"])
        nearly_new = found(original, self.words(60, 52))[1]["fidelity-over-edit"]
        self.assertEqual(nearly_new["severity"], "block")

    def test_short_texts_never_block_on_the_amount(self):
        original = self.words(20)
        self.assertEqual(found(original, self.words(20, 19))[1]["fidelity-over-edit"]["severity"], "review")

    def test_an_oversized_text_skips_only_the_ratio(self):
        big = " ".join(f"단어{i}" for i in range(7000))
        summary, items = found(big, big.replace("단어3 ", "바뀜 "))
        self.assertIsNone(summary["changed_share"])
        self.assertNotIn("fidelity-over-edit", items)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "draft.md").write_text(ORIGINAL + "\n", encoding="utf-8")
        (self.root / "good.md").write_text(
            "2026-11-03 기준으로 사용자 1624명이 참여했고, 응답자의 73.5%가 만족한다고 답했다. "
            "담당자는 \"다음 분기에 다시 점검하겠다고 약속했다\"라고 말했다. 자세한 내용은 https://example.com/report 에서 볼 수 있다. "
            "설정은 `max_retries=3`으로 두었다. KatFish 자료를 썼다.\n", encoding="utf-8")
        (self.root / "bad.md").write_text(ORIGINAL.replace("73.5%는", "대다수는") + "\n", encoding="utf-8")

    def test_the_gate_follows_the_comparison(self):
        good = check(self.root, ["good.md"], original="draft.md")
        self.assertTrue(good["passed"])
        self.assertEqual(good["fidelity"]["status"], "ok")
        bad = check(self.root, ["bad.md"], original="draft.md")
        self.assertFalse(bad["passed"])
        self.assertEqual(bad["blocking"], 1)
        self.assertIn("fidelity-number-lost", [f["id"] for f in bad["findings"]])
        self.assertIsNone(check(self.root, ["good.md"])["fidelity"], "원문을 주지 않으면 비교하지 않습니다.")

    def test_fidelity_findings_do_not_lower_the_style_score(self):
        plain = check(self.root, ["bad.md"])
        compared = check(self.root, ["bad.md"], original="draft.md")
        self.assertEqual(plain["score"], compared["score"])
        self.assertEqual(plain["files"][0]["score"], compared["files"][0]["score"])

    def test_unreadable_inputs_never_pass(self):
        missing = check(self.root, ["good.md"], original="nope.md")
        self.assertEqual(missing["fidelity"]["status"], "missing")
        self.assertFalse(missing["passed"])
        unreadable = check(self.root, ["nope.md"], original="draft.md")
        self.assertEqual(unreadable["fidelity"]["status"], "polished_unreadable")
        self.assertFalse(unreadable["passed"])
        (self.root / "empty.md").write_text("\n", encoding="utf-8")
        self.assertFalse(check(self.root, ["good.md"], original="empty.md")["passed"], "빈 원문은 비교할 수 없습니다.")

    def test_comparison_needs_exactly_one_polished_document(self):
        with self.assertRaises(ValueError):
            check(self.root, ["good.md", "bad.md"], original="draft.md")
        with self.assertRaises(ValueError):
            check(self.root, ["good.md"], texts=[("<text 1>", "다른 글")], original="draft.md")

    def test_cli_compares_a_file_against_its_draft(self):
        def run(name):
            process = subprocess.run([sys.executable, "-m", "gtg", "prose", name, "--original", "draft.md", "--workspace", str(self.root)],
                                     cwd=ROOT, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            return process.returncode, json.loads(process.stdout)

        code, report = run("good.md")
        self.assertEqual((code, report["fidelity"]["numbers"]), (0, {"lost": [], "added": []}))
        code, report = run("bad.md")
        self.assertEqual(code, 1)
        self.assertEqual(report["fidelity"]["numbers"]["lost"], ["73.5%"])


class NumberPatternTests(unittest.TestCase):
    def test_canonical_form(self):
        self.assertEqual([canonical(m) for m in NUMBER.finditer("1,624명 03월 73.5 % 3.2.0 20퍼센트")],
                         ["1624", "3", "73.5%", "3.2.0", "20%"])


if __name__ == "__main__":
    unittest.main()
