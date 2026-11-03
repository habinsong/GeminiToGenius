"""스킬 참조 문서의 '고치기 전/고친 뒤' 예시가 문체 검사기와 어긋나지 않는지 확인합니다.

모델은 이 예시를 보고 따라 합니다. 정답으로 보여 준 문장이 검사기에 걸리면 모델이 걸리는 문장을 배우고, 검사기가 잡는다고
한 나쁜 예가 실제로는 안 잡히면 문서와 검사기 중 하나가 낡은 것입니다. 명사 쌓기나 용어 병기처럼 검사 대상이 아닌 예시는
검사기에 걸릴 것을 요구하지 않고, 걸려야 하는 예시만 아래 표에 적습니다.
"""

from pathlib import Path
import re
import unittest

from gtg.prose import examine


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = {
    "profile/skills/gtg-writing/references/korean.md": "general",
    "profile/skills/gtg-korean-academic/references/academic.md": "academic",
    "profile/skills/gtg-korean-everyday/references/everyday.md": "everyday",
    "profile/skills/gtg-korean-literary/references/literary.md": "literary",
}
BEFORE, AFTER = ("고치기 전", "AI가 쓰기 쉬운 답"), ("고친 뒤", "사람이 쓰는 답")
LINE = re.compile(r"^- (고치기 전|고친 뒤|AI가 쓰기 쉬운 답|사람이 쓰는 답): (.+)$", re.M)
# 걸려야 하는 나쁜 예: (예시에 든 말, 그 예시가 보여 주는 버릇을 잡아야 하는 규칙)
MUST_BE_FLAGGED = (
    ("설치가 끝났습니다. 설정 파일을 엽니다.", "rhythm-choppy"),
    ("중요한 것은 속도가 아니라 방향이고", "ko-antithesis-chain"),
    ("에 의해 제안되었으며", "academic-agent-passive"),
    ("문제는 데이터의 양이 아니라 질이며", "ko-antithesis-chain"),
    ("새로운 지평", "ko-hype-phrase"),
    ("늦은 회신에 대해 진심으로 사과드립니다", "everyday-stiff-notice"),
    ("정말 힘들었겠다. 그런 마음이 드는 건 당연해", "everyday-empathy"),
    ("나오셨습니다", "everyday-object-honorific"),
    ("금일 모임 장소", "everyday-stiff-notice"),
    ("분위기가 정말 좋았어요!", "everyday-exclaim"),
    ("좋은 질문 감사드립니다", "ko-chatbot"),
    ("형언할 수 없는 슬픔", "literary-ineffable"),
    ("비로소 깨달았다", "literary-epiphany"),
    ("시간이 멈춘 듯했다", "literary-emotion-cliche"),
    ("바람이 불고,\n잎이 지고,", "literary-line-comma"),
)


def pairs():
    """(파일, 갈래, 고치기 전, 고친 뒤) 목록입니다. 시의 행은 ' / '로 이어 적은 백틱 구간들을 줄바꿈으로 되돌립니다."""
    found = []
    for name, register in REFERENCES.items():
        before = None
        for label, rest in LINE.findall((ROOT / name).read_text(encoding="utf-8")):
            spans = re.findall(r"`([^`]+)`", rest)
            text = ("\n" if " / " in rest else " ").join(spans)
            if label in BEFORE:
                before = text
            elif before is not None:
                found.append((name, register, before, text))
                before = None
    return found


def signals(text, register):
    return examine("example.md", text, register)[0]


class ExampleTests(unittest.TestCase):
    def test_the_references_still_hold_enough_examples_to_check(self):
        self.assertGreaterEqual(len(pairs()), 20, "예시 형식이 바뀌어 읽지 못한 것이 아닌지 확인하세요.")

    def test_every_corrected_example_passes_without_the_signals_its_bad_example_had(self):
        for name, register, before, after in pairs():
            with self.subTest(file=Path(name).name, before=before[:30]):
                bad = {item["id"] for item in signals(before, register)}
                good = signals(after, register)
                self.assertEqual([item["id"] for item in good if item["severity"] == "block"], [])
                self.assertEqual({item["id"] for item in good} & bad, set(), "고친 뒤 문장에 같은 버릇이 남아 있습니다.")

    def test_bad_examples_that_claim_to_show_a_detectable_habit_are_detected(self):
        everything = pairs()
        for needle, rule in MUST_BE_FLAGGED:
            with self.subTest(example=needle[:24], rule=rule):
                matching = [(register, before) for _, register, before, _ in everything if needle in before]
                self.assertTrue(matching, "참조 문서에서 이 예시를 찾지 못했습니다. 표를 고치세요.")
                for register, before in matching:
                    self.assertIn(rule, {item["id"] for item in signals(before, register)})


if __name__ == "__main__":
    unittest.main()
