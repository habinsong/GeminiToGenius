# `tests/test_coverage.py`

- 형식: `100644`
- 바이트: 22906
- SHA-256: `cb38c14c9e27aa6dde2ea77ed0dc55141ac86a925dd42e253b07917db70830c2`
- 인코딩: `utf-8`

```
"""검사가 실제로 실행한 검증 대상 파일을 기록하고, 실행하지 않은 범위를 사실로 표시합니다."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.certificate import build
from gtg.coverage import collector, executed_watch
from gtg.runner import execute, status
from gtg.store import Store


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_python_subprocess_execution_is_recorded(self):
        used = self.root / "used.py"
        unused = self.root / "unused.py"
        used.write_text("VALUE = 1\n")
        unused.write_text("VALUE = 2\n")
        entry = self.root / "entry.py"
        entry.write_text("import used\nassert used.VALUE == 1\n")
        with collector() as session:
            done = subprocess.run([sys.executable, "entry.py"], cwd=self.root,
                                  env=session.environment(), capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            files = session.files()
        self.assertIn(used.resolve(), files)
        self.assertIn(entry.resolve(), files)
        self.assertNotIn(unused.resolve(), files)

    def test_nested_python_subprocess_is_also_recorded(self):
        inner = self.root / "inner.py"
        inner.write_text("VALUE = 3\n")
        child = self.root / "child.py"
        child.write_text("import inner\n")
        parent = self.root / "parent.py"
        parent.write_text(f"import subprocess, sys\nsubprocess.run([sys.executable, {str(child)!r}], check=True)\n")
        with collector() as session:
            subprocess.run([sys.executable, "parent.py"], cwd=self.root, env=session.environment(), check=True)
            files = session.files()
        self.assertIn(inner.resolve(), files)

    def test_existing_sitecustomize_still_runs(self):
        other = self.root / "site-extra"
        other.mkdir()
        marker = self.root / "marker.txt"
        (other / "sitecustomize.py").write_text(f"open({str(marker)!r}, 'w').write('ran')\n")
        with collector() as session:
            environment = session.environment()
            environment["PYTHONPATH"] = environment["PYTHONPATH"] + ":" + str(other)
            subprocess.run([sys.executable, "-c", "pass"], cwd=self.root, env=environment, check=True)
            session.files()
        self.assertEqual(marker.read_text(), "ran", "기존 sitecustomize를 가리면 안 됩니다.")

    def test_no_python_execution_reports_nothing_observed(self):
        with collector() as session:
            subprocess.run(["/bin/echo", "hi"], cwd=self.root, env=session.environment(),
                           capture_output=True, check=True)
            self.assertEqual(session.files(), set())
            self.assertFalse(session.observed())

    def test_isolated_interpreter_reports_nothing_instead_of_failing(self):
        (self.root / "thing.py").write_text("VALUE = 1\n")
        with collector() as session:
            for flag in ("-I", "-E", "-S"):
                with self.subTest(flag=flag):
                    done = subprocess.run([sys.executable, flag, "-c", "pass"], cwd=self.root,
                                          env=session.environment(), capture_output=True)
                    self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(session.files(), set(), "격리 모드는 관찰되지 않으며 오류도 아닙니다.")

    def test_large_watch_scope_is_capped_instead_of_walking_forever(self):
        from gtg.coverage import MAX_WATCHED_FILES, watched_code_files

        big = self.root / "many"
        big.mkdir()
        for index in range(MAX_WATCHED_FILES + 25):
            (big / f"module_{index:05d}.py").write_text("X = 1\n")
        found, opaque = watched_code_files(self.root, ["many"])
        self.assertEqual(len(found), MAX_WATCHED_FILES)
        self.assertFalse(opaque)

    def test_capped_scope_does_not_claim_unexecuted_files(self):
        from gtg.coverage import MAX_WATCHED_FILES, executed_watch

        big = self.root / "wide"
        big.mkdir()
        for index in range(MAX_WATCHED_FILES + 3):
            (big / f"mod_{index:05d}.py").write_text("X = 1\n")
        ran, missed = executed_watch(self.root, ["wide"], set())
        self.assertEqual(ran, [])
        self.assertIsNone(missed, "범위를 다 세지 못하면 미실행을 주장하지 않습니다.")

    def test_nested_collectors_still_chain_to_the_user_sitecustomize(self):
        """관찰기 안에서 관찰기가 또 돌아도 사용자 sitecustomize를 건너뛰지 않습니다."""
        other = self.root / "site-extra"
        other.mkdir()
        marker = self.root / "nested-marker.txt"
        (other / "sitecustomize.py").write_text(f"open({str(marker)!r}, 'w').write('ran')\n")
        with collector() as outer:
            outer_environment = outer.environment()
            with collector() as inner:
                environment = {**outer_environment, **inner.environment()}
                environment["PYTHONPATH"] = (inner.environment()["PYTHONPATH"] + os.pathsep
                                             + outer_environment["PYTHONPATH"] + os.pathsep + str(other))
                (self.root / "work.py").write_text("VALUE = 1\n")
                done = subprocess.run([sys.executable, "-c", "import work; assert work.VALUE == 1"],
                                      cwd=self.root, env=environment, capture_output=True, text=True)
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertIn((self.root / "work.py").resolve(), inner.files())
        self.assertEqual(marker.read_text(), "ran", "중첩 시 사용자 sitecustomize가 실행되어야 합니다.")

    def test_watch_split_only_covers_python_files(self):
        (self.root / "pkg").mkdir()
        (self.root / "pkg/a.py").write_text("A = 1\n")
        (self.root / "pkg/b.py").write_text("B = 1\n")
        (self.root / "pkg/data.txt").write_text("not python\n")
        ran, missed = executed_watch(self.root, ["pkg"], {(self.root / "pkg/a.py").resolve()})
        self.assertEqual(ran, ["pkg/a.py"])
        self.assertEqual(missed, ["pkg/b.py"])


def spec(argv):
    return {"schema_version": 1, "goal": "실행 범위를 기록합니다.", "checks": [
        {"id": "only", "criterion": "등록한 검사가 통과합니다.", "argv": argv,
         "watch": ["touched.py", "untouched.py", "check.py"]}]}


class RunnerCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        (self.workspace / "touched.py").write_text("def value():\n    return 1\n")
        (self.workspace / "untouched.py").write_text("def other():\n    return 2\n")
        (self.workspace / "check.py").write_text("from touched import value\nassert value() == 1\n")
        self.store = Store(self.workspace / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)

    def test_passing_check_records_the_file_it_never_executed(self):
        task = self.store.create(self.workspace, spec([sys.executable, "check.py"]))
        result = execute(self.store, task, "only")
        self.assertEqual(result["status"], "passed")
        self.assertTrue(result["coverage_observed"])
        self.assertEqual(result["executed_watch"], ["check.py", "touched.py"])
        self.assertEqual(result["unexecuted_watch"], ["untouched.py"])

    def test_non_python_command_does_not_claim_anything_unexecuted(self):
        task = self.store.create(self.workspace, spec(["/bin/sh", "-c", "exit 0"]))
        result = execute(self.store, task, "only")
        self.assertEqual(result["status"], "passed")
        self.assertFalse(result["coverage_observed"])
        self.assertIsNone(result["unexecuted_watch"])

    def test_status_and_certificate_carry_the_unverified_scope(self):
        task = self.store.create(self.workspace, spec([sys.executable, "check.py"]))
        execute(self.store, task, "only")
        report = status(self.store, task)
        self.assertEqual(report["checks"][0]["unexecuted_watch"], ["untouched.py"])
        document = build(self.store, task)
        self.assertTrue(document["verified"])
        self.assertEqual(document["checks"][0]["unexecuted_watch"], ["untouched.py"])
        self.assertEqual(document["unverified_scope"], ["untouched.py"])

    def test_unobservable_check_marks_the_scope_as_incomplete(self):
        task = self.store.create(self.workspace, spec(["/bin/sh", "-c", "exit 0"]))
        execute(self.store, task, "only")
        document = build(self.store, task)
        self.assertTrue(document["verified"])
        self.assertEqual(document["unverified_scope"], [])
        self.assertFalse(document["coverage_complete"],
                         "관찰하지 못한 검사가 있으면 빈 목록을 전부 검증으로 읽히게 두지 않습니다.")

    def test_observed_check_marks_the_scope_as_complete(self):
        task = self.store.create(self.workspace, spec([sys.executable, "check.py"]))
        execute(self.store, task, "only")
        document = build(self.store, task)
        self.assertTrue(document["coverage_complete"])
        self.assertEqual(document["unverified_scope"], ["untouched.py"])

    def test_replay_passes_the_scope_and_its_completeness_through(self):
        from gtg.certificate import replay

        task = self.store.create(self.workspace, spec([sys.executable, "check.py"]))
        execute(self.store, task, "only")
        report = replay(build(self.store, task), self.workspace)
        self.assertTrue(report["reconstructed"])
        self.assertEqual(report["unverified_scope"], ["untouched.py"])
        self.assertTrue(report["coverage_complete"])

    def test_replay_verdict_is_three_valued(self):
        from gtg.certificate import replay

        task = self.store.create(self.workspace, spec([sys.executable, "check.py"]))
        execute(self.store, task, "only")
        document = build(self.store, task)
        self.assertEqual(replay(document, self.workspace)["verdict"], "pass")

        (self.workspace / "touched.py").write_text("def value():\n    return 99\n")
        broken = replay(document, self.workspace)
        self.assertEqual(broken["verdict"], "invalid")
        self.assertFalse(broken["reconstructed"])

    def test_incomplete_coverage_is_inconclusive_not_pass(self):
        from gtg.certificate import replay

        task = self.store.create(self.workspace, spec(["/bin/sh", "-c", "exit 0"]))
        execute(self.store, task, "only")
        document = build(self.store, task)
        report = replay(document, self.workspace)
        self.assertTrue(report["reconstructed"], "명령 자체는 재현됩니다.")
        self.assertFalse(report["coverage_complete"])
        self.assertEqual(report["verdict"], "inconclusive")

    def test_unverified_task_replays_as_invalid(self):
        from gtg.certificate import replay

        task = self.store.create(self.workspace, spec([sys.executable, "check.py"]))
        document = build(self.store, task)
        self.assertFalse(document["verified"])
        self.assertEqual(replay(document, self.workspace)["verdict"], "invalid")

    def test_a_file_executed_by_any_check_is_not_listed_as_unverified(self):
        document = {"schema_version": 1, "goal": "두 검사", "checks": []}
        document = {"schema_version": 1, "goal": "두 검사가 범위를 나눠 덮습니다.", "checks": [
            {"id": "first", "criterion": "첫 검사", "argv": [sys.executable, "check.py"],
             "watch": ["touched.py", "untouched.py", "check.py"]},
            {"id": "second", "criterion": "둘째 검사",
             "argv": [sys.executable, "-c", "import untouched; assert untouched.other() == 2"],
             "watch": ["untouched.py"]}]}
        task = self.store.create(self.workspace, document)
        execute(self.store, task, "first")
        execute(self.store, task, "second")
        certificate = build(self.store, task)
        self.assertTrue(certificate["verified"])
        self.assertEqual(certificate["unverified_scope"], [])


if __name__ == "__main__":
    unittest.main()


class JavaScriptCoverageTests(unittest.TestCase):
    """Node 실행도 같은 방식으로 관찰합니다. Node가 없으면 건너뜁니다."""

    @classmethod
    def setUpClass(cls):
        import shutil as _shutil
        if _shutil.which("node") is None:
            raise unittest.SkipTest("node를 찾지 못했습니다.")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        (self.workspace / "used.js").write_text("module.exports = { value: 1 };\n")
        (self.workspace / "unused.js").write_text("module.exports = { value: 2 };\n")
        (self.workspace / "check.js").write_text(
            "const used = require('./used.js');\nif (used.value !== 1) { throw new Error('bad'); }\n")
        self.store = Store(self.workspace / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)

    def js_spec(self, watch):
        return {"schema_version": 1, "goal": "자바스크립트 실행을 관찰합니다.", "checks": [
            {"id": "node", "criterion": "노드 검사가 통과합니다.",
             "argv": ["node", "check.js"], "watch": watch}]}

    def test_node_execution_is_recorded_like_python(self):
        task = self.store.create(self.workspace, self.js_spec(["used.js", "unused.js", "check.js"]))
        result = execute(self.store, task, "node")
        self.assertEqual(result["status"], "passed")
        self.assertTrue(result["coverage_observed"])
        self.assertEqual(result["executed_watch"], ["check.js", "used.js"])
        self.assertEqual(result["unexecuted_watch"], ["unused.js"])

    def test_esm_modules_are_recorded(self):
        (self.workspace / "lib.mjs").write_text("export const value = 3;\n")
        (self.workspace / "main.mjs").write_text(
            "import { value } from './lib.mjs';\nif (value !== 3) { throw new Error('bad'); }\n")
        (self.workspace / "spare.mjs").write_text("export const other = 4;\n")
        spec = {"schema_version": 1, "goal": "ESM을 관찰합니다.", "checks": [
            {"id": "esm", "criterion": "ESM 검사가 통과합니다.", "argv": ["node", "main.mjs"],
             "watch": ["lib.mjs", "main.mjs", "spare.mjs"]}]}
        task = self.store.create(self.workspace, spec)
        result = execute(self.store, task, "esm")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["executed_watch"], ["lib.mjs", "main.mjs"])
        self.assertEqual(result["unexecuted_watch"], ["spare.mjs"])

    def test_existing_node_options_are_preserved(self):
        import os as _os
        from gtg.coverage import collector

        with collector() as session:
            previous = dict(_os.environ)
            try:
                _os.environ["NODE_OPTIONS"] = "--max-old-space-size=512"
                environment = session.environment()
            finally:
                _os.environ.clear()
                _os.environ.update(previous)
        self.assertIn("--max-old-space-size=512", environment["NODE_OPTIONS"])
        self.assertIn("--require", environment["NODE_OPTIONS"])

    def test_unobservable_code_in_scope_is_not_silently_treated_as_covered(self):
        (self.workspace / "typed.ts").write_text("export const value: number = 1;\n")
        task = self.store.create(self.workspace, self.js_spec(["used.js", "check.js", "typed.ts"]))
        result = execute(self.store, task, "node")
        self.assertEqual(result["status"], "passed")
        self.assertIsNone(result["unexecuted_watch"],
                          "관찰할 수 없는 코드가 범위에 있으면 미실행을 주장하지 않습니다.")
        document = build(self.store, task)
        self.assertFalse(document["coverage_complete"])

    def test_data_files_in_scope_do_not_block_completeness(self):
        (self.workspace / "notes.md").write_text("설명 문서입니다.\n")
        (self.workspace / "config.json").write_text("{}\n")
        task = self.store.create(self.workspace, self.js_spec(["used.js", "unused.js", "check.js", "notes.md", "config.json"]))
        execute(self.store, task, "node")
        document = build(self.store, task)
        self.assertTrue(document["coverage_complete"])
        self.assertEqual(document["unverified_scope"], ["unused.js"])


class TypeScriptScopeTests(unittest.TestCase):
    """TypeScript는 네이티브로 실행될 때만 관찰됩니다. 실행 방식은 관측으로 판단합니다."""

    @classmethod
    def setUpClass(cls):
        import shutil as _shutil
        if _shutil.which("node") is None:
            raise unittest.SkipTest("node를 찾지 못했습니다.")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        (self.workspace / "lib.ts").write_text("export function double(n: number): number { return n * 2; }\n")
        (self.workspace / "spare.ts").write_text("export function unused(n: number): number { return n + 1; }\n")
        (self.workspace / "main.ts").write_text(
            "import { double } from './lib.ts';\nif (double(2) !== 4) { throw new Error('bad'); }\n")
        self.store = Store(self.workspace / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)

    def test_natively_executed_typescript_is_measured(self):
        spec = {"schema_version": 1, "goal": "TypeScript를 직접 실행합니다.", "checks": [
            {"id": "ts", "criterion": "타입스크립트 검사가 통과합니다.", "argv": ["node", "main.ts"],
             "watch": ["lib.ts", "main.ts", "spare.ts"]}]}
        task = self.store.create(self.workspace, spec)
        result = execute(self.store, task, "ts")
        if result["status"] != "passed":
            self.skipTest("이 Node는 TypeScript를 직접 실행하지 않습니다.")
        self.assertEqual(result["executed_watch"], ["lib.ts", "main.ts"])
        self.assertEqual(result["unexecuted_watch"], ["spare.ts"],
                         "네이티브 실행이 관측되면 나머지는 실제로 실행되지 않은 것입니다.")
        self.assertTrue(build(self.store, task)["coverage_complete"])

    def test_compiled_workflow_does_not_claim_typescript_was_unexecuted(self):
        (self.workspace / "built.js").write_text("module.exports = { double: (n) => n * 2 };\n")
        (self.workspace / "check.js").write_text(
            "const { double } = require('./built.js');\nif (double(2) !== 4) { throw new Error('bad'); }\n")
        spec = {"schema_version": 1, "goal": "컴파일 산출물을 실행합니다.", "checks": [
            {"id": "compiled", "criterion": "빌드 산출물 검사가 통과합니다.", "argv": ["node", "check.js"],
             "watch": ["lib.ts", "spare.ts", "built.js", "check.js"]}]}
        task = self.store.create(self.workspace, spec)
        result = execute(self.store, task, "compiled")
        self.assertEqual(result["status"], "passed")
        self.assertIsNone(result["unexecuted_watch"],
                          "TypeScript 실행이 관측되지 않으면 미실행을 주장하지 않습니다.")
        self.assertFalse(build(self.store, task)["coverage_complete"])


class RewritingLoaderTests(unittest.TestCase):
    """pytest처럼 소스를 재작성해 불러오는 러너에서도 관찰이 유지되는지 확인합니다.

    pytest를 설치하지 않고, 같은 위험 요소인 커스텀 MetaPathFinder와 어설션 재작성을
    직접 재현합니다. 관건은 재작성된 코드 객체의 `co_filename`이 실제 파일을 가리키는지입니다.
    """

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "target.py").write_text("def add(a, b):\n    return a + b\n")
        (self.root / "spare.py").write_text("def unused():\n    return 0\n")
        (self.root / "runner.py").write_text('''
import ast, importlib.abc, importlib.util, sys
from pathlib import Path


class Rewriter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """소스를 AST로 다시 컴파일해 실행합니다. pytest의 어설션 재작성과 같은 구조입니다."""

    def find_spec(self, name, path, target=None):
        source = Path(name + ".py")
        if not source.is_file():
            return None
        return importlib.util.spec_from_file_location(name, str(source.resolve()), loader=self)

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        path = module.__spec__.origin
        tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=path)
        ast.fix_missing_locations(tree)
        exec(compile(tree, path, "exec"), module.__dict__)


sys.meta_path.insert(0, Rewriter())
import target
assert target.add(1, 2) == 3
print("rewritten ok")
''')

    def test_rewritten_modules_are_still_observed(self):
        with collector() as session:
            done = subprocess.run([sys.executable, "runner.py"], cwd=self.root,
                                  env=session.environment(), capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("rewritten ok", done.stdout)
            files = session.files()
        self.assertIn((self.root / "target.py").resolve(), files,
                      "재작성된 모듈도 실제 파일 경로로 관찰되어야 합니다.")
        self.assertNotIn((self.root / "spare.py").resolve(), files)

    def test_runner_style_check_reports_the_untouched_file(self):
        spec = {"schema_version": 1, "goal": "재작성 러너로 검사합니다.", "checks": [
            {"id": "rewritten", "criterion": "재작성 러너가 통과합니다.",
             "argv": [sys.executable, "runner.py"], "watch": ["target.py", "spare.py", "runner.py"]}]}
        store = Store(self.root / ".gtg/state.sqlite3")
        self.addCleanup(store.close)
        task = store.create(self.root, spec)
        result = execute(store, task, "rewritten")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["executed_watch"], ["runner.py", "target.py"])
        self.assertEqual(result["unexecuted_watch"], ["spare.py"])
```
