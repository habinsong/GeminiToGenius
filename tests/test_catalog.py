"""전체 원문 기록과 누락 감지의 회귀 검사입니다."""

import base64
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


MODULE = importlib.util.spec_from_file_location("catalog", Path(__file__).resolve().parents[1] / "scripts/catalog.py")
catalog = importlib.util.module_from_spec(MODULE)
MODULE.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def put(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_text_binary_and_link_are_lossless(self):
        original = b"def run():\r\n    return '````'"
        self.put("source.py", original)
        binary = bytes(range(256))
        self.put("image.bin", binary)
        (self.root / "alias").symlink_to("source.py")
        rendered = catalog.render(self.root)
        manifest = json.loads(rendered["manifest.json"])
        entries = {e["path"]: e for e in manifest["files"]}
        self.assertEqual(set(entries), {"source.py", "image.bin", "alias"})
        doc = rendered["files/source.py.md"]
        self.assertIn(original, doc)
        self.assertIn(b"`````\n", doc)
        self.assertFalse(entries["source.py"]["trailing_newline"])
        self.assertEqual(entries["source.py"]["symbols"][0]["name"], "run")
        encoded = rendered["files/image.bin.md"].split(b"```base64\n", 1)[1].split(b"```", 1)[0]
        self.assertEqual(base64.b64decode(encoded), binary)
        self.assertEqual(entries["alias"]["mode"], "120000")

    def test_change_addition_and_deletion_are_detected(self):
        file = self.put("code.py", b"value = 1\n")
        output = self.root / catalog.OUTPUT / "current"
        catalog.sync(self.root, output, None, False)
        self.assertEqual(catalog.sync(self.root, output, None, True), [])
        file.write_bytes(b"value = 2\n")
        self.assertIn("files/code.py.md", catalog.sync(self.root, output, None, True))
        self.put("new.py", b"new = True\n")
        self.assertIn("files/new.py.md", catalog.sync(self.root, output, None, True))
        file.unlink()
        catalog.sync(self.root, output, None, False)
        self.assertFalse((output / "files/code.py.md").exists())
        self.assertEqual(catalog.sync(self.root, output, None, True), [])

    def test_authored_inventory_doc_is_included_but_generated_docs_are_not(self):
        self.put(catalog.OUTPUT + "/architecture.md", b"design")
        self.put(catalog.OUTPUT + "/baseline/files/old.py.md", b"archive")
        names = [e["path"] for e in json.loads(catalog.render(self.root)["manifest.json"])["files"]]
        self.assertEqual(names, [catalog.OUTPUT + "/architecture.md"])

    def test_sensitive_names_are_listed_without_reading(self):
        self.put(".env", b"DO_NOT_COPY")
        self.put(".env.private/nested.txt", b"DO_NOT_COPY_NESTED")
        self.put(".ENV.BACKUP/nested.txt", b"DO_NOT_COPY_UPPER")
        data = catalog.render(self.root)
        for item in json.loads(data["manifest.json"])["files"]:
            self.assertIn("excluded", item)
        self.assertNotIn(b"DO_NOT_COPY", b"".join(data.values()))


if __name__ == "__main__":
    unittest.main()
