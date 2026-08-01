---
name: interface-implementation
description: Implements product UI/UX, frontend screens, responsive CSS, components, forms, and interactions from real user tasks and existing design systems. Use automatically for UI 만들어, 화면 만들어, 페이지 만들어, 컴포넌트 추가, CSS 고쳐, 반응형 구현, 버튼 고쳐, 디자인 구현, frontend build, implement UI, build page, responsive CSS, component, form, or layout without requiring @mentions or slash commands.
---

# 인터페이스 구현

1. 실제 사용자, 핵심 작업, 데이터, 상태, 기존 화면·토큰을 먼저 확인합니다. 근거가 없으면 새 브랜드나 도메인 요소를 발명하지 않습니다.
2. 모바일의 읽기 순서와 조작을 먼저 만들고 `min-width`로 넓은 상태를 확장합니다. 컨테이너는 콘텐츠 관계를 따라 만들고, `width: 100%`·`flex-grow: 1`·카드를 화면 채우기 용도로 반복하지 않습니다.
3. `fit-content`·`min-content`·`clamp()`·그리드·플렉스·일반 흐름은 콘텐츠·위계·접근성을 개선할 때만 선택합니다. 비대칭·겹침·Command Bar도 같은 기준으로 판단합니다.
4. 보라·파랑 그라데이션, 무근거 `Inter`, 요술봉·추상 아이콘, 작위적 3D 이미지, 가짜 지표, 장식용 채팅창·관제 화면을 기본값으로 쓰지 않습니다.
5. 움직임은 상태 변화·관계·긴급한 주의 중 하나를 설명할 때만 넣습니다. hover 자체를 이유로 애니메이션을 넣지 않고 감속 설정을 존중합니다.
6. 키보드 포커스, 색상 외 상태 표시, 오류·빈 상태, 좁은 폭의 오버플로우·가려진 조작을 구현합니다.
7. 실제 화면을 렌더링해 가장 좁은 지원 폭과 넓은 폭을 확인합니다. 확인하지 못한 시각 품질은 통과로 쓰지 않습니다.
