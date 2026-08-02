# 2026 인터페이스 근거

확정적인 디자인 취향이 아니라, 계획과 검증 항목을 고를 때 쓰는 1차 자료입니다. 2026-08-02 확인.

- [Apple HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout): 창 크기·방향·텍스트·지역화에 맞춰 구조와 읽기 순서를 적응시키고, navigation을 콘텐츠와 함께 설계합니다.
- [Apple HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion): motion은 공간·상태·주의를 설명할 때만 쓰고, 짧고 정확하며 끌 수 있어야 합니다. 반복적인 장식 움직임은 넣지 않습니다.
- [Apple HIG Tab Bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars?changes=_1): 탭은 top-level navigation이지 동작 버튼이 아니며, 라벨을 보이고 상태를 보존하고 overflow를 피합니다.
- [Apple WWDC26 Principles of great design](https://developer.apple.com/videos/play/wwdc2026/250/): 일관된 동작과 개인의 작업 흐름에 맞춘 유연한 구조를 강조합니다.
- [Chrome cross-document View Transitions](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document): same-origin 다중 문서 전환은 `@view-transition { navigation: auto; }`로 점진 적용할 수 있고, 미지원 환경의 fallback을 남깁니다.
- [web.dev Optimize INP](https://web.dev/articles/optimize-inp): p75 200ms 이하를 목표로 field와 lab를 구분해 측정하고, long task·DOM 크기·layout thrash를 줄입니다. 측정하지 않은 수치는 주장하지 않습니다.
- [W3C WCAG 2.2 Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html), [Target Size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [Focus Appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html): 320 CSS px 재배치, 타깃, 보이는 focus를 계획에 포함합니다.
- [Google Research: Usability Hasn’t Peaked](https://research.google/pubs/usability-hasnt-peaked-exploring-how-expressive-design-overcomes-the-usability-plateau/): 48명·10개 앱 연구에서 Material 3 Expressive 변형의 과업 수행과 시선 고정 개선을 보고합니다. 이는 특정 스타일을 복제하라는 뜻이 아니라 표현성이 정보 탐색을 도울 때만 선택하라는 근거입니다.

검색 요약만으로 구현을 결정하지 않습니다. 작업 저장소의 실제 소스·상태·콘텐츠와 위 자료를 대조하고, 계획한 효과를 실제 화면에서 확인합니다.
