---
name: interface-planning
description: Plans multi-page product interfaces before implementation, including user tasks, content hierarchy, routes, states, responsive behavior, motion, accessibility, responsibility boundaries, and verification commands. Use automatically for UI 계획, 화면 설계, 웹사이트 구조, multi-page, route map, design plan, implementation plan, verification plan, or before building a substantial frontend.
---

# 인터페이스 계획

UI를 바로 쓰지 않습니다. 먼저 저장소의 실제 소스·진입점·관련 테스트를 읽고 `docs/plans/`에 다음 세 파일을 만듭니다.

- `design-plan.md`: 사용자와 주 행동, 정보 위계, 페이지/경로, loading·empty·error·success·disabled·selected·focus 상태, 모바일 우선 반응형, 키보드, 감속 모션, 실제 근거를 적습니다. 선택한 visual direction과 제품 근거·대안·trade-off를 적어 특정 유행을 기본값으로 만들지 않습니다. motion마다 목적·대상·대략적인 duration/easing과 감속 대체를 적습니다.
- `implementation-plan.md`: 변경 파일, 책임 경계, 상태·데이터 흐름, 라우트 계약, 의존 방향, 단계, 위험과 복구를 적습니다. UI 상태·도메인 판단·IO·영속성·외부 프로세스를 God Object에 넣지 않습니다.
- `verification-plan.md`: 실행할 명령, 각 경로의 320px·768px 중간 폭·1280px 확인, overflow·키보드 focus·접근 가능한 이름·최소 조작 크기·감속 모션·상태 전환·성능 측정·스크린샷 증거와 통과/실패 기준을 적습니다.

`website`, `webpage`, `repository site`처럼 설명할 대상과 흐름이 둘 이상이면 `Route:` 항목을 두 개 이상 만들고 다중 페이지로 구현합니다. 단일 페이지가 맞다면 그 이유와 페이지 전환을 만들지 않는 근거를 계획에 남깁니다. 링크는 실제 같은 출처 경로로 연결하고 각 페이지에 고유한 목적·제목·`main`·`h1`을 둡니다.

계획을 쓴 뒤 `python3 ~/.gemini/config/agy-focus/current/scripts/verify_plan.py <workspace> --require-multi-page`를 상황에 맞게 실행합니다. 구현 뒤에는 `verify_multi_page.py`로 모든 HTML 경로를 Chrome에서 320px·768px·1280px로 렌더링하고 스크린샷을 직접 엽니다. 렌더 검사는 문서 언어·charset·title/h1/main·이미지 alt·접근 가능한 이름·24 CSS px 조작 영역·실제 focus 스타일·overflow와 CLS/Long Animation Frames 계측도 반환합니다. `prefers-reduced-motion`과 보이는 키보드 focus가 없으면 완료로 쓰지 않습니다.

시각 방향은 유행을 고르는 문제가 아닙니다. 실제 사용자·콘텐츠·상태·환경이 설명하는 위계를 선택합니다. 같은 카드·표·rounded shell·그라데이션을 반복하지 않으며, 표현적인 색·서체·움직임도 해당 정보나 행동을 더 빨리 찾게 하는지 근거를 적습니다. 최소 두 가지 가능한 방향을 비교하고 선택 이유·버린 대안·위험을 계획에 남깁니다. 표현성은 Google 연구의 특정 스타일을 복제하는 근거가 아니라 과업 수행 개선을 검증할 때만 선택하는 가설입니다.

정확한 반응형·motion·접근성·성능 근거가 필요한 경우 [2026 인터페이스 근거](references/evidence.md)를 읽고 해당 URL을 계획의 출처 항목에 적습니다.
