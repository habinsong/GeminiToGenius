# 범용 2절("어떤 모델이든 지킬 점")의 근거
> 기준일: 2026-11-19 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: `universal/<분야>.md`의 `generic` 블록. 모델 전용 2절이 없는 `md/계열/모델/<분야>.md`에도 같은 블록이 들어간다.
> 모델마다 근거가 없을 때 쓰는 대체 규칙이므로 특정 모델의 평가가 아니라 여러 모델을 함께 본 연구에서 가져왔다.

## 웹
- 개발 중 브라우저로 스스로 시험한 정도가 최종 점수와 강하게 이어졌다(상관 0.72). 모델 간 격차가 코드 수정 평가보다 훨씬 크게 벌어졌다. [Vibe Code Bench (arXiv 2603.04601)](https://arxiv.org/pdf/2603.04601) [부분: 검색 요약]
- 후속 리더보드에서도 모든 시험을 일관되게 통과하는 앱을 내는 모델은 없다. 평가는 React·Vite·Supabase 고정이라 다른 스택으로 일반화되지 않는다. [Vals AI: Vibe Code Bench](https://www.vals.ai/benchmarks/vibe-code) [부분: 검색 요약]
- 생성 코드의 보안 통과율은 평균 56%이고 지난해와 거의 같다. 언어별로 Python 63%에서 Java 30%까지 갈린다. [Veracode 2026 봄 보고](https://veracode.com/blog/spring-2026-genai-code-security) [부분: 검색 요약]
- 독립 연구는 OWASP Top 10 기준 25% 안팎에서 확인된 취약점을 찾았다. 수치가 보도마다 다르다(25.1%, 25.7%). [AppSec Santa 2026](https://appsecsanta.com/research/ai-code-security-study-2026) [부분]
- 존재하지 않는 패키지 이름이 Python 코드의 약 16%, JavaScript의 약 21%에서 나왔다. 같은 이름이 반복돼 악용 가능하다. [Kaspersky: slopsquatting](https://www.kaspersky.com/blog/ai-slopsquatting-supply-chain-risk/53327/), [2026 재평가](https://www.alphaxiv.org/abs/2605.17062) [부분]
- 처음부터 앱을 만드는 평가(Vibe Code Bench v1.1)는 최상위 20여 개 모델이 81~94점에 몰렸고 Vals는 이전 판을 포화로 폐기했다. 여러 요청에 걸쳐 앱을 확장하는 평가(1-100)에서는 최고 55%로 격차가 크다. [Vals: 1-100 v1.1](https://www.vals.ai/benchmarks/vcb-1-100-v1-1), [BenchLM 미러](https://benchlm.ai/benchmarks/vibecodebench) [부분]

## 앱
- 일부 모델이 기능을 희생해 컴파일 성공만 맞춘다. 실패 유형은 리소스 연결 오류와 API 버전 문제다. [AppForge (arXiv 2510.07740)](https://arxiv.org/pdf/2510.07740) [부분: 검색 요약]
- 패치 텍스트만 보는 모바일 평가는 빌드 시점 오류를 놓친다. [AppForge 평가 설명](https://www.alphaxiv.org/benchmarks/fudan-university/appforge) [부분]
- 한계: Swift·Kotlin의 폐기 API 호출을 모델별로 센 연구는 찾지 못했다. [미확인]

## 네이티브
- C·C++ 안전성만 따로 본 연구는 찾지 못했다. 위 웹 항목의 보안 연구가 언어를 가리지 않고 쓸 수 있는 근거의 전부다. [미확인]

## 하드웨어
- 모델이 없는 핀 이름과 연결을 지어낸다. 논리 회로와 코드 생성은 잘하지만 브레드보드 배선 같은 물리 연결에서 크게 약하다. [PCEval (arXiv 2601.02404)](https://arxiv.org/pdf/2601.02404), [CircuitLM (arXiv 2601.04505)](https://arxiv.org/html/2601.04505v2) [부분: 검색 요약]
- 회로도를 데이터시트에서 생성하는 평가는 정적 전기 규칙 검사와 시뮬레이션을 함께 쓰며, 시뮬레이션만으로는 회로도 수준의 정합성을 검증하지 못한다고 밝힌다. [HWE-Bench (arXiv 2603.18102)](https://arxiv.org/html/2603.18102), [PCBSchemaGen (arXiv 2602.00510)](https://www.alphaxiv.org/abs/2602.00510.md) [부분: 검색 요약]
- 한계: 아날로그 회로 전용 데이터시트 핀 오류 평가는 찾지 못했다. [미확인]

## 펌웨어
- 코드가 동작하지 않을 때도 모델의 추론은 임베디드 설계 작업에서 도움이 됐고, 실제 보드를 붙인 폐루프 평가 틀이 쓰였다. 환각은 한계로 보고됐다. [Englhardt 외 (arXiv 2307.03817)](https://arxiv.org/html/2307.03817v1) [확인: 2023년 연구로 모델 세대가 오래됨]
- 범용 모델이 레지스터 이름과 초기화 순서를 지어낸다는 서술이 있다. 개요 페이지만 확인했다. [Specialized Language Models for Embedded Systems (arXiv 2603.11139)](https://www.alphaxiv.org/overview/2603.11139) [부분]

## 웹 리서치와 연구
- 인용 URL의 3~13%가 환각이고 5~18%가 열리지 않았다. 연구용 에이전트가 인용을 가장 많이 만들고 환각도 더 많았다. 주장이 출처로 뒷받침되는지는 측정하지 않았다. [Rao 외 (arXiv 2604.03173)](https://arxiv.org/abs/2604.03173) [부분: 검색 요약]
- 링크 유효율이 94%를 넘어도 인용한 주장의 사실 정확도는 39~77%였다. 검색 호출을 2회에서 150회로 늘리자 사실 정확도가 평균 약 42% 내려갔다. 평가자가 LLM이라 편향이 있다. [Cited but Not Verified (arXiv 2605.06635)](https://arxiv.org/html/2605.06635) [부분: 사전 공개 논문]
- 연구 에이전트가 모른다고 하기보다 지어낸다는 보도가 있다. 제목과 요약만 확인했다. [The Decoder](https://the-decoder.com/ai-research-agents-would-rather-make-up-facts-than-say-i-dont-know/) [부분]

## 기술 연구
- 패키지 환각은 웹 항목과 같다. 라이선스 판단 오류를 센 연구는 찾지 못했다. [미확인]
