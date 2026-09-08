"""설치물과 작업 상태가 사용자 저장소의 변경 목록에 나타나지 않아야 합니다."""

from pathlib import Path
import subprocess
import tempfile
import unittest

from gtg.install import install
from gtg.package import verify


ROOT = Path(__file__).resolve().parents[1]


class RepositoryNoiseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve() / "project"
        self.workspace.mkdir()
        (self.workspace / "source.py").write_text("value = 1\n")
        self.assertEqual(self.git("-c", "init.templateDir=", "init", "-q").returncode, 0)
        self.assertEqual(self.git("add", "-A").returncode, 0)
        self.assertEqual(self.git("-c", "user.email=t@example.com", "-c", "user.name=t",
                                  "commit", "-qm", "initial").returncode, 0)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.workspace), *args], capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1",
                                   "GIT_CONFIG_GLOBAL": "/dev/null"})

    def untracked(self):
        result = self.git("status", "--porcelain", "--untracked-files=all")
        self.assertEqual(result.returncode, 0, result.stderr)
        return [line for line in result.stdout.splitlines() if line.strip()]

    def test_workspace_install_leaves_the_repository_clean(self):
        self.assertEqual(self.untracked(), [])
        install(ROOT, self.workspace, "antigravity", "workspace")
        self.assertEqual(self.untracked(), [], "설치물이 사용자 변경 목록에 나타나면 안 됩니다.")

    def test_installed_package_still_verifies_with_its_own_ignore_file(self):
        result = install(ROOT, self.workspace, "antigravity", "workspace")
        target = Path(result["target"])
        self.assertEqual((target / ".gitignore").read_text(), "*\n")
        self.assertTrue(verify(target)["ok"])

    def test_other_plugins_and_user_files_are_not_ignored(self):
        install(ROOT, self.workspace, "antigravity", "workspace")
        other = self.workspace / ".agents/plugins/other-plugin"
        other.mkdir(parents=True, exist_ok=True)
        (other / "plugin.json").write_text("{}")
        (self.workspace / ".agents/rules").mkdir(parents=True, exist_ok=True)
        (self.workspace / ".agents/rules/mine.md").write_text("user rule")
        listed = " ".join(self.untracked())
        self.assertIn("other-plugin", listed)
        self.assertIn("mine.md", listed)
        self.assertNotIn("geminitogenius", listed)

    def test_uninstall_leaves_no_tracked_leftovers(self):
        from gtg.install import uninstall

        install(ROOT, self.workspace, "antigravity", "workspace")
        uninstall(self.workspace, "antigravity", "workspace")
        self.assertEqual(self.untracked(), [])


if __name__ == "__main__":
    unittest.main()
