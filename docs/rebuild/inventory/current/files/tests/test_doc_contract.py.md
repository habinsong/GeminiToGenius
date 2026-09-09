# `tests/test_doc_contract.py`

- 형식: `100644`
- 바이트: 4245
- SHA-256: `4a581926847879ff2c10dec83a0822302836856f04b9e6a9c69ef3324263b1bb`
- 인코딩: `utf-8`

````
"""배포하는 안내 문서의 명령·인자가 실제 CLI 계약과 어긋나면 실패합니다.

실제 모델은 이 문서를 읽고 명령을 만듭니다. 문서가 구현보다 낡으면 모델이 실패합니다.
"""

import argparse
from pathlib import Path
import re
import shlex
import unittest

from gtg.__main__ import build_parser


ROOT = Path(__file__).resolve().parents[1]
RUNNER = re.compile(r'(?:"\$GTG_RUNNER"|\$GTG_RUNNER|[\w./<>_-]*run\.py)\s+(.*)')
DOCS = [ROOT / "README.md", *sorted((ROOT / "profile").rglob("*.md"))]


def parser_contract() -> tuple[dict[str, set[str]], set[str]]:
    parser = build_parser()
    subparsers = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)][0]
    globals_ = {option for action in parser._actions for option in action.option_strings}
    commands = {name: {option for action in sub._actions for option in action.option_strings}
                for name, sub in subparsers.choices.items()}
    return commands, globals_


def documented_calls(text: str) -> list[tuple[str, list[str]]]:
    calls = []
    for block in re.findall(r"```bash\n(.*?)```", text, re.S):
        for line in block.splitlines():
            line = line.strip()
            match = RUNNER.search(line)
            if not match or line.startswith("#"):
                continue
            try:
                tokens = shlex.split(match[1])
            except ValueError:
                continue
            if tokens:
                calls.append((line, tokens))
    return calls


class DocumentedCommandTests(unittest.TestCase):
    def setUp(self):
        self.commands, self.global_options = parser_contract()

    def test_documentation_actually_contains_runner_examples(self):
        total = sum(len(documented_calls(path.read_text(encoding="utf-8"))) for path in DOCS)
        self.assertGreaterEqual(total, 8, "안내 문서에서 실행 예시를 찾지 못했습니다.")

    def test_every_documented_command_and_flag_exists(self):
        for path in DOCS:
            for line, tokens in documented_calls(path.read_text(encoding="utf-8")):
                with self.subTest(doc=path.name, line=line):
                    leading = [token for token in tokens if token.startswith("--")]
                    rest = list(tokens)
                    while rest and rest[0].startswith("--"):
                        option = rest.pop(0)
                        self.assertIn(option, self.global_options, f"전역 옵션이 아닙니다: {option}")
                        if rest and not rest[0].startswith("--"):
                            rest.pop(0)
                    self.assertTrue(rest, f"명령 이름이 없습니다: {line}")
                    name = rest.pop(0)
                    self.assertIn(name, self.commands, f"등록되지 않은 명령입니다: {name}")
                    allowed = self.commands[name] | self.global_options
                    for token in rest:
                        if token.startswith("--"):
                            self.assertIn(token.split("=", 1)[0], allowed,
                                          f"{name} 명령에 없는 인자입니다: {token}")
                    del leading

    def test_a_stale_flag_is_detected(self):
        sample = '```bash\npython3 "$GTG_RUNNER" status TASK_ID --no-such-flag\n```\n'
        calls = documented_calls(sample)
        self.assertEqual(len(calls), 1)
        tokens = calls[0][1]
        self.assertNotIn("--no-such-flag", self.commands[tokens[0]] | self.global_options)

    def test_every_command_is_documented_somewhere(self):
        used = set()
        for path in DOCS:
            for _, tokens in documented_calls(path.read_text(encoding="utf-8")):
                rest = list(tokens)
                while rest and rest[0].startswith("--"):
                    rest.pop(0)
                    if rest and not rest[0].startswith("--"):
                        rest.pop(0)
                if rest:
                    used.add(rest[0])
        missing = sorted(set(self.commands) - used)
        self.assertEqual(missing, [], f"안내 문서에 예시가 없는 명령입니다: {missing}")


if __name__ == "__main__":
    unittest.main()
````
