"""개수가 맞아도 필수 이벤트가 없거나 실제 시간 제한이 틀리면 거부합니다."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from gtg.package import MANIFEST, build, verify


ROOT = Path(__file__).resolve().parents[1]


class PackageHookTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def rewrite(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value))
        self.refresh_hash(name)

    def refresh_hash(self, name):
        path = self.root / name
        manifest = json.loads((self.root / MANIFEST).read_text())
        manifest["files"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.root / MANIFEST).write_text(json.dumps(manifest))

    def test_duplicate_context_hook_cannot_replace_completion(self):
        build(ROOT, self.root, self.root, "antigravity")
        hooks = json.loads((self.root / "hooks.json").read_text())
        hooks["gtg-completion"] = hooks["gtg-context"]
        self.rewrite("hooks.json", hooks)
        for execute in (False, True):
            with self.subTest(execute_hooks=execute), self.assertRaises(ValueError):
                verify(self.root, execute_hooks=execute)

    def test_declared_millisecond_timeout_is_enforced(self):
        build(ROOT, self.root, self.root, "gemini-cli")
        hooks = json.loads((self.root / "hooks/hooks.json").read_text())
        hooks["hooks"]["BeforeAgent"][0]["hooks"][0]["timeout"] = 1
        self.rewrite("hooks/hooks.json", hooks)
        runner = self.root / "run.py"
        runner.write_text("import time\ntime.sleep(0.1)\n" + runner.read_text())
        self.refresh_hash("run.py")
        with self.assertRaisesRegex(ValueError, "시간 제한"):
            verify(self.root)

    def test_disabled_or_malformed_required_hook_is_a_validation_error(self):
        build(ROOT, self.root, self.root, "antigravity")
        hooks = json.loads((self.root / "hooks.json").read_text())
        hooks["gtg-context"]["enabled"] = False
        self.rewrite("hooks.json", hooks)
        with self.assertRaises(ValueError):
            verify(self.root)

    def test_command_cannot_dispatch_a_different_event(self):
        build(ROOT, self.root, self.root, "antigravity")
        hooks = json.loads((self.root / "hooks.json").read_text())
        handler = hooks["gtg-completion"]["Stop"][0]
        handler["command"] = handler["command"].removesuffix("Stop") + "PreInvocation"
        self.rewrite("hooks.json", hooks)
        with self.assertRaisesRegex(ValueError, "이벤트"):
            verify(self.root, execute_hooks=False)

    def test_malformed_and_filtered_cli_hooks_are_rejected_before_execution(self):
        build(ROOT, self.root, self.root, "gemini-cli")
        valid = (self.root / "hooks/hooks.json").read_text()
        for replacement in (None, False, [], {"hooks": False},
                            {"hooks": [], "matcher": "never"}):
            with self.subTest(group=replacement):
                hooks = json.loads(valid)
                hooks["hooks"]["AfterAgent"][0] = replacement
                self.rewrite("hooks/hooks.json", hooks)
                with self.assertRaises(ValueError):
                    verify(self.root, execute_hooks=False)

    def test_invalid_timeout_values_are_rejected(self):
        build(ROOT, self.root, self.root, "antigravity")
        valid = (self.root / "hooks.json").read_text()
        for timeout in (False, 0, -1, 0.5, None, "5", float("inf"), float("nan")):
            with self.subTest(timeout=timeout):
                hooks = json.loads(valid)
                hooks["gtg-context"]["PreInvocation"][0]["timeout"] = timeout
                self.rewrite("hooks.json", hooks)
                with self.assertRaises(ValueError):
                    verify(self.root, execute_hooks=False)


if __name__ == "__main__":
    unittest.main()
