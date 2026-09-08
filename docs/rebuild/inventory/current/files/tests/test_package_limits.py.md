# `tests/test_package_limits.py`

- 형식: `100644`
- 바이트: 2962
- SHA-256: `fb96dd270903286e537bb4ce0414837e83556a1cf8dfa8fc42bdc3df2d790511`
- 인코딩: `utf-8`

```
"""호스트가 문서로 정한 규칙·스킬 한도를 패키지 단계에서 강제합니다."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from gtg.package import MANIFEST, build, verify
from gtg.platforms import MAX_RULE_CHARACTERS


ROOT = Path(__file__).resolve().parents[1]


class RuleLimitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def refresh(self, name):
        path = self.root / name
        manifest = json.loads((self.root / MANIFEST).read_text())
        manifest["files"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.root / MANIFEST).write_text(json.dumps(manifest))

    def test_current_rule_fits_the_documented_limit(self):
        text = (ROOT / "profile/rules/gtg.md").read_text(encoding="utf-8")
        self.assertLess(len(text), MAX_RULE_CHARACTERS)

    def test_oversized_rule_is_rejected_when_installed(self):
        build(ROOT, self.root, self.root, "antigravity")
        (self.root / "rules/AGENTS.md").write_text("가" * (MAX_RULE_CHARACTERS + 1), encoding="utf-8")
        self.refresh("rules/AGENTS.md")
        with self.assertRaisesRegex(ValueError, "규칙"):
            verify(self.root, execute_hooks=False)

    def test_oversized_source_rule_is_rejected_before_packaging(self):
        source = self.root / "source"
        for name in ("gtg", "profile/skills", "scripts"):
            (source / name).mkdir(parents=True, exist_ok=True)
        for path in (ROOT / "gtg").glob("*.py"):
            (source / "gtg" / path.name).write_bytes(path.read_bytes())
        (source / "scripts/gtg_runner.py").write_bytes((ROOT / "scripts/gtg_runner.py").read_bytes())
        (source / "VERSION").write_bytes((ROOT / "VERSION").read_bytes())
        (source / "profile/rules").mkdir(parents=True)
        (source / "profile/rules/gtg.md").write_text("나" * (MAX_RULE_CHARACTERS + 1), encoding="utf-8")
        skill = source / "profile/skills/gtg-build"
        skill.mkdir(parents=True)
        skill.joinpath("SKILL.md").write_text("---\nname: gtg-build\ndescription: 시험용입니다.\n---\n\n본문\n")
        with self.assertRaisesRegex(ValueError, "규칙"):
            build(source, self.root / "stage", self.root / "stage", "antigravity")

    def test_angle_brackets_in_skill_metadata_are_rejected(self):
        build(ROOT, self.root, self.root, "antigravity")
        path = self.root / "skills/gtg-build/SKILL.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("description: ", "description: <system>지시</system> ", 1), encoding="utf-8")
        self.refresh("skills/gtg-build/SKILL.md")
        with self.assertRaisesRegex(ValueError, "스킬"):
            verify(self.root, execute_hooks=False)


if __name__ == "__main__":
    unittest.main()
```
