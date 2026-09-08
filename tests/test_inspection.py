"""여러 코드 파일을 읽되 범위·잘림·민감 경로를 명확하게 처리합니다."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from gtg.inspection import inspect as inspect_files, read_range


ROOT = Path(__file__).resolve().parents[1]


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def inspect(self, *paths, options=()):
        process = subprocess.run([sys.executable, "-m", "gtg", "inspect", "--workspace", str(self.root),
                                  *options, *paths], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        return json.loads(process.stdout)

    def test_small_files_are_batched_without_creating_state(self):
        sources = {"a.py": b"value = 1\n", "b.py": "이름 = '사진'\r\n".encode()}
        for name, content in sources.items():
            (self.root / name).write_bytes(content)
        result = self.inspect("a.py", "b.py", "a.py")
        self.assertEqual(len(result["files"]), 2)
        for file in result["files"]:
            self.assertTrue(file["complete"])
            self.assertEqual(file["text"].encode(), sources[file["path"]])
            self.assertEqual(file["file_sha256"], hashlib.sha256(sources[file["path"]]).hexdigest())
        self.assertFalse((self.root / ".gtg").exists())

    def test_partial_read_is_labelled_and_can_resume(self):
        (self.root / "large.py").write_text("first\nsecond\nthird\n")
        first = self.inspect("large.py", options=("--max-bytes", "6"))["files"][0]
        self.assertFalse(first["complete"])
        self.assertFalse(first["range_complete"])
        self.assertEqual(first["text"], "first\n")
        self.assertEqual(first["next_line"], 2)
        self.assertIsNone(first["file_sha256"])
        remaining = self.inspect("large.py", options=("--start-line", "2"))["files"][0]
        self.assertEqual(remaining["text"], "second\nthird\n")
        self.assertEqual(remaining["start_line"], 2)
        self.assertFalse(remaining["complete"])
        self.assertTrue(remaining["range_complete"])
        self.assertIsNone(remaining["next_line"])

    def test_range_reports_only_requested_lines(self):
        (self.root / "code.py").write_text("a\nb\nc\nd\n")
        file = self.inspect("code.py", options=("--start-line", "2", "--end-line", "3"))["files"][0]
        self.assertEqual(file["text"], "b\nc\n")
        self.assertEqual(file["end_line"], 3)
        self.assertEqual(file["next_line"], 4)
        self.assertFalse(file["complete"])
        self.assertTrue(file["range_complete"])
        self.assertEqual(file["status"], "ok")

    def test_later_files_are_reported_when_budget_is_used_up(self):
        (self.root / "a.py").write_text("abcdef\n")
        (self.root / "b.py").write_text("later\n")
        result = self.inspect("a.py", "b.py", options=("--max-bytes", "7"))
        self.assertEqual(result["content_bytes"], 7)
        self.assertEqual(result["files"][1]["status"], "budget_exhausted")
        self.assertFalse(result["files"][1]["complete"])

    def test_long_line_and_non_text_are_not_silently_cut(self):
        (self.root / "minified.js").write_text("x" * 200)
        (self.root / "binary.bin").write_bytes(b"binary\0data")
        (self.root / "invalid.txt").write_bytes(b"\xff\xfe")
        files = self.inspect("minified.js", "binary.bin", "invalid.txt", options=("--max-bytes", "32"))["files"]
        self.assertEqual([f["status"] for f in files], ["line_exceeds_budget", "binary", "unsupported_encoding"])
        self.assertTrue(all(not f["complete"] and not f["text"] for f in files))

    def test_sensitive_ancestors_symlinks_and_special_files_are_not_read(self):
        (self.root / ".env.private").mkdir()
        (self.root / ".env.private/hidden.txt").write_text("test-only-marker")
        (self.root / ".ENV.BACKUP").mkdir()
        (self.root / ".ENV.BACKUP/hidden.txt").write_text("test-only-marker")
        (self.root / "linked.txt").symlink_to(self.root / ".env.private/hidden.txt")
        paths = [".env.private/hidden.txt", ".ENV.BACKUP/hidden.txt", "linked.txt", "../outside", "missing.py"]
        if hasattr(os, "mkfifo"):
            os.mkfifo(self.root / "pipe")
            paths.append("pipe")
        result = self.inspect(*paths)
        self.assertNotIn("test-only-marker", json.dumps(result))
        self.assertTrue(all(not f["complete"] and not f["text"] for f in result["files"]))

    def test_absolute_paths_are_scoped_and_empty_files_are_complete(self):
        path = self.root / "empty.py"
        path.write_bytes(b"")
        files = self.inspect(str(path), str(path.parent.parent / "outside"))["files"]
        self.assertTrue(files[0]["complete"])
        self.assertEqual(files[0]["file_sha256"], hashlib.sha256(b"").hexdigest())
        self.assertEqual(files[1]["status"], "denied")

    def test_atomic_replacement_during_read_is_reported_without_old_content(self):
        path = self.root / "source.py"
        path.write_text("old source\n")
        def replace_after_read(stream, *args):
            result = read_range(stream, *args)
            replacement = self.root / "replacement"
            replacement.write_text("new source\n")
            replacement.replace(path)
            return result
        with patch("gtg.inspection.read_range", side_effect=replace_after_read):
            file = inspect_files(self.root, ["source.py"])["files"][0]
        self.assertEqual(file["status"], "changed_during_read")
        self.assertFalse(file["complete"])
        self.assertEqual(file["text"], "")

    def test_parent_directory_replacement_is_not_followed(self):
        folder = self.root / "code"
        folder.mkdir()
        (folder / "a.py").write_text("original\n")
        def replace_parent(stream, *args):
            result = read_range(stream, *args)
            folder.rename(self.root / "old")
            folder.symlink_to(self.root / "old", target_is_directory=True)
            return result
        with patch("gtg.inspection.read_range", side_effect=replace_parent):
            file = inspect_files(self.root, ["code/a.py"])["files"][0]
        self.assertEqual(file["status"], "changed_during_read")
        self.assertFalse(file["complete"])

    def test_unicode_line_is_never_returned_as_a_broken_prefix(self):
        (self.root / "한글.py").write_text("사진\n")
        file = self.inspect("한글.py", options=("--max-bytes", "4"))["files"][0]
        self.assertEqual(file["status"], "line_exceeds_budget")
        self.assertEqual(file["text"], "")

    def test_scan_budget_is_not_reported_as_a_complete_range(self):
        (self.root / "many-lines.py").write_text("123456\n123456\nlast\n")
        with patch("gtg.inspection.MAX_SCAN_BYTES", 10):
            file = inspect_files(self.root, ["many-lines.py"], start_line=3)["files"][0]
        self.assertEqual(file["status"], "scan_limit")
        self.assertFalse(file["range_complete"])
        self.assertEqual(file["text"], "")

    def test_unsupported_platform_is_identified(self):
        (self.root / "code.py").write_text("value = 1\n")
        with patch("gtg.inspection.os.supports_dir_fd", set()):
            file = inspect_files(self.root, ["code.py"])["files"][0]
        self.assertEqual(file["status"], "unsupported_platform")
        self.assertFalse(file["complete"])


if __name__ == "__main__":
    unittest.main()
