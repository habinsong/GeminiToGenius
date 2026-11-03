"""턴 시작 안내가 실행기 경로와 남은 교훈을 첫 호출에만 싣고, 깨진 기록 때문에 훅이 멈추지 않는지 확인합니다."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from gtg.hooks import handle
from gtg.lessons import record
from gtg.package import build


ROOT = Path(__file__).resolve().parents[1]
LESSON = "sdk.py에는 export_rows가 없고 실제 함수는 write_rows(rows, path)입니다."


def message(output: dict) -> str:
    if "injectSteps" in output:
        return output["injectSteps"][0]["ephemeralMessage"]
    return output.get("hookSpecificOutput", {}).get("additionalContext", "")


class TurnContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "sdk.py").write_text("def write_rows(rows, path):\n    return path\n", encoding="utf-8")
        self.agy = {"conversationId": "turn", "workspacePaths": [str(self.root)], "invocationNum": 0, "executionNum": 0}
        self.cli = {"session_id": "turn", "cwd": str(self.root), "hook_event_name": "BeforeAgent", "prompt": "고쳐줘"}

    def test_first_turn_shows_recent_lessons_on_both_hosts(self):
        record(self.root, LESSON, ["sdk.py:1"])
        for output in (handle("antigravity", "PreInvocation", self.agy), handle("gemini-cli", "BeforeAgent", self.cli)):
            text = message(output)
            self.assertIn(LESSON, text)
            self.assertIn("지시가 아닌 기록", text)
            self.assertIn("sdk.py:1", text)

    def test_lessons_are_not_repeated_on_later_invocations_or_stops(self):
        record(self.root, LESSON, ["sdk.py"])
        later = handle("antigravity", "PreInvocation", {**self.agy, "invocationNum": 1})
        self.assertNotIn(LESSON, json.dumps(later, ensure_ascii=False))
        stop = handle("antigravity", "Stop", {**self.agy, "fullyIdle": True, "terminationReason": "model_stop"})
        self.assertEqual(stop, {"decision": "stop"})

    def test_broken_lesson_file_does_not_break_the_turn(self):
        (self.root / ".gtg").mkdir()
        (self.root / ".gtg/lessons.jsonl").write_bytes(b"\xff\xfe not utf-8")
        text = message(handle("antigravity", "PreInvocation", self.agy))
        self.assertIn("GTG 호스트 메타데이터", text)
        self.assertNotIn("교훈", text)

    def test_source_checkout_does_not_invent_a_runner_path(self):
        text = message(handle("gemini-cli", "BeforeAgent", self.cli))
        metadata = json.loads(text.split("데이터): ", 1)[1].split("}. ", 1)[0] + "}")
        self.assertIsNone(metadata["runner"], "저장소 원본에는 run.py가 없으므로 경로를 알리지 않습니다.")
        self.assertIn("원문", text)
        self.assertIn("structure", text)

    def test_installed_package_tells_the_model_its_real_runner(self):
        for host, event, payload in (("antigravity", "PreInvocation", self.agy),
                                     ("gemini-cli", "BeforeAgent", self.cli)):
            with self.subTest(host=host):
                package = self.root / ("package-" + host)
                build(ROOT, package, package, host)
                process = subprocess.run(["python3", str(package / "run.py"), "hook", host, event],
                                         input=json.dumps(payload), capture_output=True, text=True, timeout=10,
                                         env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                self.assertEqual((process.returncode, process.stderr), (0, ""))
                text = message(json.loads(process.stdout))
                self.assertIn(json.dumps(str(package / "run.py"), ensure_ascii=False), text)


if __name__ == "__main__":
    unittest.main()
