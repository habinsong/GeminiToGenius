"""AST 측정이 빈 본문·단순 전달·추상화·응집도를 실제 코드 모양대로 구분하는지 확인합니다."""

import textwrap
import unittest

from gtg.code_shape import complexity, shape
import ast


def measured(source: str) -> dict:
    return shape(textwrap.dedent(source))


class CodeShapeTests(unittest.TestCase):
    def functions(self, source):
        return {f["qualname"]: f for f in measured(source)["functions"]}

    def test_every_placeholder_body_is_a_stub_but_real_work_is_not(self):
        found = self.functions('''
            def only_pass():
                pass

            def only_ellipsis():
                ...

            def only_docstring():
                """나중에 채웁니다."""

            def not_implemented(value):
                raise NotImplementedError("later")

            def returns_value():
                return 1

            def raises_other():
                raise ValueError("bad input")
        ''')
        for name in ("only_pass", "only_ellipsis", "only_docstring", "not_implemented"):
            self.assertTrue(found[name]["stub"], name)
        for name in ("returns_value", "raises_other"):
            self.assertFalse(found[name]["stub"], name)

    def test_abstract_and_overload_markers_are_recorded(self):
        found = self.functions('''
            from abc import ABC, abstractmethod
            from typing import overload

            class Port(ABC):
                @abstractmethod
                def send(self, data): ...

            @overload
            def parse(value: int) -> int: ...
        ''')
        self.assertTrue(found["Port.send"]["abstract_marker"])
        self.assertTrue(found["parse"]["abstract_marker"])

    def test_pass_through_requires_every_argument_forwarded_unchanged(self):
        found = self.functions('''
            def total(items, start=0):
                return sum(items, start)

            def same(items, start=0):
                return total(items, start)

            def renamed_keyword(items, start=0):
                return total(items, start=start)

            def changed(items, start=0):
                return total(items, start + 1)

            def dropped(items, start=0):
                return total(items)

            def variadic(*args, **kwargs):
                return total(*args, **kwargs)
        ''')
        self.assertEqual(found["same"]["forwards_to"], "total")
        self.assertEqual(found["renamed_keyword"]["forwards_to"], "total")
        self.assertEqual(found["variadic"]["forwards_to"], "total")
        self.assertIsNone(found["changed"]["forwards_to"], "인자를 가공하면 전달 함수가 아닙니다.")
        self.assertIsNone(found["dropped"]["forwards_to"], "받은 인자를 버리면 전달 함수가 아닙니다.")
        self.assertEqual(found["total"]["forwards_to"], "sum", "내장 함수에 이름만 붙인 함수도 검토 대상입니다.")

    def test_class_kinds_and_wrapper_detection(self):
        classes = {c["name"]: c for c in measured('''
            import abc
            from typing import Protocol

            class Base(abc.ABC):
                pass

            class Meta(metaclass=abc.ABCMeta):
                pass

            class Hidden:
                def run(self):
                    raise NotImplementedError

            class Port(Protocol):
                def send(self, data): ...

            class Wrapper:
                def __init__(self, client):
                    self.client = client
                def get(self, key):
                    return self.client.get(key)
                def put(self, key, value):
                    return self.client.put(key, value)

            class Worker:
                def __init__(self):
                    self.count = 0
                def add(self, value):
                    self.count += value
                    return self.count
        ''')["classes"]}
        self.assertTrue(classes["Base"]["abstract"])
        self.assertTrue(classes["Meta"]["abstract"])
        self.assertTrue(classes["Hidden"]["abstract"], "NotImplementedError만 던지는 메서드도 추상 지점입니다.")
        self.assertTrue(classes["Port"]["protocol"])
        self.assertTrue(classes["Wrapper"]["wrapper"])
        self.assertFalse(classes["Worker"]["wrapper"])
        self.assertFalse(classes["Worker"]["abstract"])

    def test_cohesion_separates_shared_state_from_unrelated_methods(self):
        classes = {c["name"]: c for c in measured('''
            class Together:
                def a(self):
                    return self.value
                def b(self):
                    self.value = 2
                def c(self):
                    return self.value + 1

            class Apart:
                def a(self):
                    return self.first
                def b(self):
                    return self.second
                def c(self):
                    return self.third

            class Single:
                def only(self):
                    return self.value
        ''')["classes"]}
        self.assertEqual(classes["Together"]["tcc"], 1.0)
        self.assertEqual(classes["Apart"]["tcc"], 0.0)
        self.assertIsNone(classes["Single"]["tcc"], "메서드가 하나면 응집도를 계산하지 않습니다.")

    def test_complexity_counts_branches_but_not_nested_definitions(self):
        tree = ast.parse(textwrap.dedent('''
            def decide(a, b, items):
                if a and b:
                    return 1
                for item in items:
                    if item:
                        continue
                def inner(x):
                    if x:
                        return 1
                    return 0
                return [x for x in items if x]
        '''))
        # 1 + if + and + for + if + comprehension(for) + comprehension(if); inner의 if는 따로 셉니다.
        self.assertEqual(complexity(tree.body[0]), 7)

    def test_exports_and_top_level_names(self):
        result = measured('''
            __all__ = ["public"]

            def public():
                return 1

            @decorator
            def registered():
                return 2

            class Thing:
                pass
        ''')
        self.assertEqual(result["exported"], {"public"})
        self.assertEqual(set(result["top_level"]), {"public", "registered", "Thing"})
        self.assertTrue(result["top_level"]["registered"]["decorated"])

    def test_syntax_error_is_not_swallowed(self):
        with self.assertRaises(SyntaxError):
            shape("def broken(:\n    pass\n")


if __name__ == "__main__":
    unittest.main()
