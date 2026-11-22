# Gemini 4 Hydrogen — 비판적 평가·쓸 때와 쓰지 않을 때
> 제공자: Google · 모델 ID: `gemini-4-hydrogen` · 기준일: 2026-11-19 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: [`md/03-gemini/gemini-4-hydrogen/GEMINI.md`](../../../md/03-gemini/gemini-4-hydrogen/GEMINI.md)
> 소제목의 번호(2.x)는 주제별로 나누기 전 일반 조사 기록의 번호다. 문장 속 `§2.x`는 그 번호를 가리킨다.

#### 2.4 비판적 평가 (대부분 벤더 수치, 독립 측정은 얕음)
- **수치는 모두 Google 보고다.** Artificial Analysis 지수는 인용 값이고 HLE-Diamond 58.8%, Vals Tax Agent Bench 52.3%, Agents' Last Exam v1.1 71.6%, Agent Arena 5위 같은 항목은 Google이 고른 벤치마크다. 안전 수치(에이전트 과잉 행동 최대 81% 감소, 내부 정직성 평가 94%)도 내부 평가다. [부분, 벤더 주장]
- **속도·토큰 개선은 익명 파트너 사례다.** AI Studio 파트너가 2~2.8배 속도, 12~23% 낮은 토큰 사용을 보고했지만 파트너·워크로드가 공개되지 않았다. [부분]
- **Argon을 넘었다는 주장은 지수 1점 차이다.** 51 대 50이고 `xhigh`에서도 54다. 오차를 감안하면 같은 급으로 본다. 코딩 과제에서 직접 비교한다. [추정]
- **환각은 남아 있다.** Google 스스로 여전히 환각을 일으킨다고 적었고 3.8 Flash 대비 5배 감소라는 비교 기준은 자체 평가다. [확인/부분]
- **이 저장소의 Gemini 계열 경고는 그대로다.** 전역 규칙 무시, 없는 사실 날조 사례를 근거로 여전히 권장하지 않는다. 더 나은 대안이 있으면 쓰지 않는다.

#### 2.5 쓸 때와 쓰지 않을 때
- 쓴다: 값싸고 빠른 반복 에이전트 작업, 초안·분류·추출 같은 가벼운 작업, 멀티모달 입력(비디오·오디오) 처리, Antigravity의 실행 모델.
- 쓰지 않는다: 가장 어려운 장시간 추론·보안 작업(Carbon 또는 다른 계열), 사실 정확성이 결과를 좌우하는 조사, 검증 없이 쓰는 코드 생성.

## 재확인 (2026-11-19, 웹 검색, 사용자·후기 글)
- 독립 개발자 후기는 얕다. 초기 접근자는 Antigravity에서 "꽤 빠르고 꽤 좋다"(날아다니는 도시를 만들게 함)고 썼다. MindStudio는 Gemini 4 세 모델(Hydrogen, Argon, Carbon)이 코딩 에이전트 벤치마크에서 Anthropic·OpenAI에 뒤진다고 주장하되 Google은 가격과 도달 범위에서 이긴다고 봤다. 환각을 직접 시험한 후기는 없다. 지침 강화(읽기 규율)는 사용자 보고에 근거한 것이며 이 후기들이 확인해 주지는 않는다. [부분] ([MindStudio](https://www.mindstudio.ai/blog/is-google-behind-in-ai-coding-race), [pasqualepillitteri](https://pasqualepillitteri.it/en/news/33146/what-people-are-building-gemini-4-hydrogen-first-24-hours))
