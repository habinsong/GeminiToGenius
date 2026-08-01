---
name: focus-session
description: Maintains a narrow, evidence-first work loop for multi-file Antigravity tasks when the agent risks context drift or unnecessary tool use.
---

# 집중 세션

여러 파일을 다루거나 작업이 길어져 목표가 흐려질 때만 활성화합니다.

1. 현재 사용자 지시에서 목표, 범위, 완료 조건을 각각 한 문장으로 고정합니다.
2. 활성 workspace와 관련 파일만 검색하고 먼저 상태와 기존 변경을 확인합니다.
3. 작업을 읽기 → 최소 변경 → 가장 작은 검증 루프로 나눕니다.
4. 각 루프가 끝날 때 변경 파일, 실행 명령, 통과·실패 근거를 짧게 기록합니다.
5. 관련 없는 스킬을 모두 읽지 말고 현재 단계에 필요한 스킬 하나만 활성화합니다.
6. MCP·플러그인·패키지 설치는 목적과 데이터 범위를 확인하기 전에는 연결하지 않습니다.
7. 컨텍스트가 길어지면 새 문서를 더 읽지 말고 현재 목표와 미검증 항목을 먼저 요약합니다.

완료 보고에는 변경 내용과 실제 검증 결과를 구분하고, 실행하지 않은 UI·하드웨어·원격 검증은 성공으로 표현하지 않습니다.
