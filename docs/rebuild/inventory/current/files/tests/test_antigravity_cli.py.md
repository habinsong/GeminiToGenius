# `tests/test_antigravity_cli.py`

- 형식: `100644`
- 바이트: 8378
- SHA-256: `c0112eff4e9ba41b23b59a9ecbe0aed0cdbe9ffc367c230f4c05b7c4ccc3c7e8`
- 인코딩: `utf-8`

```
"""Antigravity CLI 플러그인 경로와 훅 계약을 실제 파일·실행으로 검사합니다."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import unittest.mock

from gtg.hooks import handle
from gtg.install import destination, detected, hosts_for, install
from gtg.package import build, verify
from gtg.sessions import key


ROOT = Path(__file__).resolve().parents[1]


class AntigravityCliPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "한글 공백 프로젝트"
        self.root.mkdir()

    def test_global_destination_matches_official_cli_plugin_path(self):
        target = destination(self.root, "antigravity-cli", "global")
        self.assertEqual(target, self.root / ".gemini/antigravity-cli/plugins/geminitogenius")

    def test_workspace_scope_is_rejected_until_verified(self):
        with self.assertRaises(ValueError):
            destination(self.root, "antigravity-cli", "workspace")

    def test_cli_install_registers_the_plugin_with_the_host(self):
        """파일만 놓아 두면 agy가 플러그인을 읽지 않습니다. 등록 명령까지 실행해야 합니다."""
        fake = self.root / "bin"
        fake.mkdir()
        log = self.root / "agy-calls.log"
        (fake / "agy").write_text(f'#!/bin/sh\necho "$@" >> "{log}"\nexit 0\n', encoding="utf-8")
        (fake / "agy").chmod(0o755)
        with unittest.mock.patch.dict(os.environ, {"PATH": f"{fake}:{os.environ['PATH']}"}):
            report = install(ROOT, self.root, "antigravity-cli", "global")
        self.assertEqual(report["host_registration"], {"registered": True})
        target = destination(self.root, "antigravity-cli", "global")
        self.assertEqual(log.read_text(encoding="utf-8").strip(), f"plugin install {target}")

    def test_missing_host_binary_reports_the_manual_command_instead_of_failing(self):
        with unittest.mock.patch("gtg.install.shutil.which", return_value=None):
            report = install(ROOT, self.root, "antigravity-cli", "global")
        self.assertTrue(report["ok"], "등록 도구가 없다고 설치가 실패하지 않습니다.")
        self.assertFalse(report["host_registration"]["registered"])
        self.assertIn("agy plugin install", report["host_registration"]["manual_command"])

    def test_other_hosts_do_not_run_a_registration_command(self):
        report = install(ROOT, self.root, "antigravity", "global")
        self.assertIsNone(report["host_registration"])

    def test_package_uses_plugin_layout_and_executes_both_hooks(self):
        stage = self.root / "stage"
        build(ROOT, stage, stage, "antigravity-cli")
        self.assertEqual(json.loads((stage / "plugin.json").read_text())["name"], "geminitogenius")
        self.assertTrue((stage / "rules/AGENTS.md").exists())
        self.assertTrue((stage / "skills/gtg-build/SKILL.md").exists())
        hooks = json.loads((stage / "hooks.json").read_text())
        self.assertEqual(set(hooks), {"gtg-context", "gtg-completion"})
        self.assertEqual(hooks["gtg-context"]["PreInvocation"][0]["timeout"], 5)
        self.assertIn("hook antigravity-cli PreInvocation", hooks["gtg-context"]["PreInvocation"][0]["command"])
        self.assertEqual(verify(stage)["hooks_executed"], 2)

    def test_install_is_independent_from_the_desktop_plugin(self):
        desktop = install(ROOT, self.root, "antigravity", "global")
        cli = install(ROOT, self.root, "antigravity-cli", "global")
        self.assertEqual(cli["hooks_executed"], 2)
        self.assertNotEqual(cli["target"], desktop["target"])
        self.assertEqual(Path(cli["target"]), self.root / ".gemini/antigravity-cli/plugins/geminitogenius")
        self.assertTrue(verify(Path(desktop["target"]))["ok"])
        self.assertEqual(json.loads((Path(cli["target"]) / "gtg-manifest.json").read_text())["platform"],
                         "antigravity-cli")

    def test_hook_events_use_the_shared_antigravity_contract(self):
        payload = {"conversationId": "cli-session", "workspacePaths": [str(self.root)], "invocationNum": 0}
        first = handle("antigravity-cli", "PreInvocation", payload)
        self.assertTrue(first["injectSteps"][0]["ephemeralMessage"])
        stop = handle("antigravity-cli", "Stop",
                      {**payload, "executionNum": 0, "fullyIdle": True, "terminationReason": "model_stop"})
        self.assertEqual(stop, {"decision": "stop"})
        self.assertNotEqual(key("antigravity-cli", "cli-session"), key("antigravity", "cli-session"))


class HostDetectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def marker(self, relative):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")

    def test_only_host_written_settings_count_as_evidence(self):
        self.assertEqual(detected(self.root), [])
        (self.root / ".gemini/config/plugins/geminitogenius").mkdir(parents=True)
        self.assertEqual(detected(self.root), [], "GTG가 만든 폴더는 호스트 근거가 아닙니다.")
        self.marker(".gemini/config/config.json")
        self.marker(".gemini/antigravity-cli/settings.json")
        self.assertEqual(detected(self.root), ["antigravity", "antigravity-cli"])

    def test_missing_platform_falls_back_to_desktop_and_never_guesses_workspace(self):
        self.assertEqual(hosts_for("install", self.root, "global", None), ["antigravity"])
        self.marker(".gemini/antigravity-cli/settings.json")
        self.assertEqual(hosts_for("install", self.root, "global", None), ["antigravity-cli"])
        self.assertEqual(hosts_for("install", self.root, "workspace", None), ["antigravity"])
        self.assertEqual(hosts_for("install", self.root, "global", "gemini-cli"), ["gemini-cli"])

    def test_one_command_installs_checks_and_removes_every_detected_host(self):
        self.marker(".gemini/config/config.json")
        self.marker(".gemini/antigravity-cli/settings.json")
        command = ["bash", str(ROOT / "scripts/install.sh")]
        home = ["--home", str(self.root)]
        installed = subprocess.run(command + home, capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        report = json.loads(installed.stdout)
        self.assertEqual([item["platform"] for item in report["hosts"]], ["antigravity", "antigravity-cli"])
        self.assertTrue(all(item["hooks_executed"] == 2 for item in report["hosts"]))
        checked = subprocess.run(command + ["doctor"] + home, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertEqual(len(json.loads(checked.stdout)["hosts"]), 2)
        removed = subprocess.run(command + ["uninstall"] + home, capture_output=True, text=True)
        self.assertEqual(removed.returncode, 0, removed.stdout + removed.stderr)
        for item in json.loads(removed.stdout)["hosts"]:
            self.assertTrue(Path(item["preserved"]).is_dir())
            self.assertFalse(Path(item["removed"]).exists())

    def test_one_failing_host_is_reported_without_hiding_the_others(self):
        self.marker(".gemini/config/config.json")
        self.marker(".gemini/antigravity-cli/settings.json")
        blocked = self.root / ".gemini/antigravity-cli/plugins/geminitogenius"
        blocked.mkdir(parents=True)
        (blocked / "user.md").write_text("사용자 파일")
        result = subprocess.run(["bash", str(ROOT / "scripts/install.sh"), "--home", str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["ok"])
        outcome = {item["platform"]: item["ok"] for item in report["hosts"]}
        self.assertEqual(outcome, {"antigravity": True, "antigravity-cli": False})
        self.assertEqual((blocked / "user.md").read_text(), "사용자 파일")


if __name__ == "__main__":
    unittest.main()
```
