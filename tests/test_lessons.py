"""교훈 기록이 근거 없는 문장·숨은 문자·중복·무한 증가를 막고, 깨진 기록도 조용히 건너뛰는지 확인합니다."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg import lessons
from gtg.lessons import record, recent


ROOT = Path(__file__).resolve().parents[1]
TEXT = "sdk.py에는 export_rows가 없고 실제 함수는 write_rows(rows, path)입니다."


class LessonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "sdk.py").write_text("def write_rows(rows, path):\n    return path\n", encoding="utf-8")

    def test_lesson_needs_existing_evidence_inside_the_workspace(self):
        for evidence in ([], ["missing.py"], ["../sdk.py"], ["/etc/hostname"], ["sdk.py:0"], ["ftp://example.com/x"]):
            with self.subTest(evidence=evidence), self.assertRaises(ValueError):
                record(self.root, TEXT, evidence)
        result = record(self.root, TEXT, ["sdk.py:1", "https://docs.python.org/3/library/csv.html"])
        self.assertTrue(result["recorded"])
        self.assertEqual(result["lesson"]["evidence"], ["https://docs.python.org/3/library/csv.html", "sdk.py:1"])

    def test_symlinked_evidence_and_storage_are_refused(self):
        (self.root / "link.py").symlink_to(self.root / "sdk.py")
        with self.assertRaises(ValueError):
            record(self.root, TEXT, ["link.py"])
        (self.root / ".gtg").mkdir()
        (self.root / ".gtg/lessons.jsonl").symlink_to(self.root / "sdk.py")
        with self.assertRaises(ValueError):
            record(self.root, TEXT, ["sdk.py"])
        self.assertEqual(recent(self.root), [], "링크된 기록은 읽지 않습니다.")
        self.assertIn("write_rows", (self.root / "sdk.py").read_text(), "링크 대상 파일을 덮어쓰지 않습니다.")

    def test_text_must_be_one_visible_sentence_of_bounded_length(self):
        for text in ("짧음", "가" * 301, "보이지 않는​문자가 있는 교훈입니다 정말로", "제어\x07문자가 들어간 교훈 문장입니다"):
            with self.subTest(text=text[:12]), self.assertRaises(ValueError):
                record(self.root, text, ["sdk.py"])

    def test_duplicates_are_kept_once_regardless_of_case_and_spacing(self):
        first = record(self.root, TEXT, ["sdk.py"])
        again = record(self.root, "  " + TEXT.upper().replace(" ", "   ") + " ", ["sdk.py"])
        self.assertTrue(first["recorded"])
        self.assertFalse(again["recorded"])
        self.assertEqual(again["reason"], "duplicate")
        self.assertEqual(len(recent(self.root, 10)), 1)

    def test_storage_is_capped_and_newest_comes_first(self):
        for index in range(lessons.MAX_KEEP + 3):
            record(self.root, f"{index}번 교훈: sdk.py의 함수 이름을 다시 확인합니다.", ["sdk.py"])
        stored = (self.root / ".gtg/lessons.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(stored), lessons.MAX_KEEP)
        newest = recent(self.root, 2)
        self.assertTrue(newest[0]["text"].startswith(f"{lessons.MAX_KEEP + 2}번"))
        self.assertTrue(newest[1]["text"].startswith(f"{lessons.MAX_KEEP + 1}번"))
        texts = [json.loads(line)["text"] for line in stored]
        self.assertTrue(texts[0].startswith("3번 "), "가장 오래된 기록부터 지웁니다.")
        self.assertFalse(any(text.startswith(("0번 ", "1번 ", "2번 ")) for text in texts))

    def test_broken_lines_are_skipped_and_private_folder_is_ignored_by_git(self):
        record(self.root, TEXT, ["sdk.py"])
        with (self.root / ".gtg/lessons.jsonl").open("a", encoding="utf-8") as stream:
            stream.write("{깨진 줄\n[]\n{\"text\": 1}\n")
        self.assertEqual([item["text"] for item in recent(self.root)], [TEXT])
        self.assertEqual((self.root / ".gtg/.gitignore").read_text(), "*\n")
        self.assertEqual(oct((self.root / ".gtg/lessons.jsonl").stat().st_mode & 0o777), "0o600")

    def test_existing_gitignore_in_state_folder_is_preserved(self):
        (self.root / ".gtg").mkdir()
        (self.root / ".gtg/.gitignore").write_text("사용자 설정\n", encoding="utf-8")
        record(self.root, TEXT, ["sdk.py"])
        self.assertEqual((self.root / ".gtg/.gitignore").read_text(encoding="utf-8"), "사용자 설정\n")

    def test_cli_records_lists_and_rejects_missing_evidence(self):
        def run(*args):
            process = subprocess.run([sys.executable, "-m", "gtg", *args, "--workspace", str(self.root)],
                                     cwd=ROOT, capture_output=True, text=True,
                                     env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            return process.returncode, json.loads(process.stdout)

        code, output = run("lesson", "--text", TEXT, "--evidence", "sdk.py:1")
        self.assertEqual((code, output["recorded"]), (0, True))
        code, output = run("lessons")
        self.assertEqual((code, [item["text"] for item in output["lessons"]]), (0, [TEXT]))
        code, output = run("lesson", "--text", TEXT + " 근거 없음")
        self.assertEqual((code, output["ok"]), (1, False))
        code, output = run("lessons", "--limit", "0")
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
