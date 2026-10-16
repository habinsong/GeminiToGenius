"""실제 로컬 환경 확인을 기능·배포 검증으로 확대하지 않습니다."""

import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from gtg.environment import observe
from gtg.package import build, verify
from gtg.platforms import PLATFORMS


ROOT = Path(__file__).resolve().parents[1]


class EnvironmentTests(unittest.TestCase):
    def test_observation_alone_is_not_a_target_compatibility_pass(self):
        result = observe()
        self.assertEqual(result["observed"]["system"], platform.system())
        self.assertIsNone(result["matches"])
        self.assertFalse(result["target_compatibility_verified"])
        self.assertFalse(result["resource_limits_verified"])

    def test_matching_host_and_available_executable_are_reported(self):
        with patch("gtg.environment.shutil.which", return_value="/fixture/bin/tool"):
            result = observe({"system": platform.system(), "executables": ["fixture-tool"]})
        self.assertTrue(result["matches"])
        self.assertEqual(result["mismatches"], [])
        self.assertFalse(result["target_compatibility_verified"])

    def test_missing_executable_and_wrong_host_are_not_silently_repaired(self):
        result = observe({"system": "fixture-unsupported-os", "executables": ["gtg-fixture-missing-tool-49017"]})
        self.assertFalse(result["matches"])
        self.assertEqual({item["field"] for item in result["mismatches"]},
                         {"system", "executables.gtg-fixture-missing-tool-49017"})

    def test_unknown_or_empty_requirements_are_not_a_noop_success(self):
        for value in ({}, [], {"gpu_memory": 80}, {"system": ""}, {"executables": []},
                      {"executables": ["../git"]}, {"executables": ["git --version"]},
                      {"system": True}, {"executables": "git"}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                observe(value)

    def test_cli_mismatch_fails_without_creating_state_or_changing_requirements(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            expected = root / "requirements.json"
            content = json.dumps({"system": "fixture-unsupported-os"})
            expected.write_text(content)
            done = subprocess.run([sys.executable, "-B", "-m", "gtg", "environment", "--expect", str(expected)],
                                  cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
            self.assertFalse(json.loads(done.stdout)["matches"])
            self.assertEqual(expected.read_text(), content)
            self.assertEqual({p.name for p in root.iterdir()}, {"requirements.json"})

    def test_cli_rejects_symlinked_requirement_document(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "requirements.json").write_text(json.dumps({"system": platform.system()}))
            (root / "link.json").symlink_to(root / "requirements.json")
            done = subprocess.run([sys.executable, "-B", "-m", "gtg", "environment", "--expect", str(root / "link.json")],
                                  cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(done.returncode, 1)
            self.assertIn("심볼릭", json.loads(done.stdout)["error"])

    def test_cli_explicit_null_requirements_do_not_become_observation_only(self):
        with tempfile.TemporaryDirectory() as directory:
            expected = Path(directory).resolve() / "requirements.json"
            expected.write_text("null")
            done = subprocess.run([sys.executable, "-B", "-m", "gtg", "environment", "--expect", str(expected)],
                                  cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
            self.assertIn("JSON 객체", json.loads(done.stdout)["error"])

    def test_packaged_preflight_is_a_real_check_and_file_changes_invalidate_success(self):
        for host in PLATFORMS:
            with self.subTest(host=host), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                package, workspace = root / "package", root / "workspace"
                workspace.mkdir()
                build(ROOT, package, package, host)
                self.assertTrue(verify(package)["ok"])
                self.assertTrue((package / "skills/gtg-build/references/critical-review.md").is_file())
                runner = str(package / "run.py")
                expected = workspace / "requirements.json"
                expected.write_text(json.dumps({"system": platform.system()}))
                spec = {"schema_version": 1, "goal": "명시한 로컬 환경 필요조건을 비교합니다.", "checks": [{
                    "id": "environment", "criterion": "현재 Python 프로세스의 OS 필요조건이 맞습니다.",
                    "argv": [sys.executable, runner, "environment", "--expect", str(expected)],
                    "watch": ["requirements.json"]}]}
                (workspace / "task.json").write_text(json.dumps(spec))

                def command(*args):
                    done = subprocess.run([sys.executable, runner, *args, "--workspace", str(workspace)],
                                          cwd=workspace, capture_output=True, text=True)
                    return done, json.loads(done.stdout)

                done, result = command("start", "--spec", "task.json")
                self.assertEqual(done.returncode, 0, result)
                task = result["task_id"]
                done, result = command("verify", task)
                self.assertEqual(done.returncode, 0, result)
                self.assertTrue(result["verified"])
                expected.write_text(json.dumps({"system": "fixture-unsupported-os"}))
                _, result = command("status", task)
                self.assertEqual(result["checks"][0]["status"], "stale")
                done, result = command("verify", task)
                self.assertEqual(done.returncode, 1, result)
                self.assertFalse(result["verified"])
                self.assertEqual(json.loads(expected.read_text())["system"], "fixture-unsupported-os")


if __name__ == "__main__":
    unittest.main()
