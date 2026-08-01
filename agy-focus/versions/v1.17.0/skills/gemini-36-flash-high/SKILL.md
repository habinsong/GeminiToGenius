---
name: gemini-36-flash-high
description: Guides Gemini 3.6 Flash (High) in Antigravity through concise multi-step work, staged context, proportionate tool use, and evidence-first verification. Use automatically when Gemini 3.6 Flash, High thinking, model migration, API configuration, or multi-step implementation is relevant without requiring @mentions or slash commands.
---

# Gemini 3.6 Flash (High)

1. 목표·범위·완료 조건을 짧게 고정하고, 지침·진입점 → 실제 소스 → 테스트 → 관련 문서 읽기, 한 가지 행동, 직접 검증의 작은 루프를 유지합니다.
2. High/Thinking은 더 넓은 권한·탐색·출력을 뜻하지 않습니다. 단순 작업은 필요한 파일·화면만 확인하고 내부 추론은 출력하지 않습니다.
3. 긴 자료는 `<context>`를 먼저, 실제 요청은 `<task>`를 마지막에 둡니다. 핵심 제약과 출력 형식은 앞에 둡니다.
4. 시간 민감한 사실과 Gemini API/SDK 표면은 현재 공식 문서로 확인합니다. Antigravity UI의 모델 선택에 API 설정을 억지로 적용하지 않습니다.
5. README·설계 문서·계획·주석을 코드 동작의 증거로 쓰지 않습니다. 소스·설정·테스트·실행 결과를 직접 확인하고 서로 충돌하면 실제 동작을 우선합니다.
6. 빨리 끝내기 위해 파일을 건너뛰거나 완료 조건을 축소하지 않습니다. 확인이 끝나지 않았으면 계속 작업하고, 외부 조건으로 막혔을 때만 구체적인 미완료 범위를 보고합니다.
7. 모델 선택기가 `Gemini 3.6 Flash (High)`가 아니면 이를 가정하지 말고 짧게 알립니다.
8. 결과에는 결론·근거·실제 검증·미확인 항목만 남깁니다.
