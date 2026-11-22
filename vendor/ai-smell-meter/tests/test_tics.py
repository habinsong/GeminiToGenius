"""입버릇 낱말 규칙: 규칙마다 걸리는 글과 안 걸리는 글. 여러 번 나와야 세는 규칙은 반복해서 넣는다."""
import unittest

import _path  # noqa: F401
from ai_smell.detect import analyze
from ai_smell.rules import ko_tics

# (규칙 id, 걸려야 하는 한 문장, 걸리면 안 되는 한 문장, 반복 횟수)
CASES = [
    ("ko.tic.value-figurative", "그 일은 해 볼 값어치가 있다.", "입력값을 검증한다.", 1),
    ("ko.tic.value-bare", "값이 바뀐다. 값을 읽는다.", "기본값이 바뀐다. 반환값을 읽는다.", 5),
    ("ko.tic.judge", "그렇게 판단한다.", "그렇게 정한다.", 5),
    ("ko.tic.criterion-becomes", "이 수치가 기준이 된다.", "이 수치를 쓴다.", 2),
    ("ko.tic.criterion-bare", "기준을 정한다.", "조건을 정한다.", 6),
    ("ko.tic.test-heavy", "시험을 돌린다.", "검사를 돌린다.", 6),
    ("ko.tic.test-bench", "이번 일이 시험대에 올랐다.", "이번 일을 마쳤다.", 1),
    ("ko.tic.pivotal", "속도가 관건이다.", "속도가 필요하다.", 1),
    ("ko.tic.trail", "조건이 따라붙는다.", "조건이 있다.", 2),
    ("ko.tic.defer", "결정을 미뤘다.", "결정을 했다.", 2),
    ("ko.tic.crossover", "다음 주제로 넘어갑니다.", "다음 주제를 봅니다.", 3),
    ("ko.tic.continues", "문제가 다른 문제로 이어집니다.", "문제가 다른 문제를 낳는다.", 4),
    ("ko.tic.draw-line", "여기서 선을 긋는다.", "여기서 멈춘다.", 1),
    ("ko.tic.touch-up", "따로 손볼 곳이 없다.", "따로 고칠 곳이 없다.", 1),
    ("ko.tic.distinct", "차이가 뚜렷하게 확인됐다.", "차이가 컸다.", 1),
    ("ko.tic.weak-verdict", "초록은 약했으며 시는 약했다.", "초록은 점수가 낮았다.", 1),
    ("ko.tic.density", "표현 밀도를 본다.", "철의 밀도는 7.8 g/cm³이다.", 1),
    ("ko.tic.text-amount", "글 분량으로 나눈다.", "글자 수로 나눈다.", 1),
    ("ko.tic.weigh-up", "내용이 사실인지는 따지지 않는다.", "내용이 사실인지 묻지 않는다.", 1),
    ("ko.tic.between", "초록은 그 사이였다. 시는 둘 사이에 있다.", "초록은 중간이었다.", 1),
    ("ko.tic.degree-of", "구분 정도는 낮았다.", "얼마나 구분되는지 낮았다.", 1),
    ("ko.tic.whether", "사실 여부를 알 수 없다.", "사실인지 알 수 없다.", 1),
    ("ko.tic.not-look", "코드 블록과 URL은 보지 않았다.", "코드 블록과 URL은 보지않았다. 내용은 확인하지 않았다.", 1),
    ("ko.tic.freq-phrase", "출현 빈도를 센다.", "나온 횟수를 센다.", 1),
    ("ko.tic.computed-score", "산출 점수를 본다.", "계산한 점수를 본다.", 1),
    ("ko.tic.style-pattern", "문체 패턴을 본다.", "말투를 본다.", 1),
    ("ko.tic.detail-adj", "세부적인 한계를 적는다.", "자세한 한계를 적는다.", 1),
    ("ko.format.middle-dot", "코드·URL·표를 뺀다.", "코드와 URL과 표를 뺀다.", 1),
    ("ko.tic.reveal", "차이를 드러낸다.", "차이를 보여 준다.", 1),
    ("ko.tic.signal-bare", "신호를 찾는다. 신호로는 부족하다.", "표현을 찾는다.", 1),
    ("ko.tic.compare-with", "두 글을 견주어 본다.", "두 글을 비교한다.", 1),
    ("ko.tic.purpose", "비교하는 용도다.", "비교에 쓴다.", 1),
    ("ko.tic.skip", "코드는 건너뛴다.", "코드는 제외한다.", 1),
    ("ko.tic.reproduce", "결과가 재현됐다.", "결과가 다시 나왔다.", 1),
    ("ko.tic.ask-back", "필자에게 되묻는다. 되묻지 않는다.", "필자에게 묻는다.", 1),
    ("ko.tic.put-in-criteria", "탐지기 통과는 기준에 넣지 않는다.", "탐지기 통과는 쓰지 않는다.", 1),
    ("ko.tic.put-keep", "그대로 둔다. 표는 둔다.", "그대로 남긴다. 표는 쓴다.", 1),
    ("ko.tic.fit-to", "기준에 맞춘다. 표본에 맞추지 않는다.", "기준에 따른다.", 1),
    ("ko.tic.score-bare", "점수가 높다.", "시험점수가 높다.", 1),
    ("ko.tic.local", "걸린 곳만 국소 수정한다.", "병원에서 국소 마취를 했다.", 1),
    ("ko.tic.count-verb", "표현을 센다. 점수에 세지 않는다. 지금도 세고 있다.", "나이를 센다. 숫자를 세어 본다. 표현을 헤아린다.", 1),
    ("ko.tic.habit-speech", "모델의 입버릇을 센다.", "모델이 자주 쓰는 표현을 본다.", 1),
    ("ko.tic.sentence-frame", "문장틀을 본다. 문장 틀도 본다.", "문장 구조를 본다.", 1),
    ("ko.tic.dash-word", "줄표를 줄인다.", "쉼표를 줄인다.", 1),
    ("ko.tic.neutral", "이 도구는 모델 중립이다.", "중립국이다. 정치적 중립을 지킨다.", 1),
    ("ko.tic.lean-on", "점수에 기댄다. 규칙에 기대지 않는다.", "벽에 기댄다. 친구에게 기댄다.", 1),
    ("ko.tic.approx", "이 기준은 근삿값이다.", "이 기준은 근삿값 8어절이다. 근사값은 0.5다.", 1),
    ("ko.tic.measured-value", "이 값은 측정한 값이다.", "측정한 값은 3.2%다. 측정값 8어절을 쓴다.", 1),
    ("ko.tic.heavy-light", "이 문장은 무겁다.", "가방이 무겁다. 3kg이라 가볍다.", 1),
    ("ko.tic.measure-any", "효과를 재지 않았다.", "방의 길이를 잰다.", 1),
    ("ko.tic.limit-open", "한계는 여기에 있다.", "여기서는 안 된다.", 1),
    ("ko.tic.limit-bare", "한계가 있다. 한계를 적는다.", "안 되는 곳이 있다.", 1),
    ("ko.tic.work-done", "하는 일과 하지 않는 일을 나눈다.", "하는 동작과 쓰는 규칙을 나눈다.", 1),
    ("ko.tic.not-do", "표를 쓰지 않는다. 줄표를 늘리지 않는다.", "표를 쓴다. 줄표를 줄인다.", 1),
    ("ko.tic.index-bare", "점수 대신 지수를 쓴다.", "물가지수와 주가 지수를 본다. 지수 함수를 쓴다.", 1),
    ("ko.tic.who-text", "사람 글과 AI 글을 비교한다.", "사람이 쓴 글과 AI가 쓴 글을 비교한다.", 1),
    ("ko.tic.structure-habit", "구조 습관이 남았다.", "구조가 남았다.", 1),
    ("ko.tic.false-detect", "오탐과 미탐이 있다.", "오탐지와 미탐지가 있다.", 1),
    ("ko.tic.seem", "정규식으로 잘 안 보인다. 효과가 있어 보인다.", "카메라로 멀리 보인다. 눈에 보인다.", 1),
    ("ko.tic.come-out", "결과가 나왔다. 오탐이 나오지 않았다.", "그가 문으로 나왔다. 건물에서 나온다.", 1),
    ("ko.tic.prior-bare", "전 수치는 같은 자료에서 뺀 것이다.", "수정 전 수치는 같다. 모든 수치를 쓴다.", 1),
    ("ko.tic.piece", "위키백과 조각을 뺐다.", "케이크 조각을 먹었다. 부품 조각을 모은다.", 1),
    ("ko.tic.listen", "필자의 말을 듣는다. 지시를 듣지 않는다.", "이어폰으로 음악을 듣는다. 귀로 듣는다.", 1),
    ("ko.tic.pair-up", "두 글을 짝지어 비교한다. 짝을 이루어 쓴다.", "두 글을 대응시켜 비교한다.", 1),
    ("ko.tic.holdout", "홀드아웃에서 확인했다.", "검증 자료에서 확인했다.", 1),
    ("ko.tic.leave", "필자의 문체를 남긴다. 흔적을 남기지 않는다.", "일부러 조금 남긴다. 식당에서 음식을 남겼다.", 1),
    ("ko.tic.point-at", "논문이 짚은 방향과 같다. 문제를 짚는다.", "지팡이를 짚는다. 맥을 짚었다.", 1),
    ("ko.tic.fathom", "연결 단절은 따로 헤아린다. 지수에 헤아리지 않는다.", "그의 마음을 헤아린다. 아픔을 헤아렸다.", 1),
    ("ko.tic.open-data", "공개 자료로 확인했다.", "공개된 자료로 확인했다.", 1),
    ("ko.tic.replace-with", "아래 자료로 갈음했다.", "아래 자료로 대신했다.", 1),
    ("ko.tic.link-word", "이음말을 넣는다.", "이어지는 말을 넣는다.", 1),
    ("ko.tic.gap-arises", "둘 사이에 차이가 난다.", "둘 사이에 차이가 발생한다. 차이가 확인된다.", 1),
    ("ko.tic.reach", "한 번도 안 닿는 값이다. 닿은 값을 쓴다.", "손이 벽에 닿았다. 물에 닿는다.", 1),
    ("ko.tic.personify", "시간이 말했다. 침묵이 속삭였다.", "그가 말했다. 방이 조용했다.", 1),
    ("ko.tic.realize", "그는 비로소 깨달았다.", "그는 문을 열었다.", 1),
    ("ko.tic.object-honorific", "커피 나오셨습니다.", "커피 나왔습니다.", 1),
    ("ko.tic.win-lose", "이 모델이 이겼다. 저 모델은 밀렸다.", "이 모델이 앞선다.", 1),
    ("ko.tic.stand", "그 모델이 우위에 선다. 저 모델은 뒤에 섭니다.", "의자에 앉는다.", 1),
    ("ko.tic.exceed", "기준을 웃돈다.", "기준에 못 미친다.", 2),
    ("ko.tic.put-forward", "장점을 내세운다.", "장점을 쓴다.", 2),
    ("ko.tic.claim", "그렇게 주장한다.", "그렇게 말한다.", 5),
    ("ko.tic.demand", "조건을 요구한다.", "조건을 둔다.", 5),
    ("ko.tic.widen", "범위를 넓힌다.", "범위가 넓다.", 2),
    ("ko.tic.apply", "규칙을 적용한다.", "규칙을 쓴다.", 5),
    ("ko.tic.dress-up", "보고를 그럴듯하게 꾸민다.", "보고를 쓴다.", 2),
    ("ko.tic.back-up", "자료가 주장을 뒷받침한다.", "자료가 주장에 힘을 싣는다.", 2),
    ("ko.tic.adapt", "환경에 적응한다.", "환경에 맞춘다.", 3),
    ("ko.term.release", "릴리스 노트를 쓴다.", "릴리즈 노트를 쓴다.", 1),
    ("ko.term.harness", "하니스를 만든다. 하네즈도 만든다.", "하네스를 만든다.", 1),
    ("ko.term.synthesizer", "신시사이저를 켠다.", "신디사이저를 켠다.", 1),
    ("ko.tic.corpus", "말뭉치에서 고른다.", "자료에서 고른다.", 1),
    ("ko.tic.shape", "경로는 이런 모양입니다.", "경로는 이렇게 씁니다.", 1),
    ("ko.tic.unrelated", "이 숫자는 지침의 뜻과는 상관이 없습니다.", "이 숫자는 정렬에 씁니다.", 1),
    ("ko.tic.whole", "전체 목록을 본다. 계열 전체를 본다.", "목록을 본다.", 4),
    ("ko.tic.contract-word", "응답 계약을 따른다.", "공통 규칙을 따른다.", 1),
    ("ko.tic.same-as", "어느 문서든 같은 순서로 이루어져 있습니다.", "어느 문서든 순서가 있습니다.", 1),
    ("ko.tic.among", "답은 세 가지 중 하나다.", "답은 하나다.", 2),
    ("ko.tic.empty-answer", "빈 답변이 돌아왔다.", "답이 돌아왔다.", 2),
]


class TicRules(unittest.TestCase):
    def test_every_rule_has_a_case(self):
        self.assertEqual({r.id for r in ko_tics.RULES}, {c[0] for c in CASES})

    def test_cases(self):
        for rid, pos, neg, n in CASES:
            hit = {f.rule_id for f in analyze((pos + " ") * n).findings}
            miss = {f.rule_id for f in analyze((neg + " ") * n).findings}
            with self.subTest(rule=rid):
                self.assertIn(rid, hit, f"걸려야 한다: {pos!r}")
                self.assertNotIn(rid, miss, f"걸리면 안 된다: {neg!r}")

    def test_only_the_fixed_spellings_edit_text(self):
        for r in ko_tics.RULES:
            if r.id in ("ko.term.release", "ko.term.harness", "ko.term.synthesizer"):
                self.assertEqual(r.tier, "safe", r.id)
            else:
                self.assertEqual(r.tier, "none", r.id)


if __name__ == "__main__":
    unittest.main()
