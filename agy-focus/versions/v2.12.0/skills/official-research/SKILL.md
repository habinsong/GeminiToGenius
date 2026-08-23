---
name: official-research
description: Verifies time-sensitive, obscure, or official Antigravity and Gemini facts through primary-source pages before answering. Use automatically for 최신, 공식 문서, 출처, 업데이트, 검색, Antigravity 문서, Gemini 문서, latest, official docs, source, or migration requests without requiring @mentions or slash commands.
---

# 공식 최신 조사 및 사전 검증 (2. Think Before Coding)

최신성·공식성·불확실성이 요청에 포함되거나 구현 전 선행 조사가 필요할 때 기억이나 추측에 의존하지 않고 실제 웹 검색으로 확인합니다.

1. **코딩 전 지적재산권 및 라이선스 검증**:
   - `search_web` 및 `read_url_content`를 사용하여 관련 논문, 레퍼런스, 공식 가이드라인, 특허 및 소스 자료를 수집합니다.
   - 특허 만료 여부를 확인하고, 적용 가능한 라이선스를 점검하며, 저작권을 평가하여 **사용이 안전하다고 확인된 자료만** 작업에 반영합니다.
2. **공식 출처 엄격 판별**:
   - Antigravity 문서는 `https://antigravity.google/docs/` 아래 공식 URL만 1차 출처로 인정합니다.
   - Gemini 문서는 `https://ai.google.dev/` 공식 문서 URL만 인정합니다.
   - 검색 요약이나 블로그, 커뮤니티 글은 1차 출처로 취급하지 않습니다.
3. **복수 해석 및 단순 접근 선호**:
   - 복수 해석이 존재할 경우 간결히 언급하고, 가장 유력한 해석으로 진행하며 가정을 명시합니다.
   - 요청된 솔루션이 문제에 비해 과도하게 복잡한 경우 푸시백합니다.
4. **사실과 추론의 명확한 분리**:
   - 확인된 사실, 추론, 확인하지 못한 항목을 분리하고 실제 읽은 문서의 정확한 URL을 함께 보고합니다.
5. **임의 날조 금지**:
   - 읽은 페이지나 저장소에 없는 파일, API, 동작, 프로젝트 관례를 임의로 날조하지 않습니다. 근거가 없으면 미확인으로 명시합니다.
