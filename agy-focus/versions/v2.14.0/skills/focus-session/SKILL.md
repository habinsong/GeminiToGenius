---
name: focus-session
description: Maintains a narrow, evidence-first loop for long or multi-file Antigravity work when scope, context, or tool use may drift. Use automatically for 여러 파일, 작업이 길어, 범위가 넓어, 맥락이 복잡해, long task, multi-file, or keep focused without requiring @mentions or slash commands.
---

# 집중 세션 및 장기 지평 실행 (Fable/Opus Long-Horizon Behavior)

1. **목표 중심 실행 (5. Goal-Driven Execution)**: 모호한 작업을 검증 가능한 목표로 바꿉니다.
   - 버그 수정: 실패 경로 재현 → 패치 → 통과 확인
   - 유효성 검사: 무효 입력 정의 → 테스트 추가/갱신 → 검증
   - 리팩터링: 전/후 동작 일치 확인
   - UI 개선: 가시 상태 정의 → 컴포넌트 업데이트 → 레이아웃/빌드 검증
2. **3단계 단기 계획 루프**:
   ① Inspect current implementation (현재 구현 점검 & 관련 파일 식별)
   ② Patch smallest failing surface (가장 작은 실패면 패치 & 타깃 체크)
   ③ Run final check (최종 점검: build/test/typecheck)
3. **장기 지평 지속성 (6. Long-Horizon Behavior)**:
   - 전체 세션에 걸쳐 원래 목표를 유지하고 작업을 작은 완결 루프로 분할합니다.
   - 추측이나 기억보다 저장소의 실제 증거를 우선하며, 수정 전 검색 및 정독을 수행합니다.
   - 의미 있는 편집마다 즉시 검증하고 실패 시 디버깅 루프를 돕니다.
   - 무관한 정리로 이탈하지 않으며 약한 모델의 불필요한 의식을 제거합니다.
4. **컨텍스트 압축 전 6대 필수 보존 항목**:
   - `Current goal` (현재 목표)
   - `Files changed` (변경된 파일 목록)
   - `Commands run` (실행한 명령어)
   - `Passing checks` (통과한 검증 항목)
   - `Failing checks` (실패한 검증 항목)
   - `Next concrete step` (다음 구체적 실행 단계)
5. **비용 및 속도 최적화 (19. Cost and Speed)**: 타깃 검색과 읽기(`rg`, `git diff`, 선별적 파일 읽기)를 사용하며 불필요하게 거대 파일을 컨텍스트에 덤프하지 않습니다.
