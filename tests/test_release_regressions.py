"""3.0.1 최종 검토에서 재현한 재실행·범위·설치 경계 결함입니다."""

import os
from pathlib import Path
import signal
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from gtg.certificate import build as certificate, replay
from gtg.install import destination, doctor, install
from gtg.package import build
from gtg.runner import execute
from gtg.spec import fingerprint
from gtg.store import Store


ROOT = Path(__file__).resolve().parents[1]


class ReplayReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "value.txt").write_text("good")
        self.store = Store(self.root / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)

    def issued(self, script, timeout=5):
        (self.root / "check.py").write_text(script)
        spec = {"schema_version": 1, "goal": "재실행 중 상태와 프로세스를 확인합니다.", "checks": [
            {"id": "check", "criterion": "현재 입력이 올바릅니다.", "argv": [sys.executable, "check.py"],
             "watch": ["value.txt", "check.py"], "timeout_seconds": timeout}]}
        task = self.store.create(self.root, spec)
        self.assertEqual(execute(self.store, task, "check")["status"], "passed")
        return certificate(self.store, task)

    def test_replay_cannot_repair_inputs_during_check_and_claim_original_success(self):
        proof = self.issued("from pathlib import Path\n"
                            "if Path('repair').exists():\n    Path('value.txt').write_text('good')\n"
                            "assert Path('value.txt').read_text() == 'good'\n")
        (self.root / "repair").touch()
        (self.root / "value.txt").write_text("bad")
        result = replay(proof, self.root)
        self.assertEqual(result["verdict"], "invalid")
        self.assertEqual(result["checks"][0]["reason"], "changed_during_check")

    @unittest.skipUnless(os.name == "posix", "프로세스 그룹은 POSIX에서 검사합니다.")
    def test_replay_rejects_and_terminates_background_children(self):
        self.child_scenario(timeout=False)

    @unittest.skipUnless(os.name == "posix", "프로세스 그룹은 POSIX에서 검사합니다.")
    def test_replay_timeout_terminates_the_child_group(self):
        self.child_scenario(timeout=True)

    def child_scenario(self, *, timeout):
        child = "import time; from pathlib import Path; time.sleep(0.8); Path('leaked').touch(); time.sleep(10)"
        proof = self.issued("import subprocess, sys, time\nfrom pathlib import Path\n"
                            "if Path('spawn').exists():\n"
                            f"    child = subprocess.Popen([sys.executable, '-c', {child!r}])\n"
                            "    Path('child.pid').write_text(str(child.pid))\n"
                            + ("    time.sleep(10)\n" if timeout else ""), timeout=0.2 if timeout else 5)
        (self.root / "spawn").touch()
        try:
            result = replay(proof, self.root)
            time.sleep(1)
            self.assertFalse((self.root / "leaked").exists(), "재실행 뒤 하위 프로세스가 남으면 안 됩니다.")
            self.assertEqual(result["verdict"], "invalid")
            self.assertEqual(result["checks"][0]["reason"], "timeout" if timeout else "background_processes")
        finally:
            if (self.root / "child.pid").exists():
                try:
                    os.kill(int((self.root / "child.pid").read_text()), signal.SIGKILL)
                except ProcessLookupError:
                    pass


class ScopeReleaseTests(unittest.TestCase):
    def test_overlapping_watch_paths_hash_once_within_the_same_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "src").mkdir()
            (root / "src/code.py").write_text("VALUE = 1\n")
            with patch("gtg.spec.MAX_WATCH_FILES", 1):
                expected = fingerprint(root, ["src"])
                self.assertEqual(fingerprint(root, ["src", "src/code.py"]), expected)


class InstallReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def fake_agy(self, code=0):
        folder = self.root / "bin"
        folder.mkdir()
        path = folder / "agy"
        path.write_text(f"#!/bin/sh\ntouch '{self.root / 'registered'}'\nexit {code}\n")
        path.chmod(0o755)
        return patch.dict(os.environ, {"PATH": str(folder) + os.pathsep + os.environ["PATH"]})

    def test_custom_home_install_does_not_touch_the_real_host_registry(self):
        with self.fake_agy():
            report = install(ROOT, self.root, "antigravity-cli", "global")
        self.assertTrue(report["ok"])
        self.assertFalse((self.root / "registered").exists())
        self.assertFalse(report["host_registration"]["registered"])

    def test_native_registration_failure_is_reported_as_incomplete_installation(self):
        with self.fake_agy(3), patch("gtg.install.Path.home", return_value=self.root):
            report = install(ROOT, self.root, "antigravity-cli", "global")
        self.assertFalse(report["ok"])
        self.assertFalse(report["host_registration"]["registered"])
        self.assertTrue(Path(report["target"]).is_dir(), "검증한 파일과 복구 경로는 보존합니다.")

    def test_doctor_rejects_a_package_built_for_another_host(self):
        target = destination(self.root, "antigravity", "global")
        build(ROOT, target, target, "antigravity-cli")
        with self.assertRaises(ValueError):
            doctor(self.root, "antigravity", "global")

    def test_native_cli_copy_preserves_and_repairs_the_shared_desktop_package(self):
        desktop = install(ROOT, self.root, "antigravity", "global")
        shared = Path(desktop["target"])
        original = (shared / "gtg-manifest.json").read_bytes()

        def native_copy(platform, target, **kwargs):
            if platform == "antigravity-cli":
                shutil.copytree(target, shared, dirs_exist_ok=True)
                return {"registered": True}
            return None

        with self.fake_agy(), patch("gtg.install.Path.home", return_value=self.root), \
                patch("gtg.install.register", side_effect=native_copy):
            result = install(ROOT, self.root, "antigravity-cli", "global")
        self.assertTrue(result["shared_host_repair"]["ok"])
        self.assertEqual((Path(result["shared_host_backup"]) / "gtg-manifest.json").read_bytes(), original)
        for platform in ("antigravity", "antigravity-cli"):
            self.assertTrue(doctor(self.root, platform, "global")["ok"])


if __name__ == "__main__":
    unittest.main()
