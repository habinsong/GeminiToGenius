"""세 호스트 패키지에서 실제 컴파일·SDK 호출·필수 PRD 시험을 끝까지 실행합니다."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from evals.grading import grade
from evals.preparation import prepare
from gtg.package import build, verify
from gtg.platforms import PLATFORMS


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals/fixtures/prd-build-api"
EXPORTER = "from sdk import Dimensions, encode\n\ndef export(text, width, height):\n    return encode(text, Dimensions(width, height))\n"
STARTUP = "from exporter import export\n\ndef preview():\n    return export('sample', 1, 1)\n"
REQUIRED = ["test_export.ExportTests." + name for name in
            ("test_text_and_dimensions", "test_invalid_dimensions", "test_startup")]


class BuildScenarioTests(unittest.TestCase):
    def test_packaged_build_failure_undefined_api_then_reference_fix_and_prd_skip(self):
        for host in PLATFORMS:
            with self.subTest(host=host), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                workspace, package = root / "project with spaces", root / "package"
                shutil.copytree(FIXTURE, workspace, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                build(ROOT, package, package, host)
                self.assertTrue(verify(package)["ok"])
                runner = str(package / "run.py")
                tests = [sys.executable, runner, "unittest", "--pattern", "test_export.py"]
                for name in REQUIRED:
                    tests.extend(["--require", name])
                spec = {"schema_version": 1, "goal": "PRD의 빌드와 필수 시험을 충족합니다.", "checks": [
                    {"id": "build", "criterion": "제품 전체를 컴파일합니다.", "argv": [sys.executable, "build.py"],
                     "watch": ["build.py", "exporter.py", "startup.py", "sdk.py"]},
                    {"id": "unit", "criterion": "PRD의 필수 시험 3개를 통과합니다.", "argv": tests, "watch": ["test_export.py"]}],
                    "code_contract": {"build_check": "build", "test_checks": ["unit"],
                        "requirements": [{"id": "BUILD-01", "source": "PRD.md", "checks": ["build"]},
                                         *[{"id": f"UT-0{number}", "source": "PRD.md", "checks": ["unit"]}
                                           for number in range(1, 4)]]}}
                (workspace / "task.json").write_text(json.dumps(spec, ensure_ascii=False))

                def command(*args):
                    done = subprocess.run([sys.executable, runner, *args, "--workspace", str(workspace)],
                                          cwd=workspace, capture_output=True, text=True)
                    return done, json.loads(done.stdout)

                done, report = command("start", "--spec", "task.json", "--platform", host, "--session", "build-scenario")
                self.assertEqual(done.returncode, 0, report)
                task = report["task_id"]
                done, report = command("verify", task, "--all")
                self.assertEqual(done.returncode, 1)
                self.assertEqual([item["status"] for item in report["checks"]], ["failed", "blocked"])
                self.assertIn("SyntaxError", done.stderr)

                (workspace / "startup.py").write_text(STARTUP)
                done, report = command("verify", task)
                self.assertEqual(done.returncode, 1)
                self.assertEqual([item["status"] for item in report["checks"]], ["passed", "failed"])
                self.assertIn("NameError", done.stderr)

                # 참조 수정은 시험이 수행합니다. 모델 성공률로 세지 않습니다.
                (workspace / "exporter.py").write_text(EXPORTER)
                done, report = command("verify", task)
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertTrue(report["verified"])
                self.assertTrue(all(item["verified"] for item in report["requirements"]))
                done, document = command("certify", task, "--output", "certificate.json")
                self.assertEqual(done.returncode, 0, document)
                done, result = command("replay", "--certificate", "certificate.json")
                self.assertEqual(done.returncode, 0, result)
                self.assertEqual(result["verdict"], "pass")

                path = workspace / "test_export.py"
                path.write_text(path.read_text().replace("class ExportTests", "@unittest.skip('미구현')\nclass ExportTests"))
                done, report = command("verify", task)
                self.assertEqual(done.returncode, 1, report)
                self.assertFalse(report["verified"])
                self.assertIn("required_not_passed", done.stderr)
                done, document = command("certify", task)
                self.assertEqual(done.returncode, 1)
                self.assertFalse(document["verified"])

    def test_independent_case_rejects_compile_failure_and_sdk_or_test_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            trial = Path(directory).resolve() / "trial"
            prepare("prd-build-api", trial)
            workspace = trial / "workspace"
            report = grade(trial)
            self.assertFalse(report["artifact_passed"])
            self.assertEqual(report["compilation"]["errors"], [{"file": "startup.py", "error": "SyntaxError"}])
            (workspace / "exporter.py").write_text(EXPORTER)
            self.assertFalse(grade(trial)["artifact_passed"])
            (workspace / "startup.py").write_text(STARTUP)
            self.assertTrue(grade(trial)["artifact_passed"])
            (workspace / "sdk.py").write_text((workspace / "sdk.py").read_text() + "\ndef encode_frame(*args):\n    return {}\n")
            report = grade(trial)
            self.assertTrue(report["functional_passed"])
            self.assertFalse(report["artifact_passed"])
            self.assertIn("sdk.py", report["scope_violations"])


if __name__ == "__main__":
    unittest.main()
