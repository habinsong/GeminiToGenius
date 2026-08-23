---
name: gtg
description: Activates the GeminiToGenius strict execution harness for complete code inspection, persistent implementation, anti-AI-Slop UI, human product copy, and rendered verification. Invoke explicitly with /GTG for coding, debugging, refactoring, UI, UX, website, app, or multi-file tasks where shallow completion is unacceptable.
---

# GTG

`/GTG`가 선택되면 이 계약을 현재 작업의 완료 시점까지 유지합니다. 첫 계획이나 첫 생성물을 결과로 취급하지 않습니다.

## 실행 계약

1. **복명복창 및 목표 고정 (0. Communication & 5. Goal-Driven Execution)**: 사용자가 프롬프트를 입력하자마자 첫 응답에서 프롬프트와 핵심 요구사항을 반드시 한국어로 명확히 복명복창(요약 및 확인)합니다. 사용자 목표·허용 범위·완료 조건을 고정하고 현재 workspace와 사용자 변경을 먼저 확인합니다.
2. **지침 우선순위 및 사전 조사 (0.1 Instruction Priority & 2. Think Before Coding)**: 지침 충돌 시 명시적 사용자 지시 > 저장소 AGENTS.md > 중첩 AGENTS.md > 글로벌 규칙 > 일반 관례 순서를 따릅니다. 코딩 전 웹 검색으로 논문, 레퍼런스, 공식 가이드라인, 특허 만료 여부, 라이선스, 저작권을 확인하여 안전이 검증된 자료만 반영합니다.
3. **전체 파일 지도 및 소스 우선 인테이크 (10. Standard Workflow & 4. Surgical Changes)**: 변경 작업은 전체 파일 지도를 만든 뒤 저장소 지침과 진입점을 확인합니다. 영향 범위의 파일은 `view_file`로 처음부터 마지막 줄까지 연속해서 읽습니다. README·docs는 실제 소스와 관련 테스트를 모두 끝까지 읽은 뒤 대조합니다. IDE의 요약이나 파일명 목록은 읽은 것으로 보지 않습니다.
4. **쉘 및 IDE 우회 금지 (1. Core Operating Rule & 10. Standard Workflow)**: `cat`, `sed`, `head`, `tail`, `rg`, `git show`, `git diff`, Python·Node로 소스 확인 전 README·docs·Markdown을 먼저 훑지 않습니다. 소스 확인 전 shell 문서 읽기는 훅이 차단하며, 마지막 변경 뒤에는 실제 성공 결과가 있는 검증 명령이 필수입니다.
5. **책임 분리 및 500줄 제한 (15. Architecture Rules & 3. Simplicity First)**: 최소한의 코드로 해결하며 투기적 추상화·새 프레임워크·불필요한 의존성을 배제합니다. Single God Object를 방지하고 UI 상태·도메인 정책·IO·영속성·외부 프로세스·표현 책임을 가장 작은 응집 단위로 분리합니다. 파일당 500줄 제한 규칙(500-Line Limit Rule)을 준수합니다.
6. **디버깅 7단계 및 re-fix 루프 (12. Debugging Rules & 1. Core Operating Rule)**: 실제 문제를 재현하고 가장 작은 실패 면을 식별한 뒤 로그/스택트레이스를 분석하고 단일 가설 수립 → 패치 → 재검증 루프를 수행합니다. 막혔을 때는 Tested, Failed, Ruled out, Next cause를 보고합니다.
7. **테스트 및 검증 명령 규율 (17. Testing Rules & 11. Verification Commands)**: 동작을 검증하며 실패한 테스트를 임의로 삭제하지 않습니다. 언어별 표준 검증 명령(pnpm, pytest/ruff/pyright, cargo, swift)을 실행하고 미실행 시 이유와 정적 검체 내역을 밝힙니다.
8. **Git 및 보안 안전 수칙 (13. Git Rules & 14. Security Rules)**: 명시적 요청 없이 커밋·푸시·히스토리 수정을 하지 않으며, 비밀 파일(.env, *.key, id_rsa, ~/.ssh 등)을 절대 유출하지 않고 위험 명령어(sudo, rm -rf, curl|sh 등)를 실행하지 않습니다.
9. **UI·웹 구현 및 Chrome 렌더 계측 (16. UI / UX Rules & 8. UI Evidence)**: UI 작업 시 `docs/plans/`에 설계·구현·검증 계획을 작성하고 `scripts/verify_ui_render.py`로 320px·768px·1280px 렌더링, 수평 overflow, prefers-reduced-motion, 보이는 keyboard focus를 계측합니다. 다중 페이지 구조를 준수합니다.
10. **사람 중심 제품 카피 및 Zero AI Slop (16. UI/UX Rules & 0. Communication)**: "AI 특유의 서술 텍스트" 및 "AI 기술 서술 텍스트"를 전면 배제합니다. 특별한 사유가 없는 한 단답형을 금지하고 온전한 문장형 종결어미(~합니다, ~해요 등)를 사용하며, 비전공자도 단번에 알아들을 수 있는 쉬운 일상 언어로 작성합니다.
11. **장기 지평 유지 및 압축 전 보존 (6. Fable/Opus Long-Horizon Behavior & 19. Cost and Speed)**: 작업 지평을 끝까지 유지하며 컨텍스트 압축 전에는 Current goal, Files changed, Commands run, Passing checks, Failing checks, Next concrete step을 보존합니다.
12. **표준 최종 응답 포맷 (20. Final Response Format & 21. Hard Prohibitions)**: 최종 답변은 복명복창 후 핵심 원인 → 변경 내용 → 검증 결과 → 남은 리스크 순서로 한국어 존댓말 문장형 종결어미를 갖추어 간결하게 작성합니다. 8대 절대 금지 사항을 엄수합니다.

상세 규율 레퍼런스:
- [코딩 표준 및 8대 금지](references/coding-standards.md)
- [아키텍처 및 500줄 제한](references/architecture-rules.md)
- [디버깅 7단계 및 테스팅](references/debugging-and-testing.md)
- [보안 및 Git 안전 규칙](references/security-and-git.md)
- [언어별 검증 명령어](references/verification-commands.md)
- [저장소 표준 및 지침 우선순위](references/repository-standards.md)
- [UI 품질 계약](references/ui-quality.md)
