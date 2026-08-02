# 2026 인터페이스 근거

계획과 검증 항목을 고를 때 확인한 공식·1차 자료입니다. 2026-08-02 확인.

- [Apple Design Principles](https://developer.apple.com/design/human-interface-guidelines/design-principles): 목적, 유연성, 단순성, 완성도를 제품 맥락에 맞춰 판단하며 접근성을 처음부터 고려합니다. 특정 스타일을 복제하라는 지침이 아닙니다.
- [Apple HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout): 창 크기·방향·텍스트·지역화에 맞춰 구조와 읽기 순서를 적응시키고, 필요하면 sidebar와 tab bar를 폭에 맞춰 전환합니다.
- [Apple HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion): motion은 상태·공간·주의를 설명할 때만 사용하고, 선택 가능하며, 감속 설정에서 반복·주변부 움직임을 줄입니다.
- [Apple HIG Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility): 키보드만으로 이동하고, 익숙한 입력 대안을 제공하며, 빠르거나 깜박이는 장식 움직임과 시간 제한을 조심합니다.
- [Apple HIG Tab Bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars?changes=_1): tab bar는 top-level navigation이며 action bar가 아닙니다. 라벨과 현재 위치를 보이고 섹션별 탐색 상태를 보존합니다.
- [Apple HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials): 재료와 투명도는 underlying content를 가리지 않는 계층과 시스템 설정·접근성 상태에 맞춰 적용합니다.
- [Android Developers: Material 3 in Compose](https://developer.android.com/develop/ui/compose/designsystems/material3): 2026년 Material 3 Expressive를 포함하며 typography·shape·color·motion을 의미 있는 테마 역할로 관리합니다. shape는 주의를 모으고 상태·브랜드를 설명할 때 선택합니다.
- [Chrome cross-document View Transitions](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document): same-origin 다중 문서 전환은 @view-transition navigation auto로 점진 적용하고 지원하지 않는 브라우저의 일반 링크 fallback을 보존합니다.
- [Chrome Long Animation Frames](https://developer.chrome.com/docs/web-platform/long-animation-frames): 50ms를 넘는 렌더링 프레임과 입력이 포함된 blocking duration을 진단하는 자료입니다. 애니메이션을 넣었다는 사실만으로 성능을 주장하지 않고 실제 상호작용을 측정합니다.
- [web.dev Optimize INP](https://web.dev/articles/optimize-inp): field와 lab를 구분하고, p75 200ms 이하 목표를 측정 가능한 근거와 함께 사용합니다.
- [web.dev prefers-reduced-motion](https://web.dev/articles/prefers-reduced-motion): 비필수 motion에 감속 대체 경로를 제공하고, 자동 반복 움직임을 줄입니다.
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/): [320 CSS px reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html), [보이는 focus](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html), [최소 24×24 CSS px target](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [상호작용 애니메이션 대체](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)를 계획과 실제 화면에서 확인합니다.
- [Google Research: Usability Hasn’t Peaked](https://research.google/pubs/usability-hasnt-peaked-exploring-how-expressive-design-overcomes-the-usability-plateau/): 48명·10개 앱 연구의 표현적 Material 변형 결과를 “화려함”의 근거가 아니라, 표현성이 정보 탐색과 과업 수행을 개선하는지 검증해야 한다는 근거로만 사용합니다.

검색 요약만으로 구현을 결정하지 않습니다. 저장소의 실제 소스·상태·콘텐츠와 위 자료를 대조하고, 계획한 시각 효과와 상호작용을 320px·중간 폭·1280px 및 실제 화면에서 확인합니다.
