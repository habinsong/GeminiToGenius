# `tests/test_checkpoints.py`

- 형식: `100644`
- 바이트: 4243
- SHA-256: `055218c2c6b3ddf7050309769e1ebc192f989cebfd31f9dee973522860a91fbb`
- 인코딩: `utf-8`

```
"""작업 메모가 재시작 후 남고 코드 변경과 실제 검증을 혼동하지 않습니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.checkpoints import latest, record
from gtg.hooks import handle
from gtg.runner import status
from gtg.sessions import Sessions, key
from gtg.store import Store


ROOT = Path(__file__).resolve().parents[1]


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / "source.txt").write_text("first")
        self.path = self.root / ".gtg/state.sqlite3"
        self.store = Store(self.path)
        self.addCleanup(self.store.close)
        self.task = self.store.create(self.root, {"schema_version": 1, "goal": "긴 작업을 재개합니다.", "checks": [{
            "id": "check", "criterion": "현재 파일의 동작을 검증합니다.", "argv": [sys.executable, "-c", "pass"],
            "watch": ["source.txt"]}]})
        self.note = {"summary": "입력 경계를 확인했습니다.", "next_action": "실패 입력을 재현합니다.", "files": ["source.txt"]}

    def test_checkpoint_survives_restart_without_marking_checks_passed(self):
        saved = record(self.store, self.task, self.note)
        other = Store(self.path)
        self.addCleanup(other.close)
        restored = status(other, self.task)
        self.assertEqual(restored["checkpoint"]["id"], saved)
        self.assertEqual(restored["checkpoint"]["next_action"], self.note["next_action"])
        self.assertTrue(restored["checkpoint"]["files_unchanged"])
        self.assertFalse(restored["verified"])
        self.assertFalse(restored["checkpoint"]["is_verification_evidence"])

    def test_changed_files_make_note_stale_without_erasing_it(self):
        record(self.store, self.task, self.note)
        (self.root / "source.txt").write_text("changed")
        restored = latest(self.store, self.task)
        self.assertFalse(restored["files_unchanged"])
        self.assertEqual(restored["summary"], self.note["summary"])

    def test_repeated_save_is_idempotent_and_new_milestone_keeps_history(self):
        first = record(self.store, self.task, self.note)
        self.assertEqual(record(self.store, self.task, self.note), first)
        second = record(self.store, self.task, {**self.note, "next_action": "수정 후 회귀 검사를 실행합니다."})
        self.assertNotEqual(first, second)
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM checkpoints").fetchone()[0], 2)

    def test_unbound_note_has_no_file_freshness_claim(self):
        record(self.store, self.task, {**self.note, "files": []})
        self.assertIsNone(latest(self.store, self.task)["files_unchanged"])

    def test_private_or_outside_paths_and_result_fields_are_rejected(self):
        for note in ({**self.note, "files": [".env"]}, {**self.note, "files": ["../other"]},
                     {**self.note, "verified": True}, {**self.note, "summary": "x" * 2049}):
            with self.subTest(note=note), self.assertRaises(ValueError):
                record(self.store, self.task, note)

    def test_checkpoint_cli_and_host_context(self):
        sessions = Sessions(self.store)
        sessions.bind(key("antigravity", "checkpoint-session"), self.task)
        note_path = self.root / "note.json"
        note_path.write_text(json.dumps(self.note))
        command = [sys.executable, "-m", "gtg", "--state", str(self.path), "checkpoint", self.task, "--note", str(note_path)]
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertFalse(json.loads(process.stdout)["verified"])
        context = handle("antigravity", "PreInvocation", {"conversationId": "checkpoint-session", "workspacePaths": [str(self.root)], "invocationNum": 1})
        self.assertIn(self.note["next_action"], str(context))
        self.assertIn("검증 근거가 아닌", str(context))


if __name__ == "__main__":
    unittest.main()
```
