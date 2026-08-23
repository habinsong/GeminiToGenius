---
name: interface-planning
description: Plans multi-page product interfaces before implementation, including user tasks, content hierarchy, routes, states, responsive behavior, motion, accessibility, responsibility boundaries, and verification commands. Use automatically for UI 계획, 화면 설계, 웹사이트 구조, multi-page, route map, design plan, implementation plan, verification plan, or before building a substantial frontend.
---

# 인터페이스 계획

UI를 바로 쓰지 않습니다. 먼저 저장소의 실제 소스·진입점·관련 테스트를 읽고 `docs/plans/`에 다음 세 파일을 만듭니다.

- `design-plan.md`: 사용자와 주 행동, 사용자 결과(success signal), 실패 시 recovery·retry·undo, 정보 위계, 페이지/경로, loading·empty·error·success·disabled·selected·focus 상태, 모바일 우선 반응형, 키보드, 감속 모션, 실제 근거를 적습니다. 가짜 윈도우 창틀(트래픽 라이트 점, 윈도우 타이틀바), 사이드바와 1px 사각 테두리 박스 덤프, 형광 네온사인 발광 컬러를 배제하고 웹 본연의 캔버스와 선명한 흑백 대비, 명확한 타이포그래피 위계를 계획합니다. `restrained` 또는 `expressive` 방향을 제품 근거로 선택하고 버린 대안·trade-off를 적습니다. adaptive 전략을 `reflow`·`reveal`·`presentation` 중에서 선택하고 전체 화면에서 compact로 바뀌는 조건, 선택한 WAI-ARIA 키보드 패턴을 적습니다. evidence matrix의 각 행에 출처 URL 하나와 그 출처의 근거 발견·결정 또는 구현 영향·검증 게이트를 같은 행에 기록합니다. 별도의 `Decision ledger` 표에서 최소 두 판단을 `Decision ID | User outcome | Decision | Rationale / evidence | Implemented in | Verified by`로 연결합니다.
- `implementation-plan.md`: 변경 파일, 책임 경계, 상태·데이터 흐름, 라우트 계약, 의존 방향, 단계, 위험과 복구를 적습니다. UI 상태·도메인 판단·IO·영속성·외부 프로세스를 God Object에 넣지 않습니다.
- `verification-plan.md`: 실행할 명령, 각 경로의 320px·768px 중간 폭·1280px 확인, 실제 사용자의 flow trace와 recovery path, 계획-구현 대조, 브라우저 화면 관찰, 독립 기준(공식 문서·실행 결과)을 적습니다. overflow·키보드 focus·접근 가능한 이름·최소 조작 크기·감속 모션·상태 전환·성능 측정·스크린샷 증거와 통과/실패 기준도 적습니다.

`website`, `webpage`, `landing page`, `repository site`, `static page`는 단일 페이지로 시작하지 않습니다. `Route:` 항목을 두 개 이상 만들고 각 페이지를 실제 경로로 구현합니다. 링크는 실제 같은 출처 경로로 연결하고 각 페이지에 고유한 목적·제목·`main`·`h1`을 둡니다.

계획을 쓴 뒤 `python3 ~/.gemini/config/agy-focus/current/scripts/verify_plan.py <workspace> --require-multi-page --require-ui-evidence`를 실행합니다. UI 근거는 Apple·Google·Chrome·W3C·HCI 연구와 주요 디자인 시스템 중 서로 다른 공식·1차 출처를 최소 4개, 3개 호스트, 4개 분야로 대조하고 URL마다 같은 matrix 행에 finding·impact·verification을 적어야 합니다. 구현 뒤에는 `verify_multi_page.py`로 모든 HTML 경로를 Chrome에서 320px·768px·1280px로 렌더링하고 스크린샷을 직접 엽니다.

카피는 "AI 특유의 서술 텍스트"와 "AI 기술 서술 텍스트"를 전면 배제하고, 특별한 사유가 없는 한 단답형을 금지하며 온전한 문장형 종결어미(~합니다, ~해요)를 사용하고, 비전공자도 단번에 알아들을 수 있는 쉬운 일상 언어로 작성하도록 계획합니다.

정확한 반응형·motion·접근성·성능 근거가 필요한 경우 [2026 인터페이스 근거](references/evidence.md)를 읽고 해당 URL을 계획의 출처 항목에 적습니다.
