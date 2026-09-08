"""완료 주장을 증거에 묶고 상태 DB 없이 재실행으로 확인합니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.certificate import build, digest, replay
from gtg.runner import execute
from gtg.store import Store


def spec(goal="합계 함수를 고칩니다."):
    return {"schema_version": 1, "goal": goal, "checks": [
        {"id": "sum", "criterion": "합계가 올바릅니다.", "argv": [sys.executable, "check.py"],
         "watch": ["total.py", "check.py"]},
        {"id": "style", "criterion": "구문이 유효합니다.",
         "argv": [sys.executable, "-c", "import ast, pathlib; ast.parse(pathlib.Path('total.py').read_text())"],
         "watch": ["total.py"]}]}


class CertificateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        (self.workspace / "total.py").write_text("def total(values):\n    return sum(values)\n")
        (self.workspace / "check.py").write_text("from total import total\nassert total([1, 2]) == 3\n")
        self.store = Store(self.workspace / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)
        self.task = self.store.create(self.workspace, spec())

    def pass_all(self):
        for check in ("sum", "style"):
            self.assertEqual(execute(self.store, self.task, check)["status"], "passed")

    def test_certificate_binds_every_claim_to_a_command_and_fingerprint(self):
        self.pass_all()
        document = build(self.store, self.task)
        self.assertTrue(document["verified"])
        self.assertEqual(document["workspace"], str(self.workspace))
        self.assertEqual({check["id"] for check in document["checks"]}, {"sum", "style"})
        for check in document["checks"]:
            self.assertEqual(check["status"], "passed")
            self.assertEqual(check["returncode"], 0)
            self.assertTrue(check["criterion"])
            self.assertTrue(check["argv"])
            self.assertRegex(check["evidence_fingerprint"], r"\A[0-9a-f]{64}\Z")
        self.assertEqual(document["digest"], digest(document))

    def test_unverified_task_cannot_produce_a_completion_claim(self):
        self.assertEqual(execute(self.store, self.task, "style")["status"], "passed")
        document = build(self.store, self.task)
        self.assertFalse(document["verified"])
        pending = {check["id"]: check["status"] for check in document["checks"]}
        self.assertEqual(pending["sum"], "pending")
        self.assertIsNone(pending_evidence(document, "sum"))

    def test_edited_body_breaks_the_digest(self):
        self.pass_all()
        document = build(self.store, self.task)
        for change in ({"verified": True, "goal": "다른 목표"}, {"checks": []}):
            with self.subTest(change=tuple(change)):
                tampered = {**document, **change}
                self.assertNotEqual(digest(tampered), tampered["digest"])
                with self.assertRaises(ValueError):
                    replay(tampered, self.workspace)

    def test_replay_reconstructs_the_claim_without_the_state_database(self):
        self.pass_all()
        document = build(self.store, self.task)
        self.store.close()
        (self.workspace / ".gtg/state.sqlite3").unlink()
        report = replay(document, self.workspace)
        self.assertTrue(report["reconstructed"])
        self.assertEqual([check["reconstructed"] for check in report["checks"]], [True, True])
        self.assertFalse((self.workspace / ".gtg/state.sqlite3").exists(), "재실행은 상태 DB를 만들지 않습니다.")

    def test_changed_evidence_files_break_reconstruction(self):
        self.pass_all()
        document = build(self.store, self.task)
        (self.workspace / "total.py").write_text("def total(values):\n    return sum(values)  # 주석\n")
        report = replay(document, self.workspace)
        self.assertFalse(report["reconstructed"])
        reasons = {check["id"]: check["reason"] for check in report["checks"] if not check["reconstructed"]}
        self.assertEqual(set(reasons), {"sum", "style"})
        self.assertTrue(all(reason == "fingerprint" for reason in reasons.values()))

    def test_failing_command_is_reported_as_a_broken_claim(self):
        self.pass_all()
        document = build(self.store, self.task)
        (self.workspace / "check.py").write_text("from total import total\nassert total([1, 2]) == 4\n")
        for check in document["checks"]:
            if check["id"] == "sum":
                check["evidence_fingerprint"] = None
        document["digest"] = digest(document)
        report = replay(document, self.workspace)
        broken = next(check for check in report["checks"] if check["id"] == "sum")
        self.assertFalse(broken["reconstructed"])
        self.assertEqual(broken["reason"], "returncode")

    def test_foreign_workspace_commands_are_not_run_without_consent(self):
        self.pass_all()
        document = build(self.store, self.task)
        with tempfile.TemporaryDirectory() as other:
            elsewhere = Path(other).resolve()
            with self.assertRaisesRegex(ValueError, "작업공간"):
                replay(document, elsewhere)
            report = replay(document, elsewhere, trust_commands=True)
            self.assertFalse(report["workspace_matches"])
            self.assertFalse(report["reconstructed"])


class InstalledCertificateTests(unittest.TestCase):
    def test_installed_cli_writes_a_certificate_and_replays_it_after_the_state_is_gone(self):
        from gtg.install import install

        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            package = install(root, workspace, "antigravity", "workspace")
            runner = str(Path(package["target"]) / "run.py")
            (workspace / "total.py").write_text("def total(values):\n    return sum(values)\n")
            (workspace / "check.py").write_text("from total import total\nassert total([1, 2]) == 3\n")
            (workspace / "task.json").write_text(json.dumps(spec()))

            def command(*args, expect=0):
                done = subprocess.run([sys.executable, runner, *args], cwd=workspace, capture_output=True, text=True)
                self.assertEqual(done.returncode, expect, done.stdout + done.stderr)
                return json.loads(done.stdout)

            task = command("start", "--spec", "task.json", "--workspace", ".")["task_id"]
            command("certify", task, expect=1)
            command("verify", task)
            issued = command("certify", task, "--output", "proof.json")
            self.assertTrue(issued["verified"])
            saved = json.loads((workspace / "proof.json").read_text())
            self.assertNotIn("state_path", saved)
            self.assertEqual(saved["digest"], digest(saved))

            (workspace / ".gtg/state.sqlite3").unlink()
            report = command("replay", "--certificate", "proof.json", "--workspace", ".")
            self.assertTrue(report["reconstructed"])
            self.assertTrue(report["workspace_matches"])

            (workspace / "total.py").write_text("def total(values):\n    return 0\n")
            broken = command("replay", "--certificate", "proof.json", "--workspace", ".", expect=1)
            self.assertFalse(broken["reconstructed"])


def pending_evidence(document, check_id):
    return next(check["evidence_fingerprint"] for check in document["checks"] if check["id"] == check_id)


if __name__ == "__main__":
    unittest.main()
