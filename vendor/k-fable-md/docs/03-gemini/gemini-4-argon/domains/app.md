# Gemini 4 Argon · 앱 — 조사 기록
> 제공자: Google · 모델 ID: `gemini-4-argon` · 기준일: 2026-11-03 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사·검증 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: [`md/03-gemini/gemini-4-argon/app.md`](../../../../md/03-gemini/gemini-4-argon/app.md)
> 절 번호는 지침 문서의 번호를 따른다(§1 분야 규칙, §2 이 모델의 분야 운용). 응답 계약과 작업 원칙은 전역 지침(AGENTS·CLAUDE·GEMINI.md)이 맡는다.
> 분야 규칙의 근거 수준 표기 원본: [`docs/_common/domain-rules/app.md`](../../../_common/domain-rules/app.md)

## 2. 이 모델의 앱 작업 운용
모델 전체 특성은 상위 폴더의 [`README.md`](../README.md)가 안내하는 개요·운용·비판 문서를 따른다. 요약: Android Studio에서도 진입할 수 있는 Google 생태계 모델, 자기 검증이 약하다는 평가, 컴퓨터 사용은 프리뷰, 2026-11-30 이후 가격 2배.

- **Android 개발 도구 연동이 공식 진입점으로 소개된다.** Google은 Gemini API의 유료 티어를 Google AI Studio와 Android Studio에서 쓰는 것을 개발자 진입점으로 안내한다. [부분] 다만 모바일 앱 개발 품질에 대한 독립 평가는 찾지 못했다. [미확인] 실기기 검증을 생략하지 않는다.
- **변경 후 실제 검사를 지시문으로 박는다.** 이 모델은 자기 검증이 약하다는 후기가 있다. [부분] "컴파일·린트·단위 테스트를 돌리고 출력을 읽고, 실패하면 원인을 고쳐 다시 돌려라. 못 돌렸으면 무엇을 왜 못 했는지 말하라"를 시작에 적는다. 빌드·테스트 출력은 파일로 한 번 저장한 뒤 실패한 구간만 읽는다.
- **스토어 정책·플랫폼 요건은 grounding으로 확인하고 출처를 연다.** 이 모델은 Google 검색 grounding과 URL 컨텍스트를 지원한다. [부분] §1.2 표의 날짜는 모델의 말이 아니라 공식 정책 페이지에서 직접 확인한다.
- **컴퓨터 사용은 프리뷰다.** 시뮬레이터 조작에 쓰려면 프리뷰 제약과 성공률을 자체 과제로 측정하고, 결과는 스크린샷·로그로 확인한다. 독립 수치는 찾지 못했다. [부분/미확인]
- **Live API와 명시적 캐싱이 없다.** 실시간 음성 앱이나 긴 정적 프롬프트 재사용에 의존하는 설계는 암묵적 캐싱만 가능함을 감안한다. [부분]
- **`thinking_level`을 명시한다.** 짧은 UI 문자열 작업은 `LOW`, 일반 구현은 `MEDIUM`(기본), 어려운 수명주기 문제만 `HIGH`. `MINIMAL`은 400이다. [부분]
- **함수 호출 하네스는 thought signature를 돌려준다.** [부분]
- **비용.** 2026-11-30 이후 입력 $4 / 출력 $20이다. 번역 초안·로그 분류 같은 대량 작업은 Gemini 3.8 Flash나 더 작은 모델을 쓴다. [부분]
- **서명 키, 프로파일, 스토어 제출·배포는 승인 후에만.**
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
- Android Studio 진입점·가격·컴퓨터 사용 프리뷰: [Gemini 4 Argon is now available for developers](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-4-argon/), [OpenRouter 목록](https://openrouter.ai/google/gemini-4-argon) (스니펫만) [부분]
- 자기 검증 약점·누락 기능: [eesel.ai 리뷰](https://www.eesel.ai/blog/gemini-4-argon-review), [Layer3 Labs 리뷰](https://www.layer3labs.io/guides/gemini-4-argon-review) [부분]
- 추가 확인(2026-11-19 웹 검색): [Sonar: Gemini 4 Argon 코드 평가](https://www.sonarsource.com/blog/google-gemini-4-argon-evaluation/)
- 추가 확인(2026-11-19 웹 검색): [Android Headlines: Argon 출시와 성능 논란](https://www.androidheadlines.com/2026/10/google-gemini-4-argon-launch-benchmark-performance-debate.html)
- 추가 확인(2026-11-19 웹 검색): [Artificial Analysis Coding Agent Index v2.1 표(2차 정리)](https://freakyjolly.com/coding-agent-index-v2-1-explained/)
- 추가 확인(2026-11-19 웹 검색): [Artificial Analysis: gemini-4-argon 모델 페이지](https://artificialanalysis.ai/models/gemini-4-argon)
- 추가 확인(2026-11-19 웹 검색): [Google AI 개발자 포럼: Gemini 4 Argon·Hydrogen 안드로이드 앱 피드백](https://discuss.ai.google.dev/t/feedback-from-a-long-time-ai-studio-user-gemini-4-argon-hydrogen-fall-short-on-ui-ux-quality-and-scope-control-when-building-android-apps/201696)
- 한계: 모바일 개발에 대한 Argon 전용 독립 벤치마크는 없다.
