"""임시 경로에서 설치·원문 검증·중도 실패 복구를 실행합니다."""

import json
import os
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gtg.install import destination, install, lock, restore, uninstall
from gtg.package import MANIFEST, verify
from gtg import legacy


ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "한글 공백 프로젝트"
        self.root.mkdir()

    def test_antigravity_install_executes_both_hooks_and_preserves_other_files(self):
        custom = self.root / ".agents/rules/mine.md"
        custom.parent.mkdir(parents=True)
        custom.write_text("user rule")
        result = install(ROOT, self.root, "antigravity", "workspace")
        self.assertEqual(result["hooks_executed"], 2)
        self.assertEqual(custom.read_text(), "user rule")
        self.assertTrue((Path(result["target"]) / "skills/gtg-build/SKILL.md").exists())

    def test_gemini_extension_has_its_own_manifest_and_timeout_units(self):
        result = install(ROOT, self.root, "gemini-cli", "global")
        target = Path(result["target"])
        self.assertTrue((target / "gemini-extension.json").exists())
        hooks = json.loads((target / "hooks/hooks.json").read_text())
        self.assertEqual(hooks["hooks"]["AfterAgent"][0]["hooks"][0]["timeout"], 5000)
        self.assertEqual(result["hooks_executed"], 2)

    def test_reinstall_backs_up_previous_package_and_uninstall_preserves_it(self):
        first = install(ROOT, self.root, "antigravity", "workspace")
        target = Path(first["target"])
        original = (target / "rules/AGENTS.md").read_bytes()
        second = install(ROOT, self.root, "antigravity", "workspace")
        self.assertEqual((Path(second["backup"]) / "rules/AGENTS.md").read_bytes(), original)
        removed = uninstall(self.root, "antigravity", "workspace")
        self.assertFalse(target.exists())
        self.assertEqual((Path(removed["preserved"]) / "rules/AGENTS.md").read_bytes(), original)
        restored = restore(self.root, "antigravity", "workspace", Path(removed["preserved"]))
        self.assertEqual(Path(restored["restored"]), target)
        self.assertTrue(verify(target)["ok"])

    def test_preflight_failure_does_not_modify_existing_install(self):
        install(ROOT, self.root, "antigravity", "workspace")
        target = destination(self.root, "antigravity", "workspace")
        manifest = (target / MANIFEST).read_bytes()
        with patch("gtg.install.verify", side_effect=ValueError("preflight failed")):
            with self.assertRaises(ValueError):
                install(ROOT, self.root, "antigravity", "workspace")
        self.assertEqual((target / MANIFEST).read_bytes(), manifest)

    def test_post_activation_failure_restores_previous_bytes(self):
        install(ROOT, self.root, "antigravity", "workspace")
        target = destination(self.root, "antigravity", "workspace")
        original = (target / MANIFEST).read_bytes()
        calls = 0

        def fail_second(path, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise ValueError("activation failed")
            return verify(path, **kwargs)

        with patch("gtg.install.verify", side_effect=fail_second):
            with self.assertRaisesRegex(ValueError, "activation failed"):
                install(ROOT, self.root, "antigravity", "workspace")
        self.assertEqual((target / MANIFEST).read_bytes(), original)
        self.assertTrue(verify(target)["ok"])

    def test_tampered_or_missing_source_is_detected(self):
        result = install(ROOT, self.root, "antigravity", "workspace")
        target = Path(result["target"])
        (target / "gtg/hooks.py").write_text("print('{}')")
        with self.assertRaises(ValueError):
            verify(target)
        (target / "run.py").unlink()
        with self.assertRaises(ValueError):
            verify(target)

    def test_unknown_existing_folder_and_symlink_are_preserved(self):
        target = destination(self.root, "antigravity", "workspace")
        target.mkdir(parents=True)
        (target / "user.txt").write_text("preserve")
        with self.assertRaises(ValueError):
            install(ROOT, self.root, "antigravity", "workspace")
        self.assertEqual((target / "user.txt").read_text(), "preserve")
        (target / "user.txt").unlink()
        target.rmdir()
        target.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            install(ROOT, self.root, "antigravity", "workspace")
        self.assertTrue(target.is_symlink())

    def test_concurrent_install_lock_is_not_ignored(self):
        with lock(self.root / ".gtg/installer"):
            with self.assertRaisesRegex(ValueError, "진행 중"):
                install(ROOT, self.root, "antigravity", "workspace")

    def test_legacy_migration_only_moves_owned_links_and_can_restore(self):
        gemini = self.root / ".gemini"
        (gemini / "config").mkdir(parents=True)
        for name, target in legacy.LINKS.items():
            (gemini / name).symlink_to(target)
        result = install(ROOT, self.root, "antigravity", "global")
        saved = Path(result["legacy_backup"])
        for name, target in legacy.LINKS.items():
            self.assertFalse((gemini / name).is_symlink())
            self.assertEqual(os.readlink(saved / name), target)
        uninstall(self.root, "antigravity", "global")
        legacy.restore(self.root, saved)
        for name, target in legacy.LINKS.items():
            self.assertEqual(os.readlink(gemini / name), target)

    def test_regular_user_global_rules_are_not_migrated(self):
        gemini = self.root / ".gemini"
        gemini.mkdir()
        (gemini / "GEMINI.md").write_text("user instructions")
        result = install(ROOT, self.root, "antigravity", "global")
        self.assertIsNone(result["legacy_backup"])
        self.assertEqual((gemini / "GEMINI.md").read_text(), "user instructions")

    def test_shell_entrypoint_preserves_callers_workspace(self):
        command = ["bash", str(ROOT / "scripts/install.sh")]
        installed = subprocess.run(command + ["--workspace", "."], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        self.assertEqual(Path(json.loads(installed.stdout)["target"]), destination(self.root, "antigravity", "workspace"))
        checked = subprocess.run(command + ["doctor", "--workspace", "."], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_doctor_rejects_a_moved_install_and_reinstall_repairs_it(self):
        install(ROOT, self.root, "antigravity", "workspace")
        moved = self.root.with_name("이동한 프로젝트")
        self.root.rename(moved)
        command = ["bash", str(ROOT / "scripts/install.sh")]
        checked = subprocess.run(command + ["doctor", "--workspace", str(moved)], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 1, checked.stdout + checked.stderr)
        self.assertFalse(json.loads(checked.stdout)["ok"])
        repaired = install(ROOT, moved, "antigravity", "workspace")
        self.assertTrue(repaired["ok"])
        self.assertTrue(verify(Path(repaired["target"]))["ok"])


if __name__ == "__main__":
    unittest.main()
