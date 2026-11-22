# Gemini 4 Carbon — 교차 확인
> 제공자: Google · 모델 ID: `gemini-4-carbon` · 기준일: 2026-11-22 · 근거 표기: [확인]·[부분]·[미확인] (정의는 docs/README.md의 근거 수준)

> 사람이 읽는 조사 기록이다. LLM 컨텍스트에 넣지 않는다.
> 컨텍스트용 지침: [`md/03-gemini/gemini-4-carbon/GEMINI.md`](../../../md/03-gemini/gemini-4-carbon/GEMINI.md)

`overview.md`의 사양을 다른 출처로 다시 맞춰 본 기록이다. 2026-11-19에 AI Studio 모델 문서와 VentureBeat 기사를 직접 읽고 웹 검색으로 맞췄다. 이전 판(2026-11-03)은 모델 ID·가격이 모두 [미확인]이었다.

## 교차 확인 표
| 항목 | 값 | 상태 | 출처 | 비고 |
|---|---|---|---|---|
| 모델 ID | `gemini-4-carbon` | [확인] 1차 + [부분] 2차 다수 | AI Studio 문서, 보도 | 이전 판의 503 보고는 일반 공개 전 상태로 본다 |
| 일반 공개일 | 2026-11-10 | [부분] 2차 다수 일치 | VentureBeat 등 | 1차(발표문·모델 문서)에 날짜 없음 |
| 컨텍스트 / 최대 출력 | 1,048,576 / 65,536(긴 디코딩 시 1,048,576) | [확인] 1차 | AI Studio 문서 | VentureBeat는 컨텍스트 1M으로 적음 |
| thinking 레벨 | low·medium·high | [확인] 1차 | AI Studio 문서 | Hydrogen은 xhigh가 더 있음 |
| 가격 (입력/출력/캐시) | 도입가 $2 / $10 / $0.10(2026-11-30까지), 이후 $4 / $20 / $0.20 | [확인] 1차 + [부분] 2차 다수 일치 | AI Studio 가격 페이지, VentureBeat, MindStudio, Lindy | Argon의 가격 구조와 같음. Batch·Flex·Priority 요금도 같은 페이지에 있다 |
| 독립 지수 | Carbon 60(`high`), Fable 5.2 65(`max`) | [부분] 2차 | VentureBeat 인용 | 발표 때 59에서 채점 갱신 뒤 60 |

## 아직 못 올린 것
- 지식 컷오프, Vertex AI 제공 시점.
- 가격 페이지는 2026-11-22에 읽었다. 인상일(2026-12-01) 이후에 다시 확인한다.
- Google 일반 공개 발표문 본문, 모델 카드.

## 출처
- [AI Studio 모델 문서](https://aistudio.google.com/docs/models/gemini-4-carbon)
- [AI Studio 가격 페이지](https://aistudio.google.com/docs/pricing)
- [VentureBeat](https://venturebeat.com/technology/google-gemini-4-carbon-is-now-publicly-available-and-it-undercuts-claude-fable-5-2-and-opus-5-5-on-api-price)
- [MindStudio](https://www.mindstudio.ai/blog/gemini-4-carbon-pricing-rollout)
- [Lindy](https://www.lindy.ai/blog/gemini-4-carbon)
