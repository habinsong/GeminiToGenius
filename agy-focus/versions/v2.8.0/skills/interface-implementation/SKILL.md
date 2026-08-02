---
name: interface-implementation
description: Implements product UI/UX, frontend screens, responsive CSS, components, forms, and interactions from real user tasks and existing design systems. Use automatically for UI 만들어, 화면 만들어, 페이지 만들어, 컴포넌트 추가, CSS 고쳐, 반응형 구현, 버튼 고쳐, 디자인 구현, frontend build, implement UI, build page, responsive CSS, component, form, or layout without requiring @mentions or slash commands.
---

# 인터페이스 구현

1. 코드보다 먼저 실제 사용자, 핵심 작업, 주요 데이터, 전체 상태, 지원 기기·입력, 기존 화면·디자인 토큰을 적고 `docs/plans/`의 설계·구현·검증 계획을 작성합니다. 근거가 없으면 새 브랜드·가짜 콘텐츠·범용 SaaS 화면을 발명하지 않습니다.
2. 제품 고유의 시각 방향을 도메인 자료·콘텐츠 밀도·사용 환경에서 고릅니다. 가능한 방향을 둘 이상 짧게 비교하고 선택 이유와 trade-off를 계획에 남깁니다. 서체·색·간격·형태마다 기능 또는 브랜드 근거를 하나씩 제시할 수 있어야 하며, 단지 달라 보이기 위한 유행 스타일은 적용하지 않습니다.
3. 장식 전에 의미 구조와 위계를 만듭니다. 한 화면의 주 행동을 분명히 하고, 제목·본문·데이터·보조 행동의 순서를 시맨틱 구조와 시각적 강도로 일치시킵니다.
4. 중앙 정렬 히어로+그라데이션 제목+떠 있는 목업+동일한 3개 카드, 카드 안 카드, 모든 요소의 같은 여백·radius, pill 남용, 보라·파랑 네온, glow·blob·유리 효과, 요술봉·별·추상 아이콘, 작위적 3D 이미지, 가짜 지표·후기·로고·대시보드를 기본 조합으로 쓰지 않습니다.
5. anti-slop은 별도 시각 스타일이 아닙니다. GitHub/Vercel풍 다크 문서, terminal 미학, 네오 브루탈리즘, 긴 표·정의 목록도 제품 근거 없이 기본값으로 쓰지 않습니다.
6. `Inter`·`Roboto`·`Arial`과 라이브러리 기본 토큰은 기존 제품이 실제로 쓰거나 사용자가 지정한 경우만 유지합니다. 새 서체는 읽기 성능·문자 지원·로딩 fallback을 확인하고, 색상은 장식보다 정보·상태·행동 구분에 씁니다.
7. 모바일 읽기 순서와 터치 조작부터 만들고 콘텐츠가 깨지는 지점에서 `min-width` 또는 container query로 확장합니다. `width: 100%`·`flex-grow: 1`은 실제 관계상 필요할 때만 쓰고, intrinsic sizing·일반 흐름·grid·flex를 콘텐츠에 맞게 선택합니다.
8. 320 CSS px에서 정보와 조작이 양방향 스크롤 없이 재배치되게 합니다. 화면 폭 때문에 필요한 콘텐츠를 숨기지 않고, 이미지·영상·지연 콘텐츠의 공간을 미리 확보합니다.
9. 가능한 경우 네이티브 HTML·플랫폼 컨트롤과 기존 컴포넌트를 사용합니다. 키보드 순서와 보이는 focus, 접근 가능한 이름, 색상 외 상태, 본문 4.5:1·큰 글자 3:1 대비, 최소 24×24 CSS px 타깃을 확인합니다.
10. loading·empty·error·success·disabled·focus·selected·long content·real data 상태를 구현합니다. 즉시 끝나는 작업에 skeleton을 넣거나 빈 공간을 가짜 데이터로 채우지 않습니다.
11. hover에서만 정보나 조작을 제공하지 않습니다. 움직임은 상태 변화·공간 관계·필수 주의를 설명할 때만 쓰고 `prefers-reduced-motion` 또는 플랫폼 감속 설정에서 비필수 움직임을 제거합니다. 정적 페이지에는 요청하지 않은 JavaScript를 추가하지 않습니다.
12. 반복 UI와 상태·도메인·IO를 한 컴포넌트에 몰지 않고 `architecture-boundaries`를 따릅니다. 컴포넌트 분리는 책임과 재사용 근거가 있을 때만 합니다.
13. 웹 UI는 기본 제공 `scripts/verify_ui_render.py`로 320px·768px·1280px 렌더와 수평 overflow를 계측하고 모든 스크린샷을 직접 엽니다. 이 검사는 문서 언어·charset·title/h1/main·이미지 alt·접근 가능한 이름·24 CSS px 조작 영역·실제 focus 스타일·CLS·Long Animation Frames·실제 모션·reduced-motion emulation을 반환합니다. 키보드·터치·상태 전환도 조작합니다. 측정 가능한 환경에서 INP 200ms 이하와 CLS 0.1 이하를 확인하되 측정하지 않았으면 수치를 주장하지 않습니다.
14. 페이지 목적과 사용자 흐름이 둘 이상이면 다중 페이지를 계획하고 구현합니다. 각 경로는 고유한 `title`·`h1`·`main`과 실제 링크를 가져야 하며 `verify_multi_page.py`로 모든 경로를 320px·768px·1280px에서 렌더합니다. `prefers-reduced-motion` 감속 규칙이 실제 animation/transition을 줄이고 보이는 `:focus-visible`가 없으면 완료로 쓰지 않습니다.

정확한 접근성·반응형·성능 수치나 출처가 필요한 작업에서는 [공식 UI 근거](references/evidence.md)를 읽습니다.
