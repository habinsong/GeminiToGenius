# 공식 UI 근거

정확한 수치·검토 기준·출처가 필요할 때 읽습니다. 2026-08-02 확인.

- [Apple Design Principles](https://developer.apple.com/design/human-interface-guidelines/design-principles): 목적·유연성·단순성·완성도와 접근성을 제품 맥락에 맞춰 판단합니다.
- [Apple HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout): 창 폭과 읽기 순서에 맞춰 적응형 구조를 만들고, 필요한 경우 sidebar와 tab bar를 전환합니다.
- [Apple HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion): 상태·공간·주의를 설명하는 motion만 사용하고 감속 설정에서 반복·주변부 움직임을 줄입니다.
- [Apple HIG Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility): 키보드·대체 입력·단순한 제스처를 지원하고 빠르거나 깜박이는 장식 움직임과 시간 제한을 조심합니다.
- [Apple HIG Tab Bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars?changes=_1): tab bar는 top-level navigation이며 action bar가 아닙니다. 라벨·현재 위치·섹션별 상태를 보존합니다.
- [Apple HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials): 재료·투명도는 콘텐츠를 가리지 않는 계층과 접근성 설정에 맞춰 적용합니다.
- [Android Developers: Material 3 in Compose](https://developer.android.com/develop/ui/compose/designsystems/material3): 2026년 Material 3 Expressive를 포함하며 typography·shape·color·motion을 의미 역할로 관리합니다. 형태는 주의·상태·브랜드를 설명할 때 선택합니다.
- [Chrome cross-document View Transitions](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document): same-origin 다중 문서 전환을 점진 적용하되 일반 링크 fallback을 보존합니다.
- [Chrome Long Animation Frames](https://developer.chrome.com/docs/web-platform/long-animation-frames): 50ms 초과 프레임과 입력 blocking duration을 진단합니다. 측정하지 않은 성능 수치는 보고하지 않습니다.
- [web.dev Optimize INP](https://web.dev/articles/optimize-inp): field/lab를 구분하고 p75 200ms 이하 목표를 측정 근거와 함께 사용합니다.
- [web.dev prefers-reduced-motion](https://web.dev/articles/prefers-reduced-motion): 비필수 motion의 감속 대체 경로와 반복 움직임 감소를 요구합니다.
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/): [320 CSS px reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html), [보이는 focus](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html), [최소 24×24 CSS px target](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [상호작용 애니메이션 대체](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)를 실제 화면에서 확인합니다.
- [Google Research: Usability Hasn’t Peaked](https://research.google/pubs/usability-hasnt-peaked-exploring-how-expressive-design-overcomes-the-usability-plateau/): 표현적 디자인은 과업 수행을 돕는지 검증될 때만 선택하며, 스타일 유행의 기본값으로 취급하지 않습니다.
- [Android adaptive do's and don'ts](https://developer.android.com/develop/adaptive-apps/guides/adaptive-dos-and-donts): 실제 창 크기와 window size class를 기준으로 pane과 입력을 적응시키고, 콘텐츠 pane이 아니면 넓은 화면에 컨트롤을 억지로 늘리지 않습니다.
- [Material 3 Adaptive](https://developer.android.com/jetpack/androidx/releases/compose-material3-adaptive): 2026년 stable 1.2.0과 1.3.0-rc01의 adaptive scaffold·pane·window configuration 근거입니다. 웹 구현에 API를 복사하지 않고 창 크기별 관계만 참고합니다.
- [Design Theater](https://arxiv.org/abs/2607.22928): 생성 UI가 선언한 rationale과 실제 구현을 분리해 점검해야 하며 기능 요구사항 누락이 시각 요구보다 높게 나타났습니다.
- [FlowEval](https://arxiv.org/abs/2605.04165): 화면 외관만이 아니라 실제 사이트와 생성 UI의 상호작용 trace를 비교하는 검증 근거입니다.
- [Bridging Gulfs in UI Generation](https://arxiv.org/abs/2601.19171): 디자인 의도를 명시적 semantic representation으로 중간에 고정할 때 결과 해석과 반복 수정이 더 예측 가능해집니다.
- [GUIDE](https://research.google/pubs/guide-a-benchmark-for-user-context-understanding-and-assistance-in-gui-workflow-videos/): GUI 작업을 행동만 자동화하지 말고 사용자의 의도와 맥락을 함께 이해·지원해야 한다는 평가 근거입니다.

수치는 실제로 측정·검사했을 때만 완료 근거로 사용합니다. 제품 문맥과 기존 디자인 시스템이 우선이며, 특정 시각 스타일을 공식 기준처럼 강제하지 않습니다.
