---
name: ui-evidence-review
description: Reviews completed or existing UI/UX, frontend screens, responsive layout, visual hierarchy, interactions, design systems, and interface copy against real product evidence. Use automatically for UI 검토, 디자인 검토, 화면 점검, 접근성 확인, 반응형 확인, UX review, UI review, visual QA, design audit, accessibility review, or layout review without requiring @mentions or slash commands.
---

# UI 증거 검토

완성된 화면이나 기존 화면을 근거로 검토합니다. 구현 규율은 `interface-implementation`에 둡니다.

1. 실제 사용자 목표, 주 행동, 데이터 우선순위, 전체 상태, 기존 디자인 시스템을 코드와 화면에서 확인합니다. README 설명만으로 화면 목적을 확정하지 않습니다.
2. 화면의 구성 요소를 다른 서비스로 그대로 옮겨도 자연스러운지 묻습니다. 그렇다면 도메인 정보·작업 순서·콘텐츠 차이가 시각 구조에 반영되지 않은 AI Slop으로 봅니다.
3. 중앙 히어로·그라데이션 문구·떠 있는 목업·동일 카드 3개, 카드 중첩, 같은 radius·간격 반복, pill·glow·blob·콘텐츠 면의 장식용 유리 효과, 무근거 `Inter`, 요술봉·별·추상 아이콘, 가짜 지표·후기·회사·AI 배지·3D 장식을 찾습니다. 기능 근거가 없으면 제거합니다. 기능 계층에 남긴 재료는 콘텐츠를 가리지 않는지와 접근성 fallback을 직접 확인합니다.
4. 위 요소를 제거한 뒤 GitHub/Vercel풍 다크 문서, terminal 미학, 네오 브루탈리즘, 긴 표·정의 목록으로 자동 치환했는지도 확인합니다. anti-slop을 스타일로 취급하면 실패입니다.
5. 헤드라인·레이블·링크·오류가 실제 기능·현재 상태·다음 행동을 직접 설명하는지 확인합니다. 미래 약속·빈 칭찬·AI 특유의 서술형 문단·가짜 콘텐츠는 통과시키지 않습니다.
6. 첫 시선이 주 행동과 가장 중요한 정보로 가는지, 관련 항목은 묶이고 다른 항목은 분리되는지, 모든 요소가 동시에 강조되지 않는지 확인합니다.
7. 기본 제공 `scripts/verify_ui_render.py`로 320 CSS px·768px·1280px의 `scrollWidth`와 요소 경계를 계측하고 모든 스크린샷을 엽니다. 중간 폭에서도 읽기 순서, 콘텐츠 기반 breakpoint, 양방향 스크롤, 가려진 조작, media 공간 예약, 긴 문자열을 확인합니다. 렌더 결과의 문서 언어·charset·title/h1/main·이미지 alt·접근 가능한 이름·24 CSS px 조작 영역·실제 focus 스타일도 확인합니다. 폭이 좁다는 이유로 필요한 내용을 숨기지 않습니다.
8. 네이티브 의미 구조, 키보드 순서, 보이는 focus, 접근 가능한 이름, 색상 외 상태, 본문 4.5:1·큰 글자 3:1 대비, 최소 24×24 CSS px 타깃, 감속 설정을 확인합니다.
9. loading·empty·error·success·disabled·focus·selected와 실제 데이터 상태를 조작합니다. hover-only 기능, 목적 없는 motion, 반복해서 시간을 뺏는 transition, 예상치 못한 layout shift를 실패로 봅니다.
10. 320px·768px·1280px를 비교하고, 화면이 다른 시각 방향을 선택했다는 이유만으로 감점하지 않습니다. 제품 과업·위계·접근성·상태·성능을 더 잘 설명하는지와 계획에 사용자 결과·복구 경로·선택 근거·대안·trade-off가 있는지를 평가합니다. 계획의 Decision ID가 실제 파일과 검증 결과에 존재하는지 확인합니다.
11. 웹 성능을 측정할 수 있으면 INP 200ms 이하와 CLS 0.1 이하를 확인합니다. Chrome이 제공하는 Long Animation Frames와 CLS는 진단 자료로만 사용하고 실제 상호작용을 측정하지 않은 상태에서 INP를 추정하지 않습니다. 측정하지 않은 수치와 렌더링하지 않은 시각 품질은 통과로 쓰지 않습니다.
12. 실패한 요소만 수정하고 새 유행 스타일로 전체 화면을 덮지 않습니다. 실제 화면을 다시 렌더링해 같은 항목을 재검증합니다.

결과에는 바꾼 UI 요소, 실제 확인한 화면 상태, 확인하지 못한 시각 검증만 짧게 남깁니다.

정확한 접근성·반응형·성능 수치나 출처가 필요한 검토에서는 [공식 UI 근거](../interface-implementation/references/evidence.md)를 읽습니다.
