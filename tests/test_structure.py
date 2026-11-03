"""구조 검사가 이번 변경에서 생긴 문제만 차단하고, 기존 코드나 판단이 필요한 신호는 검토로 남기는지 확인합니다."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from gtg.structure import review


ROOT = Path(__file__).resolve().parents[1]


def lines(count: int, prefix: str = "value") -> str:
    return "".join(f"{prefix}_{i} = {i}\n" for i in range(count))


class StructureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git("init", "-q")

    def git(self, *args):
        subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "-c", "commit.gpgsign=false",
                        "-C", str(self.root), *args], check=True, capture_output=True)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text), encoding="utf-8")

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "base", "--allow-empty")

    def kinds(self, result, severity=None):
        return [(f["kind"], f["symbol"]) for f in result["findings"] if severity in (None, f["severity"])]

    def test_new_marker_blocks_but_existing_marker_and_lookalikes_do_not(self):
        self.write("app.py", "def run():\n    # TODO: old note\n    return 1\n")
        self.commit()
        self.write("app.py", """\
            def run():
                # TODO: old note
                return 1


            def export(rows):
                todo_items = list(rows)  # 소문자 todo 목록은 표식이 아닙니다.
                # TODO: CSV 쓰기
                return todo_items


            EXAMPLE = "# TODO: 문자열 안의 표식은 주석이 아닙니다"
            print(export([EXAMPLE]))
        """)
        self.write("ui.js", 'input.placeholder = "검색";\n// 추후 구현: 정렬\n')
        result = review(self.root)
        markers = [(f["path"], f["line"]) for f in result["findings"] if f["kind"] == "placeholder-marker"]
        self.assertEqual(markers, [("app.py", 8), ("ui.js", 2)])
        self.assertFalse(result["passed"])
        self.assertEqual(result["structure_unanalyzed"], ["ui.js"], "Python 외 언어는 분석 범위를 밝힙니다.")

    def test_stub_body_blocks_unless_it_is_a_declared_abstract_point_with_real_implementations(self):
        self.write("base.py", "")
        self.commit()
        self.write("base.py", """\
            from abc import ABC, abstractmethod


            class Store(ABC):
                @abstractmethod
                def save(self, row): ...


            class Memory(Store):
                def save(self, row):
                    return [row]


            class Disk(Store):
                def save(self, row):
                    return str(row)


            def export(rows):
                pass


            class Report:
                def render(self):
                    raise NotImplementedError


            class Shape:
                def area(self):
                    raise NotImplementedError


            class Square(Shape):
                def area(self):
                    return 4


            class Circle(Shape):
                def area(self):
                    return 3
        """)
        result = review(self.root)
        blocked = self.kinds(result, "block")
        self.assertIn(("placeholder-body", "export"), blocked)
        self.assertIn(("placeholder-body", "Report.render"), blocked, "하위 클래스가 없는 클래스의 NotImplementedError는 미완성입니다.")
        self.assertNotIn(("placeholder-body", "Store.save"), blocked)
        self.assertNotIn(("placeholder-body", "Shape.area"), blocked, "실제 하위 클래스가 구현하는 기반 메서드는 막지 않습니다.")
        self.assertNotIn(("single-implementation", "Store"), self.kinds(result))

    def test_single_implementation_and_pass_through_are_review_only(self):
        self.write("core.py", "def total(items):\n    return sum(items)\n")
        self.commit()
        self.write("core.py", """\
            from abc import ABC, abstractmethod


            def total(items):
                return sum(items)


            def compute_total(items):
                return total(items)


            class Exporter(ABC):
                @abstractmethod
                def export(self, rows): ...


            class CsvExporter(Exporter):
                def export(self, rows):
                    return ",".join(rows)


            print(compute_total([1]), CsvExporter().export(["a"]))
        """)
        result = review(self.root)
        self.assertTrue(result["passed"], result["findings"])
        self.assertIn(("single-implementation", "Exporter"), self.kinds(result, "review"))
        self.assertIn(("pass-through", "compute_total"), self.kinds(result, "review"))

    def test_bug_fix_in_large_file_passes_but_new_feature_there_blocks(self):
        self.write("legacy.py", lines(450))
        self.commit()
        self.write("legacy.py", lines(450).replace("value_3 = 3", "value_3 = 4"))
        self.assertTrue(review(self.root)["passed"], "큰 파일의 기존 줄 수정은 막지 않습니다.")
        self.write("legacy.py", lines(450) + "\n\ndef new_feature():\n    return value_1\n")
        result = review(self.root)
        oversized = [f for f in result["findings"] if f["kind"] == "oversized-file"]
        self.assertEqual(len(oversized), 1)
        self.assertEqual((oversized[0]["severity"], oversized[0]["measure"]["reason"]), ("block", "grew"))

    def test_crossing_the_line_limit_blocks_for_code_but_only_reviews_tests(self):
        self.write("module.py", lines(390))
        self.write("tests/test_module.py", lines(390, "case"))
        self.commit()
        self.write("module.py", lines(420))
        self.write("tests/test_module.py", lines(420, "case"))
        found = {f["path"]: f for f in review(self.root)["findings"] if f["kind"] == "oversized-file"}
        self.assertEqual(found["module.py"]["severity"], "block")
        self.assertEqual(found["module.py"]["measure"]["reason"], "crossed")
        self.assertEqual(found["tests/test_module.py"]["severity"], "review")

    def test_growing_a_large_class_blocks_and_untouched_large_class_is_ignored(self):
        methods = "".join(f"    def m{i}(self):\n        return {i}\n\n" for i in range(20))
        self.write("big.py", "class Big:\n" + methods + "\nclass Other:\n    def keep(self):\n        return 0\n")
        self.commit()
        self.write("big.py", "class Big:\n" + methods + "\nclass Other:\n    def keep(self):\n        return 1\n")
        self.assertNotIn("large-class", [k for k, _ in self.kinds(review(self.root))])
        self.write("big.py", "class Big:\n" + methods + "    def m20(self):\n        return 20\n"
                   + "\nclass Other:\n    def keep(self):\n        return 0\n")
        self.assertIn(("large-class", "Big"), self.kinds(review(self.root), "block"))

    def test_unreferenced_definition_is_reported_until_something_calls_it(self):
        self.write("tool.py", "")
        self.commit()
        self.write("tool.py", "def helper(value):\n    return value * 2\n")
        self.assertIn(("unreferenced", "helper"), self.kinds(review(self.root), "review"))
        self.write("main.py", "from tool import helper\nprint(helper(2))\n")
        self.assertNotIn(("unreferenced", "helper"), self.kinds(review(self.root)))

    def test_long_or_branchy_new_functions_are_reviewed_but_not_blocked(self):
        self.write("rules.py", "")
        self.commit()
        branches = "".join(f"    if value == {i}:\n        return {i}\n" for i in range(21))
        body = "".join(f"    total += {i}\n" for i in range(85))
        self.write("rules.py", "def pick(value):\n" + branches + "    return -1\n\n\n"
                   + "def add(total):\n" + body + "    return total\n\n\n"
                   + "def small(value):\n    return value + 1\n\n\nprint(pick(1), add(0), small(1))\n")
        result = review(self.root)
        reviewed = self.kinds(result, "review")
        self.assertIn(("long-function", "pick"), reviewed, "분기 복잡도 21 이상은 검토 신호입니다.")
        self.assertIn(("long-function", "add"), reviewed, "80줄을 넘는 함수는 검토 신호입니다.")
        self.assertNotIn(("long-function", "small"), reviewed)
        self.assertTrue(result["passed"])

    def test_syntax_error_in_changed_code_blocks(self):
        self.write("broken.py", "")
        self.commit()
        self.write("broken.py", "def broken(:\n    return 1\n")
        self.assertIn(("syntax-error", None), self.kinds(review(self.root), "block"))

    def test_untracked_files_count_but_ignored_files_do_not(self):
        self.write(".gitignore", "generated/\n")
        self.commit()
        self.write("new.py", "# FIXME: 마무리\nVALUE = 1\nprint(VALUE)\n")
        self.write("generated/out.py", "# TODO: 생성물\n")
        result = review(self.root)
        self.assertEqual(result["checked_files"], ["new.py"])
        self.assertEqual([f["path"] for f in result["findings"] if f["kind"] == "placeholder-marker"], ["new.py"])

    def test_pinned_base_keeps_the_task_scope_after_a_commit(self):
        self.write("app.py", "VALUE = 1\n")
        self.commit()
        start = subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"], capture_output=True,
                               text=True, check=True).stdout.strip()
        self.write("app.py", "VALUE = 1\n# TODO: 남은 일\n")
        self.commit()
        self.assertTrue(review(self.root)["passed"], "기본 기준(HEAD)은 커밋과 함께 움직입니다.")
        self.assertFalse(review(self.root, start)["passed"], "시작 커밋을 고정하면 작업 전체를 봅니다.")

    def test_repository_without_commits_checks_every_file(self):
        self.write("first.py", "def first():\n    pass\n")
        result = review(self.root)
        self.assertEqual(result["baseline"], "empty_repository")
        self.assertIn(("placeholder-body", "first"), self.kinds(result, "block"))

    def test_without_git_paths_are_required_and_every_line_is_new(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        plain = Path(outside.name).resolve()
        (plain / "script.py").write_text("# TODO: 시작\nprint(1)\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "지정"):
            review(plain)
        result = review(plain, "none", ["script.py"])
        self.assertEqual(result["baseline"], "none")
        self.assertFalse(result["passed"])

    def test_bad_base_and_paths_outside_the_workspace_are_rejected(self):
        self.write("app.py", "VALUE = 1\n")
        self.commit()
        for base in ("missing-revision", "--output=/tmp/x", " "):
            with self.subTest(base=base), self.assertRaises(ValueError):
                review(self.root, base)
        for path in ("../outside.py", "/etc/passwd", ".git/config"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                review(self.root, None, [path])
        with self.assertRaises(ValueError):
            review(self.root, max_lines=10)

    def test_cli_exit_code_follows_blocking_findings_only(self):
        self.write("app.py", "")
        self.commit()
        self.write("app.py", "def wrap(items):\n    return sorted(items)\n\nprint(wrap([2, 1]))\n")

        def run():
            process = subprocess.run([sys.executable, "-m", "gtg", "structure", "--workspace", str(self.root)],
                                     cwd=ROOT, capture_output=True, text=True,
                                     env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            return process.returncode, json.loads(process.stdout)

        code, report = run()
        self.assertEqual((code, report["blocking"]), (0, 0), "검토 신호만 있으면 통과입니다.")
        self.assertGreater(report["review"], 0)
        self.write("app.py", "def wrap(items):\n    pass\n")
        code, report = run()
        self.assertEqual(code, 1)
        self.assertFalse(report["passed"])


if __name__ == "__main__":
    unittest.main()
