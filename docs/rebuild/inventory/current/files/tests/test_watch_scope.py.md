# `tests/test_watch_scope.py`

- 형식: `100644`
- 바이트: 7419
- SHA-256: `b0bd4df2ddaabfb82dff4a24f421bbcfd5918675f12a0002f0de4d9b2d30baa7`
- 인코딩: `utf-8`

```
"""훅은 5초 안에 상태를 만들어야 하므로 검증 대상 범위에 상한을 둡니다."""

from pathlib import Path
import sys
import tempfile
import time
import unittest

from gtg.spec import MAX_WATCH_BYTES, MAX_WATCH_FILES, fingerprint, scope_size
from gtg.runner import status
from gtg.store import Store


def spec(watch):
    return {"schema_version": 1, "goal": "검증 범위를 확인합니다.", "checks": [
        {"id": "only", "criterion": "검사가 통과합니다.",
         "argv": [sys.executable, "-c", "pass"], "watch": watch}]}


class ScopeSizeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def spread(self, count, size=16):
        folder = self.root / "deps"
        folder.mkdir(exist_ok=True)
        for index in range(count):
            (folder / f"f{index:05d}.js").write_text("x" * size)

    def test_small_scope_is_measured(self):
        (self.root / "a.py").write_text("A = 1\n")
        (self.root / "b.py").write_text("B = 2\n")
        files, size = scope_size(self.root, ["a.py", "b.py"])
        self.assertEqual(files, 2)
        self.assertGreater(size, 0)

    def test_missing_paths_do_not_fail_measurement(self):
        (self.root / "a.py").write_text("A = 1\n")
        files, _ = scope_size(self.root, ["a.py", "not-created-yet.py"])
        self.assertEqual(files, 1)

    def test_too_many_files_are_refused_with_a_clear_reason(self):
        self.spread(MAX_WATCH_FILES + 50)
        with self.assertRaisesRegex(ValueError, "검증 대상"):
            scope_size(self.root, ["deps"])

    def test_too_many_bytes_are_refused(self):
        big = self.root / "blob"
        big.mkdir()
        chunk = "y" * (1024 * 1024)
        for index in range(4):
            (big / f"part{index}.bin").write_text(chunk)
        with self.assertRaisesRegex(ValueError, "검증 대상"):
            scope_size(self.root, ["blob"], max_bytes=2 * 1024 * 1024)

    def test_measurement_is_much_cheaper_than_hashing(self):
        self.spread(4000, size=512)
        started = time.monotonic()
        scope_size(self.root, ["deps"])
        measured = time.monotonic() - started
        started = time.monotonic()
        fingerprint(self.root, ["deps"])
        hashed = time.monotonic() - started
        self.assertLess(measured, hashed, "범위 측정이 해싱보다 싸야 등록 단계에서 쓸 수 있습니다.")


class RegistrationBoundTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "src.py").write_text("VALUE = 1\n")
        self.store = Store(self.root / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)

    def test_oversized_scope_is_rejected_at_registration(self):
        folder = self.root / "vendor"
        folder.mkdir()
        for index in range(MAX_WATCH_FILES + 20):
            (folder / f"m{index:05d}.js").write_text("x")
        with self.assertRaisesRegex(ValueError, "검증 대상"):
            self.store.create(self.root, spec(["vendor"]))

    def test_normal_scope_is_accepted(self):
        self.assertTrue(self.store.create(self.root, spec(["src.py"])))

    def test_scope_that_grows_later_marks_the_check_stale_instead_of_crashing(self):
        task = self.store.create(self.root, spec(["src.py", "vendor"]))
        run = self.store.begin(task, "only")
        self.store.finish(run, {"status": "passed", "returncode": 0,
                                "before": "x" * 64, "after": fingerprint(self.root, ["src.py", "vendor"])})
        self.assertEqual(status(self.store, task)["checks"][0]["status"], "passed")
        folder = self.root / "vendor"
        folder.mkdir(exist_ok=True)
        for index in range(MAX_WATCH_FILES + 20):
            (folder / f"m{index:05d}.js").write_text("x")
        report = status(self.store, task)
        self.assertEqual(report["checks"][0]["status"], "stale")
        self.assertFalse(report["verified"], "범위가 커져도 훅은 살아 있고 완료로 보고하지 않습니다.")

    def test_documented_limits_are_reasonable_for_the_hook_budget(self):
        self.assertGreaterEqual(MAX_WATCH_FILES, 5000)
        self.assertLessEqual(MAX_WATCH_FILES, 50000)
        self.assertGreaterEqual(MAX_WATCH_BYTES, 32 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()


class TaskWideBudgetTests(unittest.TestCase):
    """훅은 작업의 모든 검사를 한 번에 처리하므로 예산도 작업 단위여야 합니다."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.store = Store(self.root / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)

    def folder(self, name, count):
        target = self.root / name
        target.mkdir(exist_ok=True)
        for index in range(count):
            (target / f"f{index:05d}.py").write_text("X = 1\n")
        return name

    def task(self, *scopes):
        return {"schema_version": 1, "goal": "여러 검사가 범위를 나눠 봅니다.", "checks": [
            {"id": f"c{index}", "criterion": "검사입니다.", "argv": [sys.executable, "-c", "pass"],
             "watch": list(scope)} for index, scope in enumerate(scopes)]}

    def test_each_check_under_the_limit_but_the_task_over_it_is_refused(self):
        share = MAX_WATCH_FILES // 2 + 100
        a, b, c = self.folder("a", share), self.folder("b", share), self.folder("c", 10)
        with self.assertRaisesRegex(ValueError, "검증 대상"):
            self.store.create(self.root, self.task([a], [b], [c]))

    def test_repeated_identical_scopes_are_counted_once(self):
        share = MAX_WATCH_FILES // 2 + 100
        a = self.folder("a", share)
        # 같은 범위는 상태 조회에서 한 번만 해싱되므로 예산도 한 번만 씁니다.
        self.assertTrue(self.store.create(self.root, self.task([a], [a], [a])))

    def test_ordinary_task_with_several_scopes_is_accepted(self):
        src, tests = self.folder("src", 300), self.folder("tests", 120)
        self.assertTrue(self.store.create(self.root, self.task([src], [src, tests], [tests])))

    def test_refusal_states_the_real_limit_not_the_remaining_budget(self):
        share = MAX_WATCH_FILES // 2 + 100
        a, b = self.folder("a", share), self.folder("b", share)
        with self.assertRaises(ValueError) as caught:
            self.store.create(self.root, self.task([a], [b]))
        message = str(caught.exception)
        self.assertIn(str(MAX_WATCH_FILES), message,
                      "남은 예산이 아니라 실제 상한을 알려 주어야 모델이 올바르게 좁힙니다.")
        self.assertIn(str(MAX_WATCH_BYTES // (1024 * 1024)), message)

    def test_task_scope_reports_the_measured_total(self):
        from gtg.spec import task_scope

        src, tests = self.folder("src", 40), self.folder("tests", 25)
        files, size = task_scope(self.root, self.task([src], [src, tests])["checks"])
        self.assertEqual(files, 40 + 65, "서로 다른 범위는 각각 해싱되므로 각각 셉니다.")
        self.assertGreater(size, 0)
```
