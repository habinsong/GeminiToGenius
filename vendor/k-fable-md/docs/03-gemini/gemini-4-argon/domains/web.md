# Gemini 4 Argon · 웹 — 조사 기록
> 제공자: Google · 모델 ID: `gemini-4-argon` · 기준일: 2026-11-03 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사·검증 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: [`md/03-gemini/gemini-4-argon/web.md`](../../../../md/03-gemini/gemini-4-argon/web.md)
> 절 번호는 지침 문서의 번호를 따른다(§1 분야 규칙, §2 이 모델의 분야 운용). 응답 계약과 작업 원칙은 전역 지침(AGENTS·CLAUDE·GEMINI.md)이 맡는다.
> 분야 규칙의 근거 수준 표기 원본: [`docs/_common/domain-rules/web.md`](../../../_common/domain-rules/web.md)

## 2. 이 모델의 웹 작업 운용
모델 전체 특성은 상위 폴더의 [`README.md`](../README.md)가 안내하는 개요·운용·비판 문서를 따른다. 요약: `thinking_level` 명시, 자기 검증이 약하다는 평가, 2026-11-30 이후 가격 2배, 함수 호출 시 thought signature 필수.

- **웹 UI 생성 품질에 대한 독립 평가는 찾지 못했다.** [미확인] Google은 Argon으로 만든 창작 프로젝트 사례를 소개하지만 이는 벤더 시연이다. [부분] 시각 마감은 스크린샷을 직접 대조하고, 확인하지 못했으면 "화면 미확인"이라고 보고한다.
- **변경 후 실제 검증을 지시문으로 박는다.** 이 모델은 자기 검증과 코드 재검토로 돌아가는 데 약하다는 후기가 있다. [부분] "화면을 브라우저에서 열고, 콘솔 오류와 실패한 네트워크 요청을 확인하고, 관련 테스트를 돌린 뒤 결과를 읽고 실패하면 고쳐서 다시 돌려라. 못 했으면 못 했다고 말하라"를 작업 시작에 적는다. 완료 기준에 통과해야 할 검증을 포함한다.
- **낡은 명세·충돌하는 규칙을 컨텍스트에 두지 않는다.** 한 후기는 이 모델이 정확성보다 규칙을 우선하고 레거시 명세·코드에 주의가 흐트러진다고 적었다. [부분] 오래된 디자인 문서나 폐기된 컴포넌트 설명을 입력에서 빼고, 기존 UI 체계가 우선한다는 §1.1 규칙을 한 번 명시한다.
- **문서·구조 편집에는 맞을 수 있다.** 구조 편집기로 좋았다는 단일 후기가 있다. 마크업·컴포넌트 구조 정리는 시도해 볼 만하지만 결과를 린터·타입체크·테스트로 확인한다. [부분]
- **웹 사실은 Google 검색 grounding과 URL 컨텍스트로 확인한다.** 브라우저 지원, 표준, 라이브러리 버전은 grounding된 출처 URL을 직접 열어 대조한다. [부분]
- **함수 호출 하네스를 직접 만들면 thought signature를 돌려준다.** 응답의 모든 파트를 그대로 다음 턴에 넣지 않으면 검증 오류가 난다. [부분]
- **비용.** 2026-11-30 이후 입력 $4 / 출력 $20이다. 화면 단위 반복 작업은 Gemini 3.8 Flash나 다른 제공자의 균형형 모델과 작업당 비용을 비교한다. 이 모델은 지수 평가에서 출력 토큰도 많이 썼다. [부분]
- **테스트 통과를 안전 근거로 쓰지 않는다.** 테스트가 있는 544건의 통과율은 85.66%인데 취약점의 약 80%가 blocker·critical이었다. 보안 점검을 테스트와 별도 단계로 둔다. [확인: Sonar 벤치마크]
- **암호 설정과 시스템 자원 처리를 먼저 점검한다.** 취약점의 약 3분의 2가 암호 설정 오류(127건)와 시스템 자원의 불안전한 처리(81건)였고, 하드코딩된 자격 증명도 7건 나왔다. 정적 분석(SAST)을 이 두 영역부터 돌린다. [확인: Sonar 벤치마크]
- **동시성 버그를 따로 본다.** 버그 중 동시성·스레딩이 가장 많았다(58건, 17%). 스레드·비동기·인터럽트 코드는 경쟁 조건 점검(TSan 또는 리뷰)을 거친다. [확인: Sonar 벤치마크]
- **빈 응답을 완료로 세지 않는다.** 4,444건 중 69건(1.55%)이 쓸 수 있는 코드를 내지 않았다. 산출물 파일이 실제로 생겼는지 확인한다. [확인: Sonar 벤치마크]
- **화면 품질은 직접 본다.** 표준 벤치마크에 비해 실작업과 프런트엔드 웹 디자인에서 약하다는 내부자 증언이 보도됐다. 스크린샷을 대조하고 "화면 미확인"이면 그렇게 보고한다. [부분: 검색 요약만 확인]
- **실제 저장소 변경은 Carbon 이상으로 맡긴다.** 코딩 에이전트 지수의 저장소 변경 항목이 25로 낮다. 터미널과 코드 설명은 중간이다. [부분: 2차 글이 옮긴 코딩 에이전트 지수]
- **느리고 출력이 길므로 시간·토큰 상한을 둔다.** 한 작업이 30분 안팎이고 출력 토큰이 중앙값의 약 1.7배다. [확인: Artificial Analysis 모델 페이지]
- **변경 범위를 문장으로 못 박는다.** 요청하지 않은 문구를 넣고 버튼을 키우는 범위 이탈이 보고됐다. 수정은 변경 부분만 보이는 diff 형식으로 요구한다. [부분: 개발자 포럼 단일 사용자]
- **후속 편집마다 기존 기능을 확인한다.** 편집의 약 70%만 맞고 나머지는 다른 기능을 깨뜨린다는 보고가 있다. [부분: 단일 사용자]
- **밀도 높은 도구형 화면의 UI·UX는 사람이 설계한다.** 간격·위계·비율 판단이 약하다는 평이다. [부분: 단일 사용자]

## 4. 근거와 한계
- 자기 검증·낡은 명세 지적: [Google AI 개발자 포럼](https://discuss.ai.google.dev/t/how-bad-is-gemini-4-argon/190009), [eesel.ai 리뷰](https://www.eesel.ai/blog/gemini-4-argon-review), [Layer3 Labs 리뷰](https://www.layer3labs.io/guides/gemini-4-argon-review) [부분]
- thought signature·가격: [Thought signatures](https://ai.google.dev/gemini-api/docs/thought-signatures), [Now available for developers](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-4-argon/) (스니펫만) [부분]
- 추가 확인(2026-11-19 웹 검색): [Sonar: Gemini 4 Argon 코드 평가](https://www.sonarsource.com/blog/google-gemini-4-argon-evaluation/)
- 추가 확인(2026-11-19 웹 검색): [Android Headlines: Argon 출시와 성능 논란](https://www.androidheadlines.com/2026/10/google-gemini-4-argon-launch-benchmark-performance-debate.html)
- 추가 확인(2026-11-19 웹 검색): [Artificial Analysis Coding Agent Index v2.1 표(2차 정리)](https://freakyjolly.com/coding-agent-index-v2-1-explained/)
- 추가 확인(2026-11-19 웹 검색): [Artificial Analysis: gemini-4-argon 모델 페이지](https://artificialanalysis.ai/models/gemini-4-argon)
- 추가 확인(2026-11-19 웹 검색): [Google AI 개발자 포럼: Gemini 4 Argon·Hydrogen 안드로이드 앱 피드백](https://discuss.ai.google.dev/t/feedback-from-a-long-time-ai-studio-user-gemini-4-argon-hydrogen-fall-short-on-ui-ux-quality-and-scope-control-when-building-android-apps/201696)
- 한계: 웹 프런트엔드 품질의 독립 비교는 찾지 못했다.
