# Gemini 4 Argon · 네이티브 — 조사 기록
> 제공자: Google · 모델 ID: `gemini-4-argon` · 기준일: 2026-11-03 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사·검증 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: [`md/03-gemini/gemini-4-argon/native.md`](../../../../md/03-gemini/gemini-4-argon/native.md)
> 절 번호는 지침 문서의 번호를 따른다(§1 분야 규칙, §2 이 모델의 분야 운용). 응답 계약과 작업 원칙은 전역 지침(AGENTS·CLAUDE·GEMINI.md)이 맡는다.
> 분야 규칙의 근거 수준 표기 원본: [`docs/_common/domain-rules/native.md`](../../../_common/domain-rules/native.md)

## 2. 이 모델의 네이티브 작업 운용
모델 전체 특성은 상위 폴더의 [`README.md`](../README.md)가 안내하는 개요·운용·비판 문서를 따른다. 요약: Terminal-Bench 4.0에서 Opus 5.5에 뒤짐, 자기 검증이 약하다는 평가, 사이버 능력 안전장치, Gemini CLI는 Gemini 4에 비최적화.

- **시스템 코드의 핵심 변경은 상위 후보와 비교해서 맡긴다.** Terminal-Bench 4.0에서 Google 수치는 57.4%(발표 글은 57.1%)이고 같은 2차 정리에서 Claude Opus 5.5는 66.4%다. [부분] 메모리 관리, 동시성, ABI가 걸린 변경은 `opus-5.5`나 `gpt-6.1-sol` 문서와 같은 과제로 비교한 뒤 정한다.
- **자기 검증을 지시문으로 강제한다.** 이 모델은 자기 검증과 코드 재검토로 돌아가는 데 약하다는 후기가 있다. [부분] "변경 후 sanitizer 빌드와 해당 테스트를 돌리고 출력을 읽고, 실패하면 원인을 고쳐 다시 돌려라"를 시작에 적고, 돌리지 못한 검사는 "미실행"으로 보고하게 한다.
- **긴 자율 작업은 Google 시연을 근거로 삼지 않는다.** 20만 줄 파이썬 코드베이스를 밤새 최적화한 사례를 Google 개발자 블로그가 소개하지만 벤더 시연이다. [부분] 장시간 작업은 단계마다 테스트로 확인하고 `git diff`로 범위를 점검한다.
- **사이버 인접 작업의 경계.** 모델 카드는 사이버 보안 임계 능력에 도달했을 가능성을 배제할 수 없다며 안전장치를 적용한다고 한다. [부분] 침해 분석·리버스 엔지니어링·익스플로잇 같은 이중 용도 작업은 Fairwind 프로그램의 승인된 파트너에게만 열려 있다는 안내가 있어, 일반 접근에서는 거부될 수 있다. 사이버 변종 `gemini-4-argon-cyber-permissive`는 별도 변종이며 접근 조건을 확인한다. [부분/미확인]
- **도구 선택.** Gemini CLI는 Gemini 4 이후에 최적화돼 있지 않다고 README가 적는다. Antigravity CLI에서 쓰고 `AGENTS.md`로 지침을 둔다. [확인]
- **`thinking_level`을 명시한다.** 미정의 동작이 얽힌 디버깅은 `HIGH`, 컴파일 오류 분류는 `LOW`. `MINIMAL`은 400이다. 생각 토큰도 입출력 통합 한도를 쓴다. [부분]
- **테스트·경고·sanitizer 설정을 바꿔 통과시키지 않았는지 `git diff`로 확인한다.** 공개 헤더·ABI 변경은 호출자 영향부터 확인한다.
- **시스템 경로, 레지스트리, 드라이버, 부트 설정, 서명 키는 승인 없이 건드리지 않는다.**
- **테스트 통과를 안전 근거로 쓰지 않는다.** 테스트가 있는 544건의 통과율은 85.66%인데 취약점의 약 80%가 blocker·critical이었다. 보안 점검을 테스트와 별도 단계로 둔다. [확인: Sonar 벤치마크]
- **암호 설정과 시스템 자원 처리를 먼저 점검한다.** 취약점의 약 3분의 2가 암호 설정 오류(127건)와 시스템 자원의 불안전한 처리(81건)였고, 하드코딩된 자격 증명도 7건 나왔다. 정적 분석(SAST)을 이 두 영역부터 돌린다. [확인: Sonar 벤치마크]
- **동시성 버그를 따로 본다.** 버그 중 동시성·스레딩이 가장 많았다(58건, 17%). 스레드·비동기·인터럽트 코드는 경쟁 조건 점검(TSan 또는 리뷰)을 거친다. [확인: Sonar 벤치마크]
- **빈 응답을 완료로 세지 않는다.** 4,444건 중 69건(1.55%)이 쓸 수 있는 코드를 내지 않았다. 산출물 파일이 실제로 생겼는지 확인한다. [확인: Sonar 벤치마크]
- **실제 저장소 변경은 Carbon 이상으로 맡긴다.** 코딩 에이전트 지수의 저장소 변경 항목이 25로 낮다. 터미널과 코드 설명은 중간이다. [부분: 2차 글이 옮긴 코딩 에이전트 지수]
- **느리고 출력이 길므로 시간·토큰 상한을 둔다.** 한 작업이 30분 안팎이고 출력 토큰이 중앙값의 약 1.7배다. [확인: Artificial Analysis 모델 페이지]

## 4. 근거와 한계
- Terminal-Bench 비교·자기 검증: [Layer3 Labs 리뷰](https://www.layer3labs.io/guides/gemini-4-argon-review), [eesel.ai 리뷰](https://www.eesel.ai/blog/gemini-4-argon-review) [부분]
- 사이버 능력·Fairwind: [Fairwind Program](https://deepmind.google/fairwind-program/), [모델 카드](https://deepmind.google/models/model-cards/gemini-4-argon/) (스니펫만) [부분]
- Gemini CLI: [google-gemini/gemini-cli README](https://github.com/google-gemini/gemini-cli) [확인]
- 추가 확인(2026-11-19 웹 검색): [Sonar: Gemini 4 Argon 코드 평가](https://www.sonarsource.com/blog/google-gemini-4-argon-evaluation/)
- 추가 확인(2026-11-19 웹 검색): [Artificial Analysis Coding Agent Index v2.1 표(2차 정리)](https://freakyjolly.com/coding-agent-index-v2-1-explained/)
- 추가 확인(2026-11-19 웹 검색): [Artificial Analysis: gemini-4-argon 모델 페이지](https://artificialanalysis.ai/models/gemini-4-argon)
- 한계: C·C++·Rust 시스템 코드에 대한 Argon 전용 독립 평가는 찾지 못했다.
