# `tests/test_package_sources.py`

- 형식: `100644`
- 바이트: 2736
- SHA-256: `bedde0a8aee65b80547a12deeb8baac79193f87496e955a5ecbd55fc15b20cd1`
- 인코딩: `utf-8`

```
"""호스트별 규칙 원문과 패키지 원본의 읽기 경계를 검사합니다."""

from pathlib import Path
import shutil
import tempfile
import unittest

from gtg.package import build


ROOT = Path(__file__).resolve().parents[1]


class PackageSourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        for name in ("gtg", "profile"):
            shutil.copytree(ROOT / name, self.source / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (self.source / "scripts").mkdir()
        shutil.copyfile(ROOT / "scripts/gtg_runner.py", self.source / "scripts/gtg_runner.py")
        shutil.copyfile(ROOT / "VERSION", self.source / "VERSION")

    def package(self, platform="antigravity"):
        target = self.root / "package"
        return build(self.source, target, self.root / "installed", platform)

    def test_markdown_separator_does_not_remove_rule_content(self):
        original = b"# Rule\r\n\r\nKeep this first rule.\r\n\r\n---\r\n\r\nKeep this second rule.\r\n"
        (self.source / "profile/rules/gtg.md").write_bytes(original)
        self.package("gemini-cli")
        self.assertEqual((self.root / "package/GEMINI.md").read_bytes(), original)

    def test_required_source_file_links_are_rejected(self):
        for name in ("VERSION", "scripts/gtg_runner.py", "profile/rules/gtg.md"):
            with self.subTest(name=name):
                path = self.source / name
                data = path.read_bytes()
                saved = self.root / "saved"
                saved.write_bytes(data)
                path.unlink()
                path.symlink_to(saved)
                try:
                    with self.assertRaises(ValueError):
                        self.package()
                finally:
                    path.unlink()
                    path.write_bytes(data)
                    if (self.root / "package").exists():
                        shutil.rmtree(self.root / "package")

    def test_source_directory_link_is_rejected(self):
        directory = self.source / "profile/skills"
        directory.rename(self.root / "saved-skills")
        directory.symlink_to(self.root / "saved-skills", target_is_directory=True)
        with self.assertRaises(ValueError):
            self.package()

    def test_sensitive_file_cannot_enter_the_package(self):
        (self.source / "gtg/.env").write_text("synthetic-marker")
        with self.assertRaises(ValueError):
            self.package()


if __name__ == "__main__":
    unittest.main()
```
