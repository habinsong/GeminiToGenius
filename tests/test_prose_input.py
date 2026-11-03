"""파일로 저장하지 않은 글(채팅 답변 등)을 표준 입력과 --text로 검사할 수 있고, 잘못된 입력은 통과가 아니라 실패로 끝나는지 확인합니다.

글쓰기 스킬은 채팅 답변과 완료 보고도 같은 기준으로 쓰라고 하지만, 3.2.0의 prose는 파일 경로만 받아 답변을 먼저 파일로
써야 했습니다.
"""

import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.prose import check
from gtg.prose_input import MAX_BYTES, given, load, read_stream


ROOT = Path(__file__).resolve().parents[1]
SLOP = "물론입니다. 도와드리겠습니다. 내일 3시에 봐요."


class StreamTests(unittest.TestCase):
    def test_a_stream_is_read_as_one_utf8_document(self):
        self.assertEqual(read_stream(io.BytesIO("안녕하세요.\n".encode("utf-8"))), ("<stdin>", "안녕하세요.\n"))
        self.assertEqual(read_stream(io.BytesIO(b"abc"), "<x>"), ("<x>", "abc"))

    def test_oversized_binary_and_non_utf8_input_are_rejected(self):
        for data in (b"a" * (MAX_BYTES + 1), b"ab\x00cd", b"\xff\xfe\xfd"):
            with self.subTest(size=len(data)), self.assertRaises(ValueError):
                read_stream(io.BytesIO(data))
        self.assertEqual(len(read_stream(io.BytesIO(b"a" * MAX_BYTES))[1]), MAX_BYTES, "상한과 같은 크기는 읽습니다.")


class LoadTests(unittest.TestCase):
    """읽지 못한 이유는 상태에 남고, 본문이 없으면 통과가 아니라 실패입니다."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "ok.md").write_text("내용입니다.\n", encoding="utf-8")
        (self.root / "empty.md").write_text("\n \n", encoding="utf-8")
        (self.root / "image.md").write_bytes(b"\x00\x01binary")
        (self.root / ".env").write_text("SECRET=1", encoding="utf-8")

    def test_given_text_is_ok_unless_it_is_blank(self):
        self.assertEqual(given("<x>", "글"), ("<x>", "글", "ok"))
        self.assertEqual(given("<x>", " \n"), ("<x>", None, "empty"))

    def test_a_file_is_read_or_its_status_says_why_not(self):
        self.assertEqual(load(self.root, "ok.md"), ("ok.md", "내용입니다.\n", "ok"))
        self.assertEqual(load(self.root, str(self.root / "ok.md"))[0], "ok.md", "절대 경로도 작업공간 상대 이름으로 적습니다.")
        for value, status in (("empty.md", "empty"), ("missing.md", "missing"), ("image.md", "binary_large_or_encoding"),
                              (".env", "denied"), ("../outside.md", "denied")):
            with self.subTest(value=value):
                self.assertEqual(load(self.root, value)[1:], (None, status))


class TextInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_texts_are_checked_like_files_and_mixed_with_them(self):
        (self.root / "ok.md").write_text("배포를 마쳤고 시험도 통과했습니다.\n", encoding="utf-8")
        result = check(self.root, ["ok.md"], texts=[("<stdin>", SLOP)])
        self.assertEqual([f["path"] for f in result["files"]], ["ok.md", "<stdin>"])
        self.assertEqual(result["blocking"], 1, "답변 속 대화용 문구는 파일과 똑같이 차단합니다.")
        self.assertFalse(result["passed"])
        self.assertEqual(result["findings"][0]["path"], "<stdin>")

    def test_empty_text_is_a_failure_not_a_vacuous_pass(self):
        result = check(self.root, [], texts=[("<stdin>", "  \n")])
        self.assertEqual(result["files"][0]["status"], "empty")
        self.assertIsNone(result["score"])
        self.assertFalse(result["passed"])
        (self.root / "empty.md").write_text("\n\n", encoding="utf-8")
        self.assertFalse(check(self.root, ["empty.md"])["passed"], "내용 없는 파일도 100점으로 통과시키지 않습니다.")

    def test_the_number_of_documents_is_still_bounded(self):
        with self.assertRaises(ValueError):
            check(self.root, [], texts=[])
        with self.assertRaises(ValueError):
            check(self.root, [], texts=[(f"<{i}>", "글") for i in range(65)])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def run_cli(self, *args, stdin=b""):
        return subprocess.run([sys.executable, "-m", "gtg", "prose", *args, "--workspace", str(self.root)], cwd=ROOT,
                              input=stdin, capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def test_a_dash_reads_standard_input(self):
        blocked = self.run_cli("-", stdin=SLOP.encode("utf-8"))
        report = json.loads(blocked.stdout)
        self.assertEqual((blocked.returncode, report["blocking"], report["files"][0]["path"]), (1, 1, "<stdin>"))
        clean = self.run_cli("-", "--register", "everyday", stdin="내일 3시에 봐요. 늦으면 연락 줘요.".encode("utf-8"))
        self.assertEqual(clean.returncode, 0)

    def test_text_options_name_each_document(self):
        process = self.run_cli("--text", "무결점 코드입니다.", "--text", "설정을 바꿨고 서버를 다시 켰다.")
        report = json.loads(process.stdout)
        self.assertEqual([f["path"] for f in report["files"]], ["<text 1>", "<text 2>"])
        self.assertEqual(process.returncode, 0)
        self.assertLess(report["files"][0]["score"]["value"], report["files"][1]["score"]["value"])

    def test_bad_input_ends_with_an_error_and_exit_code_one(self):
        for args, stdin in (((), b""), (("-",), b"\xff\xfe"), (("-",), b"a" * (MAX_BYTES + 1))):
            with self.subTest(args=args, size=len(stdin)):
                process = self.run_cli(*args, stdin=stdin)
                self.assertEqual(process.returncode, 1)
                self.assertFalse(json.loads(process.stdout)["ok"])
        empty = self.run_cli("-", stdin=b"   \n")
        self.assertEqual((empty.returncode, json.loads(empty.stdout)["files"][0]["status"]), (1, "empty"))

    def test_the_register_applies_to_standard_input_too(self):
        text = "형언할 수 없는 슬픔이 방 안을 채웠다.".encode("utf-8")
        self.assertEqual(self.run_cli("-", stdin=text).returncode, 0)
        self.assertEqual(self.run_cli("-", "--register", "literary", stdin=text).returncode, 1)


if __name__ == "__main__":
    unittest.main()
