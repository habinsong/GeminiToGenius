# Gemini 4 Neon — 교차 확인
> 제공자: Google · 모델 ID: `gemini-4-neon` · 기준일: 2026-11-22 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: [`md/03-gemini/gemini-4-neon/GEMINI.md`](../../../md/03-gemini/gemini-4-neon/GEMINI.md)

`overview.md`의 사양을 다른 출처로 맞춰 본 기록이다. 2026-11-22에 Google 출시 글, AI Studio 모델 문서, 가격 페이지를 열어 읽고 출시 전 소문 보도와 맞췄다. 이전 판(2026-11-19)은 공식 발표가 없다고 적었고 모델 ID·가격이 [미확인]이었다.

## 교차 확인 표
| 항목 | 값 | 상태 | 출처 | 비고 |
|---|---|---|---|---|
| 출시일 | 2026-11-18 | [확인] 1차 + [부분] 2차 다수 | 블로그, 9to5Google 등 | 모델 문서는 "2026년 11월"만 표시 |
| 모델 ID | `gemini-4-neon` | [확인] 1차 | AI Studio 문서 | 출시 전 코드 문자열과 일치 |
| 컨텍스트 / 최대 출력 | 1,048,576 / 65,536(긴 디코딩 시 1,048,576) | [확인] 1차 | AI Studio 문서 | 블로그는 1M 토큰만 적음 |
| thinking 레벨 | low·medium·high·xhigh, 기본 high | [확인] 1차(기본값은 블로그) | AI Studio 문서, 블로그 | |
| 가격 (입력/출력/캐시) | $3 / $15 / $0.15 | [확인] 1차 | 블로그, 가격 페이지 | 출시 전 SKU 보도와 일치 |
| Batch·Flex / Priority | $1.50 / $7.50 / $0.075, $5.40 / $27 / $0.27 | [확인] 1차 | 가격 페이지 | 출시 전 "배치는 절반" 전언과 일치 |
| 독립 지수 | 61(3위, `xhigh`) | [부분] Google 인용 | 블로그 | 독립 사이트에서 직접 확인하지 못함 |
| Vertex AI 제공 | 확인 못 함 | [미확인] | | 출시 전 보도는 "아직 없음", 일부 2차 글은 "있음" |

## 아직 못 올린 것
- 지식 컷오프, 모델 카드의 평가 조건, Vertex AI 제공 시점, 같은 단계에서의 독립 지수 재측정.

## 출처
- [Introducing Gemini 4 Neon](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/)
- [Gemini 4 Neon (AI Studio 모델 문서)](https://aistudio.google.com/docs/models/gemini-4-neon)
- [AI Studio 가격 페이지](https://aistudio.google.com/docs/pricing)
- [TestingCatalog](https://www.testingcatalog.com/google-prepares-to-release-gemini-4-neon-model-on-apis/)
- [9to5Google](https://9to5google.com/2026/11/18/gemini-4-neon-announcement/)
