# `tests/test_hooks.py`

- 형식: `100644`
- 바이트: 13104
- SHA-256: `bd9c9970fb29208435e00779e335a77fc96a9c9ea49b8558be3a75f14ee011e8`
- 인코딩: `utf-8`

```
"""공식 JSON 계약을 실제 훅 프로세스로 재생합니다. 실제 호스트 시험은 아닙니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.hooks import handle
from gtg.runner import execute
from gtg.sessions import Sessions, key
from gtg.store import Store


ROOT = Path(__file__).resolve().parents[1]


class HookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "source.txt").write_text("ready")
        self.store = Store(self.root / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)
        self.task = self.store.create(self.root, {"schema_version": 1, "goal": "결과 검증", "checks": [{
            "id": "check", "criterion": "입력 파일을 실제로 읽을 수 있어야 합니다.",
            "argv": [sys.executable, "-c", "from pathlib import Path; assert Path('source.txt').read_text() == 'ready'"],
            "watch": ["source.txt"]}]})
        self.sessions = Sessions(self.store)
        self.agy = {"conversationId": "test-session", "workspacePaths": [str(self.root)],
                    "executionNum": 0, "fullyIdle": True, "terminationReason": "model_stop"}
        self.cli = {"session_id": "test-session", "cwd": str(self.root), "hook_event_name": "AfterAgent",
                    "stop_hook_active": False, "timestamp": "2026-09-08T00:00:00Z"}
        for platform in ("antigravity", "gemini-cli"):
            self.sessions.bind(key(platform, "test-session"), self.task)

    def test_platforms_have_distinct_stop_contracts(self):
        agy = handle("antigravity", "Stop", self.agy)
        cli = handle("gemini-cli", "AfterAgent", self.cli)
        self.assertEqual(agy["decision"], "continue")
        self.assertEqual(cli["decision"], "deny")

    def test_running_check_stops_without_claiming_completion(self):
        """검사가 실행 중이면 재개하지 않되 미검증을 조용히 통과시키지 않습니다."""
        run = self.store.begin(self.task, "check")
        self.addCleanup(self.store.finish, run, {"status": "interrupted", "returncode": None})
        agy = handle("antigravity", "Stop", self.agy)
        self.assertEqual(agy["decision"], "stop", "실행 중인 검사를 재개로 중복 실행하지 않습니다.")
        self.assertIn("실행 중", agy["reason"])
        self.assertIn("check", agy["reason"], "어떤 검사가 남았는지 밝힙니다.")
        self.assertEqual(self.sessions.get(key("antigravity", "test-session"))["retries"], 0,
                         "재개 예산을 쓰지 않습니다.")

    def test_interrupted_run_left_behind_does_not_pass_as_complete(self):
        """중단된 실행이 남긴 기록이 완료 보고를 조용히 허용하면 안 됩니다."""
        script = ("from pathlib import Path; from gtg.store import Store; import sys; "
                  "Store(Path(sys.argv[1])).begin(sys.argv[2], 'check')")
        subprocess.run([sys.executable, "-c", script, str(self.root / ".gtg/state.sqlite3"), self.task],
                       cwd=ROOT, check=True)
        response = handle("antigravity", "Stop", self.agy)
        self.assertEqual(response["decision"], "stop")
        self.assertIn("recover", response["reason"])

    def test_retry_cap_and_duplicate_event_do_not_loop_forever(self):
        self.assertEqual(handle("antigravity", "Stop", self.agy)["decision"], "continue")
        self.assertEqual(handle("antigravity", "Stop", self.agy)["decision"], "stop")
        self.agy["executionNum"] = 1
        self.assertEqual(handle("antigravity", "Stop", self.agy)["decision"], "continue")
        self.agy["executionNum"] = 2
        self.assertEqual(handle("antigravity", "Stop", self.agy)["decision"], "stop")

    def test_host_error_and_user_stop_pause_without_forcing_retry(self):
        self.sessions.pause(key("gemini-cli", "test-session"), "독립적인 어댑터 시험")
        for reason in ("error", "max_steps_exceeded", "user_cancelled", "unknown_future_reason"):
            with self.subTest(reason=reason):
                self.sessions.resume(key("antigravity", "test-session"))
                payload = {**self.agy, "terminationReason": reason}
                self.assertEqual(handle("antigravity", "Stop", payload)["decision"], "stop")
                self.assertTrue(self.sessions.get(key("antigravity", "test-session"))["paused"])

    def test_background_work_is_not_forced_to_retry(self):
        self.agy["fullyIdle"] = False
        self.assertEqual(handle("antigravity", "Stop", self.agy)["decision"], "stop")
        self.assertEqual(self.sessions.get(key("antigravity", "test-session"))["retries"], 0)

    def test_live_check_does_not_consume_retry_budget(self):
        run = self.store.begin(self.task, "check")
        self.assertEqual(handle("antigravity", "Stop", self.agy)["decision"], "stop")
        self.assertEqual(self.sessions.get(key("antigravity", "test-session"))["retries"], 0)
        self.store.finish(run, {"status": "interrupted", "returncode": None})

    def test_verified_task_stops_and_accepts_next_task(self):
        execute(self.store, self.task, "check")
        self.assertEqual(handle("antigravity", "Stop", self.agy)["decision"], "stop")
        new_task = self.store.create(self.root, self.store.task(self.task)["spec"])
        self.sessions.bind(key("antigravity", "test-session"), new_task)
        self.assertEqual(self.sessions.get(key("antigravity", "test-session"))["task_id"], new_task)
        self.assertIsNone(self.sessions.for_task(new_task)[0]["last_stop"])

    def test_native_context_fields_are_preserved(self):
        agy = handle("antigravity", "PreInvocation", self.agy)
        cli = handle("gemini-cli", "BeforeAgent", {**self.cli, "hook_event_name": "BeforeAgent"})
        self.assertIn("ephemeralMessage", agy["injectSteps"][0])
        self.assertIn("additionalContext", cli["hookSpecificOutput"])
        self.assertNotIn("llm_request", json.dumps(cli))

    def test_unbound_sessions_have_no_effect(self):
        self.agy["conversationId"] = "another-session"
        self.assertEqual(handle("antigravity", "Stop", self.agy), {"decision": "stop"})

    def test_invalid_contracts_and_path_injection_are_rejected(self):
        for changes in ({"workspacePaths": None}, {"workspacePaths": [1]},
                        {"workspacePaths": ["relative"]}, {"fullyIdle": "true"},
                        {"conversationId": "../../other"}, {"executionNum": True}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                handle("antigravity", "Stop", {**self.agy, **changes})

    def test_rebind_does_not_clear_pause_or_retry_count(self):
        session = key("antigravity", "test-session")
        self.sessions.nudge(session, "one")
        self.sessions.pause(session, "사용자가 중단했습니다.")
        self.sessions.bind(session, self.task)
        self.assertTrue(self.sessions.get(session)["paused"])
        self.assertEqual(self.sessions.get(session)["retries"], 1)

    def test_hook_subprocess_outputs_only_json_and_redacts_bad_payload(self):
        cmd = [sys.executable, "-m", "gtg.hooks", "antigravity", "Stop"]
        good = subprocess.run(cmd, cwd=ROOT, input=json.dumps(self.agy), capture_output=True, text=True)
        self.assertEqual(good.returncode, 0)
        self.assertEqual(json.loads(good.stdout)["decision"], "continue")
        bad = subprocess.run(cmd, cwd=ROOT, input="secret-value-invalid-json", capture_output=True, text=True)
        self.assertEqual(json.loads(bad.stdout), {"decision": "stop"})
        self.assertNotIn("secret-value", bad.stderr + bad.stdout)

    def test_retry_exhaustion_is_persisted_and_not_reported_as_completion(self):
        for number in range(3):
            response = handle("antigravity", "Stop", {**self.agy, "executionNum": number})
        self.assertEqual(response["decision"], "stop")
        state = self.sessions.get(key("antigravity", "test-session"))
        self.assertTrue(state["paused"])
        self.assertIn("상한", state["reason"])

    def test_gemini_retry_flag_false_cannot_create_an_endless_loop(self):
        for number in range(3):
            response = handle("gemini-cli", "AfterAgent", {**self.cli, "timestamp": str(number), "stop_hook_active": False})
        self.assertIs(response.get("continue"), False)
        self.assertIn("미검증", response.get("systemMessage", ""))
        self.assertTrue(self.sessions.get(key("gemini-cli", "test-session"))["paused"])

    def test_paused_context_keeps_the_session_id_needed_to_resume(self):
        self.sessions.pause(key("antigravity", "test-session"), "사용자 응답 대기")
        result = handle("antigravity", "PreInvocation", {**self.agy, "invocationNum": 0})
        self.assertIn("test-session", str(result))

    def test_duplicate_last_retry_does_not_pause_the_inflight_attempt(self):
        handle("antigravity", "Stop", self.agy)
        handle("antigravity", "Stop", {**self.agy, "executionNum": 1})
        handle("antigravity", "Stop", {**self.agy, "executionNum": 1})
        self.assertFalse(self.sessions.get(key("antigravity", "test-session"))["paused"])
        self.assertEqual(self.sessions.get(key("antigravity", "test-session"))["turn_open"], 1)

    def test_published_native_no_tool_call_reason_is_a_natural_stop(self):
        # 직접 실행 기록: https://atamel.dev/posts/2026/07-16_where_agy_hooks/
        payload = {**self.agy, "terminationReason": "NO_TOOL_CALL", "error": ""}
        self.assertEqual(handle("antigravity", "Stop", payload)["decision"], "continue")
        state = self.sessions.get(key("antigravity", "test-session"))
        self.assertEqual(state["retries"], 1)
        self.assertFalse(state["paused"])

    def test_stop_metadata_is_visible_without_recording_error_or_prompt_text(self):
        payload = {**self.agy, "terminationReason": "error", "error": "synthetic-private-error",
                   "prompt": "synthetic-private-prompt"}
        handle("antigravity", "Stop", payload)
        row = next(row for row in self.sessions.for_task(self.task) if row["key"] == key("antigravity", "test-session"))
        self.assertEqual(row["last_stop"], {"event": "Stop", "execution_num": 0,
                                          "termination_reason": "error", "fully_idle": True, "has_error": True})
        self.assertNotIn("synthetic-private", json.dumps(row))

    def test_native_reason_does_not_override_host_error_or_background_work(self):
        session = key("antigravity", "test-session")
        payload = {**self.agy, "terminationReason": "NO_TOOL_CALL", "fullyIdle": False}
        self.assertEqual(handle("antigravity", "Stop", payload)["decision"], "stop")
        self.assertFalse(self.sessions.get(session)["paused"])
        self.assertEqual(self.sessions.get(session)["retries"], 0)
        payload.update(fullyIdle=True, error="synthetic-error")
        self.assertEqual(handle("antigravity", "Stop", payload)["decision"], "stop")
        self.assertTrue(self.sessions.get(session)["paused"])
        self.assertEqual(self.sessions.get(session)["retries"], 0)

    def test_stop_metadata_omits_freeform_reason_and_gemini_prompt(self):
        handle("antigravity", "Stop", {**self.agy, "terminationReason": "message with private data"})
        handle("gemini-cli", "AfterAgent", {**self.cli, "prompt": "synthetic-private-prompt"})
        rows = self.sessions.for_task(self.task)
        agy = next(r for r in rows if r["key"] == key("antigravity", "test-session"))
        cli = next(r for r in rows if r["key"] == key("gemini-cli", "test-session"))
        self.assertIsNone(agy["last_stop"]["termination_reason"])
        self.assertEqual(cli["last_stop"], {"event": "AfterAgent", "stop_hook_active": False})
        self.assertNotIn("private", json.dumps(rows))

    def test_older_session_schema_keeps_task_pause_and_retry_state(self):
        db = self.store.connection
        db.execute("DROP TABLE sessions")
        db.execute("""CREATE TABLE sessions (
            key TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
            paused INTEGER NOT NULL DEFAULT 0, retries INTEGER NOT NULL DEFAULT 0,
            last_event TEXT, reason TEXT NOT NULL DEFAULT '')""")
        session = key("antigravity", "test-session")
        db.execute("INSERT INTO sessions VALUES (?, ?, 1, 2, 'previous-event', '사용자 응답 대기')", (session, self.task))
        db.commit()
        for _ in range(2):
            migrated = Sessions(self.store)
            row = migrated.get(session)
            self.assertEqual((row["task_id"], row["paused"], row["retries"], row["last_event"], row["reason"]),
                             (self.task, 1, 2, "previous-event", "사용자 응답 대기"))
            self.assertIsNone(migrated.for_task(self.task)[0]["last_stop"])


if __name__ == "__main__":
    unittest.main()
```
