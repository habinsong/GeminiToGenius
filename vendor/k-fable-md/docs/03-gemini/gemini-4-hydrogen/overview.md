# Gemini 4 Hydrogen — 개요·사양·라이선스
> 제공자: Google · 모델 ID: `gemini-4-hydrogen` · 기준일: 2026-11-22 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: [`md/03-gemini/gemini-4-hydrogen/GEMINI.md`](../../../md/03-gemini/gemini-4-hydrogen/GEMINI.md)
> 소제목의 번호(2.x)는 주제별로 나누기 전 일반 조사 기록의 번호다. 문장 속 `§2.x`는 그 번호를 가리킨다.

#### 2.1 위치와 사양
- Gemini 3.8 Flash의 후속이다. Google이 3.8 Flash의 이전 대상으로 명시했다. 2026-11-12에 발표됐다(블로그 게시일, 2026-11-16 갱신). Google은 Hydrogen을 일상 에이전트 작업의 "daily driver"로, Carbon·Argon은 길고 깊은 추론용으로 위치시킨다. 모델 ID `gemini-4-hydrogen`. [확인]
- **가격**(100만 토큰당)은 입력 $1.50 / 출력 $7.50이고 1M 컨텍스트 전 구간에서 같다고 Google이 적었다. 한 집계 사이트의 블렌디드 $1.10과는 기준이 달라 직접 비교하지 않는다. 모델 문서에는 요금이 없고 캐시 쓰기가 표준 입력가의 1.25배라는 것만 있다. 가격 페이지(2026-11-22 읽음)는 캐시 입력 $0.075, Batch·Flex $0.75 / $3.75 / $0.0375, Priority $2.70 / $13.50 / $0.135를 적고, **무료 티어가 있다**(입력·출력·캐시 무료, 무료 티어 데이터는 제품 개선에 쓰인다). 초대제 비공개 프리뷰인 Contributor 요금($0.75 / $3.75)도 있다. [확인: 발표문·가격 페이지 / 부분: 집계]
- **컨텍스트는 입력·출력 통합 한도 1,048,576 토큰**이고 생각 토큰도 포함한다. 한 번의 foreground 구간 최대 출력은 65,536 토큰이다. Interactions API나 `v1beta1` GenerateContent의 긴 디코딩에서는 입력을 뺀 1,048,576까지 늘 수 있다. 지식 컷오프는 문서에 없다. [확인]
- **입출력**: 텍스트·이미지·문서(PDF·Office 형식)·비디오(프롬프트당 10개, 약 45분)·오디오(약 8.4시간)를 받고 출력은 텍스트뿐이다. [확인]
- **추론 강도는 `thinking_level`**: `LOW` / `MEDIUM` / `HIGH`(기본) / `XHIGH`(새 단계). `thinking_budget`이나 `thinking_level="MINIMAL"`을 보내면 HTTP 400이다. 샘플링은 temperature 1.0, topP 0.95, topK 64, candidateCount 1로 고정되어 다른 값은 무시된다. [확인]
- 지원: 함수 호출, 구조화 출력, 코드 실행, URL 컨텍스트, 컴퓨터 사용, 에이전트형 비디오 이해, Google 검색·지도 grounding. 캐싱은 암묵적 캐싱만(최소 4,096 토큰)이고 2027-01-12부터 TTL 기반 제어가 열린다. Live API, 튜닝, RAG Engine은 지원하지 않는다. API는 GenerateContent, Interactions, Count Tokens, OpenAI 호환 Chat Completions. [확인]
- 가용성: Gemini API, Google AI Studio, Android Studio, Antigravity(AI Pro·Ultra 유료), Gemini 앱(무료는 자동 모델 선택), Google 검색. 데이터 처리 지역은 ML 처리 `us`·`eu`. [확인]
- 벤더 주장(Google): 3.8 Flash 대비 `high`에서 약 2.5배 빠르고 지어낸 주장이 5배 이상 줄었다. Artificial Analysis 지수 51(`high`)·54(`xhigh`)로 Argon의 50보다 높다. Terminal-Bench 4.1 57%(3.8 Flash 18.2%). 이 수치는 모두 Google 보고다. [부분]
