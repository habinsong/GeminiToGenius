# Gemini 4 Hydrogen — 교차 확인
> 제공자: Google · 모델 ID: `gemini-4-hydrogen` · 기준일: 2026-11-22 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: [`md/03-gemini/gemini-4-hydrogen/GEMINI.md`](../../../md/03-gemini/gemini-4-hydrogen/GEMINI.md)

`overview.md`의 사양을 다른 출처로 다시 맞춰 본 기록이다. 2026-11-19에 Google의 발표문과 두 문서 페이지를 직접 읽고 웹 검색으로 맞췄다.

## 1차 출처에서 읽은 것
- Google 블로그 발표문: 게시일(2026-11-12)·갱신일(2026-11-16), 가격 $1.50/$7.50, 위치, 벤더 벤치마크, 가용성, 4단계 thinking.
- Google Cloud 문서·AI Studio 모델 문서: ID, 컨텍스트 1,048,576, 출력 한도, 입출력, thinking 레벨, 지원·미지원 기능.

## 교차 확인 표
| 항목 | 값 | 상태 | 출처 | 비고 |
|---|---|---|---|---|
| 모델 ID | `gemini-4-hydrogen` | [확인] 1차 | Google Cloud 문서, AI Studio 문서 | 두 곳 일치 |
| 출시일 | 2026-11-12 | [확인] 1차(블로그) + [부분] 2차 다수 | 블로그, gHacks, 보도 | 두 문서 페이지에는 출시일이 없다 |
| 컨텍스트 / 최대 출력 | 1,048,576 / 65,536(긴 디코딩 시 확장) | [확인] 1차 | Google Cloud·AI Studio 문서 | 두 곳 일치 |
| thinking 레벨 | LOW·MEDIUM·HIGH(기본)·XHIGH | [확인] 1차 | Google Cloud 문서, 블로그 | AI Studio 문서는 소문자 low~xhigh로 표기 |
| 가격 (입력/출력/캐시) | $1.50 / $7.50 / $0.075 | [확인] 1차 2곳 | 블로그, AI Studio 가격 페이지 | 집계 사이트의 블렌디드 $1.10은 계산 기준이 달라 상충이 아니다 |
| 대체 대상 | Gemini 3.8 Flash | [확인] 블로그 + [부분] 보도 다수 | 블로그, gHacks | Yahoo Tech는 3.5 Flash로 적어 상충 |
| 지식 컷오프 | 불명 | [미확인] | 문서에 없음 |  |

## 아직 못 올린 것
- 모델 카드·안전 보고서. 가격 페이지의 요금표는 2026-11-22에 읽었다(무료 티어·Batch·Flex·Priority 포함).
- Gemini 3.8 Flash의 종료 일정.

## 출처
- [Google 블로그 발표문](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen/)
- [Google Cloud 모델 문서](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/4-hydrogen)
- [AI Studio 모델 문서](https://aistudio.google.com/docs/models/gemini-4-hydrogen)
- [AI Studio 가격 페이지](https://aistudio.google.com/docs/pricing)
- [gHacks](https://www.ghacks.net/2026/11/13/google-releases-gemini-4-hydrogen-in-search-and-the-gemini-app-replacing-gemini-3-8-flash/)
