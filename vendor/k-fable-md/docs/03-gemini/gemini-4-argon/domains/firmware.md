# Gemini 4 Argon · 펌웨어 — 조사 기록
> 제공자: Google · 모델 ID: `gemini-4-argon` · 기준일: 2026-11-03 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사·검증 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: [`md/03-gemini/gemini-4-argon/firmware.md`](../../../../md/03-gemini/gemini-4-argon/firmware.md)
> 절 번호는 지침 문서의 번호를 따른다(§1 분야 규칙, §2 이 모델의 분야 운용). 응답 계약과 작업 원칙은 전역 지침(AGENTS·CLAUDE·GEMINI.md)이 맡는다.
> 분야 규칙의 근거 수준 표기 원본: [`docs/_common/domain-rules/firmware.md`](../../../_common/domain-rules/firmware.md)

## 2. 이 모델의 펌웨어 작업 운용
모델 전체 특성은 상위 폴더의 [`README.md`](../README.md)가 안내하는 개요·운용·비판 문서를 따른다. 요약: 자기 검증이 약하다는 평가, 사이버 인접 작업 안전장치, Gemini CLI는 Gemini 4에 비최적화, 임베디드 평가 없음.

- **임베디드·드라이버·브링업에 대한 독립 평가는 찾지 못했다.** [미확인]
- **펌웨어 바이너리 분석·익스플로잇 성격의 요청은 제한될 수 있다.** 모델 카드는 사이버 임계 능력 도달 가능성을 배제하지 못해 안전장치를 적용한다고 하고, 침해 분석·리버스 엔지니어링·악성코드 분석 같은 이중 용도 작업은 Fairwind 프로그램의 승인된 파트너 대상이라는 안내가 있다. [부분] 자사 제품의 소스 취약점 점검은 일반적으로 가능해도 거부 가능성을 두고 설계한다. 거부되면 같은 요청을 반복하지 말고 사용자에게 알린다. [부분/미확인]
- **정지점을 목록으로 박는다.** 이 모델은 자기 검증이 약하다는 후기가 있고 [부분], 장시간 자율 작업의 안전장치 설계가 공개된 것이 없다. 되돌릴 수 없는 단계(플래시 소거, 퓨즈·OTP 쓰기, 보호 비트, 부트로더 덮어쓰기, 디버그 포트 잠금, 양산 이미지 서명) 앞에서만 대상 장치와 이미지를 사람이 확인한 뒤 진행한다. 그 밖의 단계에는 정지점을 넣지 않는다.
- **레지스터·타이밍은 문서로 확인한다.** 모델 카드가 환각을 인정한다. [부분] 비트 필드, 클럭 설정, 인터럽트 번호는 레퍼런스 매뉴얼의 개정판과 페이지를 근거로 남기고, 확인하지 못했으면 값을 쓰지 않는다(§1.1).
- **변경 후 검증을 지시문으로 강제한다.** 호스트 단위 테스트·정적 분석·시뮬레이터를 돌리고 출력을 읽고 실패하면 고치게 한다. 실제 보드에서 확인하지 못했으면 "하드웨어 미검증"이라고 쓴다.
- **도구.** Gemini CLI가 아니라 Antigravity CLI에서 쓰고 지침은 `AGENTS.md`로 둔다. [확인]
- **함수 호출 하네스는 thought signature를 되돌려준다.** `thinking_level`은 명시하고 `MINIMAL`은 쓰지 않는다(400). [부분]
- **정적 분석 경고를 억제하는 제안을 따르지 않는다.** 경고는 원인을 고친다(§1.1).
- **테스트 통과를 안전 근거로 쓰지 않는다.** 테스트가 있는 544건의 통과율은 85.66%인데 취약점의 약 80%가 blocker·critical이었다. 보안 점검을 테스트와 별도 단계로 둔다. [확인: Sonar 벤치마크]
- **암호 설정과 시스템 자원 처리를 먼저 점검한다.** 취약점의 약 3분의 2가 암호 설정 오류(127건)와 시스템 자원의 불안전한 처리(81건)였고, 하드코딩된 자격 증명도 7건 나왔다. 정적 분석(SAST)을 이 두 영역부터 돌린다. [확인: Sonar 벤치마크]
- **동시성 버그를 따로 본다.** 버그 중 동시성·스레딩이 가장 많았다(58건, 17%). 스레드·비동기·인터럽트 코드는 경쟁 조건 점검(TSan 또는 리뷰)을 거친다. [확인: Sonar 벤치마크]
- **빈 응답을 완료로 세지 않는다.** 4,444건 중 69건(1.55%)이 쓸 수 있는 코드를 내지 않았다. 산출물 파일이 실제로 생겼는지 확인한다. [확인: Sonar 벤치마크]
- **실제 저장소 변경은 Carbon 이상으로 맡긴다.** 코딩 에이전트 지수의 저장소 변경 항목이 25로 낮다. 터미널과 코드 설명은 중간이다. [부분: 2차 글이 옮긴 코딩 에이전트 지수]
- **느리고 출력이 길므로 시간·토큰 상한을 둔다.** 한 작업이 30분 안팎이고 출력 토큰이 중앙값의 약 1.7배다. [확인: Artificial Analysis 모델 페이지]

## 4. 근거와 한계
- 사이버 능력·Fairwind: [Fairwind Program](https://deepmind.google/fairwind-program/), [Gemini 4 Argon 모델 카드](https://deepmind.google/models/model-cards/gemini-4-argon/) (스니펫만) [부분]
- Gemini CLI: [google-gemini/gemini-cli README](https://github.com/google-gemini/gemini-cli) [확인]
- 자기 검증 약점: [eesel.ai 리뷰](https://www.eesel.ai/blog/gemini-4-argon-review) [부분]
- 추가 확인(2026-11-19 웹 검색): [Sonar: Gemini 4 Argon 코드 평가](https://www.sonarsource.com/blog/google-gemini-4-argon-evaluation/)
- 추가 확인(2026-11-19 웹 검색): [Artificial Analysis Coding Agent Index v2.1 표(2차 정리)](https://freakyjolly.com/coding-agent-index-v2-1-explained/)
- 추가 확인(2026-11-19 웹 검색): [Artificial Analysis: gemini-4-argon 모델 페이지](https://artificialanalysis.ai/models/gemini-4-argon)
- 한계: 정지점 목록은 비가역 작업의 위험에서 도출한 안전 권고이며 실험으로 검증되지 않았다. 펌웨어 분석이 실제로 거부되는 범위는 확인하지 못했다.
