# Gemini 4 Neon · 앱 — 조사 기록
> 제공자: Google · 모델 ID: `gemini-4-neon` · 기준일: 2026-11-22 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사·검증 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: [`md/03-gemini/gemini-4-neon/app.md`](../../../../md/03-gemini/gemini-4-neon/app.md)
> 절 번호는 지침 문서의 번호를 따른다(§1 분야 규칙, §2 이 모델의 분야 운용). 응답 계약과 작업 원칙은 전역 지침(AGENTS·CLAUDE·GEMINI.md)이 맡는다.
> 분야 규칙의 근거 수준 표기 원본: [`docs/_common/domain-rules/app.md`](../../../_common/domain-rules/app.md)

## 2. 이 모델의 앱 작업 운용
Gemini 4 Neon은 2026-11-18에 출시됐다. 사양과 가격은 상위 폴더의 [`overview.md`](../overview.md)를 따른다 [확인]. 이 분야의 Neon 전용 측정은 없고 전용 항목은 출시 직후 2차 보도와 초기 후기에서 가져온 것이다. 전용 항목이 없으면 `03-gemini/gemini-4-carbon/` 문서의 같은 분야 규칙을 기준선으로 삼는다. 같다는 보장은 없다. [추정]

**아직 확인하지 못한 것**
- 모바일·데스크톱 빌드·서명 도구와의 호환, 컴퓨터 사용 지원, 긴 세션의 비용를 같은 과제로 Gemini 4 Carbon와 비교한다.
- 모델 카드의 평가 조건과 지식 컷오프는 열지 않았다. 이 문서의 어떤 문장도 이 분야의 성능을 단정하지 않는다.
- **단계 수에 상한을 둔다.** 한 작업에 177단계를 쓰고 입력 토큰이 크다. 코딩 에이전트 지수는 58.6으로 최상위권이다. [부분: 2차 글이 옮긴 코딩 에이전트 지수]
- **낮은 effort 결과를 일반화하지 않는다.** `xhigh` 한 가지 구성만 측정됐다. [부분: 2차 글이 옮긴 코딩 에이전트 지수]
- **점수의 상당 부분이 Antigravity 하네스에서 나온다.** 다른 하네스에서는 결과가 크게 낮을 수 있으므로 쓰는 하네스로 직접 시험한다. [부분: 보도]
- **설계는 더 강한 모델이 하고 구현 위임에 쓴다.** 초기 사용자 평에서 Carbon보다 품질은 낮지만 훨씬 빠르고 비용이 약 절반이다. [부분: HN 초기 후기 2건]

## 4. 근거와 한계
- 상태와 출처: 상위 폴더의 [`sources.md`](../sources.md) 참조. Google 출시 글과 모델·가격 페이지를 읽었다. [확인]
- 관찰 출처(2차 전언): [https://www.testingcatalog.com/google-prepares-to-release-gemini-4-neon-model-on-apis/](https://www.testingcatalog.com/google-prepares-to-release-gemini-4-neon-model-on-apis/) [부분]
- 기준선 규칙: 같은 저장소의 `03-gemini/gemini-4-carbon/app.md`.
- 추가 확인(2026-11-19 웹 검색): [Orcarouter: Gemini 4 Neon과 Coding Agent Index](https://www.orcarouter.ai/blog/gemini-4-neon-coding-agent-index)
- 추가 확인(2026-11-19 웹 검색): [The New Stack: Gemini 4 Neon과 Antigravity 하네스](https://thenewstack.io/gemini-neon-antigravity-harness/)
- 추가 확인(2026-11-19 해외 커뮤니티·포럼): [Hacker News: Gemini 4 Neon 스레드](https://news.ycombinator.com/item?id=50552424)
- 한계: 이 분야에서 Gemini 4 Neon을 독립적으로 평가한 자료는 찾지 못했다. 전용 항목은 출시 직후 보도와 후기 기반이다.
