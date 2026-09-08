"""실제 설치 프로세스를 강제 종료한 뒤 파일 상태로 복구를 검증합니다."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.install import destination, install
from gtg.install_journal import MoveJournal, durable_json
from gtg import legacy


ROOT = Path(__file__).resolve().parents[1]
CRASH = r'''
import os, signal, sys
from pathlib import Path
from gtg.install import install
mode, root, source = sys.argv[1:]
rename = Path.rename
def interrupted(self, target):
    result = rename(self, target)
    if (mode == "backup" and self.name == "geminitogenius") or (mode == "activate" and self.name.startswith("stage-")):
        os.kill(os.getpid(), signal.SIGKILL)
    return result
Path.rename = interrupted
install(Path(source), Path(root), "antigravity", "workspace")
'''


class InstallCrashTests(unittest.TestCase):
    def test_doctor_recovers_a_process_killed_during_replacement(self):
        for point in ("backup", "activate"):
            with self.subTest(point=point), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                install(ROOT, root, "antigravity", "workspace")
                target = destination(root, "antigravity", "workspace")
                before = target.stat().st_ino
                crashed = subprocess.run([sys.executable, "-c", CRASH, point, str(root), str(ROOT)], cwd=ROOT,
                                         capture_output=True, text=True)
                self.assertEqual(crashed.returncode, -9, crashed.stdout + crashed.stderr)
                checked = subprocess.run([sys.executable, "-m", "gtg.install", "doctor", "--workspace", str(root)],
                                         cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
                self.assertTrue(json.loads(checked.stdout)["ok"])
                self.assertEqual(target.stat().st_ino, before)

    def test_committed_replacement_is_preserved_after_crash_before_journal_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            install(ROOT, root, "antigravity", "workspace")
            target = destination(root, "antigravity", "workspace")
            before = target.stat().st_ino
            script = r'''
import os, signal, sys
from pathlib import Path
from gtg.install import install
from gtg.install_journal import MoveJournal
def crash(self): os.kill(os.getpid(), signal.SIGKILL)
MoveJournal.clear = crash
install(Path(sys.argv[2]), Path(sys.argv[1]), "antigravity", "workspace")
'''
            crashed = subprocess.run([sys.executable, "-c", script, str(root), str(ROOT)], cwd=ROOT, capture_output=True)
            self.assertEqual(crashed.returncode, -9)
            after = target.stat().st_ino
            self.assertNotEqual(after, before)
            working = root / ".gtg/installer"
            self.assertTrue(MoveJournal(root, working).recover())
            self.assertEqual(target.stat().st_ino, after)
            self.assertFalse(MoveJournal(root, working).recover())

    def test_partial_legacy_link_migration_is_rolled_back(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            install(ROOT, root, "antigravity", "global")
            for name, value in legacy.LINKS.items():
                (root / ".gemini" / name).symlink_to(value)
            script = r'''
import os, signal, sys
from pathlib import Path
from gtg.install import install
rename = Path.rename
def crash(self, target):
    result = rename(self, target)
    if self.name == "hooks.json": os.kill(os.getpid(), signal.SIGKILL)
    return result
Path.rename = crash
install(Path(sys.argv[2]), Path(sys.argv[1]), "antigravity", "global")
'''
            crashed = subprocess.run([sys.executable, "-c", script, str(root), str(ROOT)], cwd=ROOT, capture_output=True)
            self.assertEqual(crashed.returncode, -9)
            journal = MoveJournal(root, root / ".gemini/gtg-installer")
            self.assertTrue(journal.recover())
            for name, value in legacy.LINKS.items():
                self.assertEqual(os.readlink(root / ".gemini" / name), value)
            self.assertTrue(destination(root, "antigravity", "global").is_dir())

    def test_interrupted_recovery_can_be_retried(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            install(ROOT, root, "antigravity", "workspace")
            target = destination(root, "antigravity", "workspace")
            before = target.stat().st_ino
            subprocess.run([sys.executable, "-c", CRASH, "activate", str(root), str(ROOT)], cwd=ROOT, capture_output=True)
            script = r'''
import os, signal, sys
from pathlib import Path
from gtg.install_journal import MoveJournal
rename = Path.rename
def crash(self, target):
    result = rename(self, target)
    if Path(target).name.startswith("stage-"): os.kill(os.getpid(), signal.SIGKILL)
    return result
Path.rename = crash
root = Path(sys.argv[1])
MoveJournal(root, root / ".gtg/installer").recover()
'''
            crashed = subprocess.run([sys.executable, "-c", script, str(root)], cwd=ROOT, capture_output=True)
            self.assertEqual(crashed.returncode, -9)
            journal = MoveJournal(root, root / ".gtg/installer")
            self.assertTrue(journal.recover())
            self.assertEqual(target.stat().st_ino, before)

    def test_user_file_created_after_crash_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            install(ROOT, root, "antigravity", "workspace")
            subprocess.run([sys.executable, "-c", CRASH, "backup", str(root), str(ROOT)], cwd=ROOT, capture_output=True)
            target = destination(root, "antigravity", "workspace")
            target.mkdir()
            (target / "user.txt").write_text("preserve")
            journal = MoveJournal(root, root / ".gtg/installer")
            with self.assertRaisesRegex(ValueError, "다른 파일"):
                journal.recover()
            self.assertEqual((target / "user.txt").read_text(), "preserve")
            self.assertTrue(journal.path.exists())
            self.assertTrue(list(journal.working.glob("backup-*/gtg-manifest.json")))

    def test_corrupt_or_out_of_scope_journal_cannot_move_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            working = root / ".gtg/installer"
            working.mkdir(parents=True)
            journal = MoveJournal(root, working)
            for source in ("../outside", ".ssh/id_rsa", ".gtg/installer/../../user.txt"):
                data = {"schema_version": 1, "root": str(root), "state": "pending", "moves": [
                    {"source": source, "target": ".gtg/installer/backup-fixture", "identity": [1, 1, 1]}]}
                durable_json(journal.path, data)
                with self.assertRaises(ValueError):
                    journal.recover()
                self.assertTrue(journal.path.exists())


if __name__ == "__main__":
    unittest.main()
