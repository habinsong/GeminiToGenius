# 2026 인터페이스 근거

계획과 검증 항목을 고를 때 확인한 공식·1차 자료입니다. 2026-08-03 확인.

## v2.6 결정 매트릭스

| 근거 | 계획 결정 | 구현·검증 게이트 |
|---|---|---|
| [Apple HIG](https://developer.apple.com/design/human-interface-guidelines?lang=en), [WWDC26 Design](https://developer.apple.com/wwdc26/guides/design/) | hierarchy·harmony·consistency와 플랫폼별 적응을 제품 맥락으로 선택 | 실제 콘텐츠·긴 문자열·창 크기별 읽기 순서, 접근성 상태 확인 |
| [Apple Materials](https://developer.apple.com/design/human-interface-guidelines/materials), [WWDC26 UI agents](https://developer.apple.com/videos/play/wwdc2026/227/) | 기능·탐색 레이어와 콘텐츠 레이어를 구분하고 AI 출력은 초안으로만 취급 | 실제 콘텐츠·예외 상태·여러 미리보기와 핵심 상호작용을 직접 검토 |
| [Android adaptive layouts](https://developer.android.com/design/ui/mobile/guides/layout-and-content/adapt-layout?hl=en) | compact·medium·expanded에서 reflow·reveal·presentation을 계획하고 무조건 stretch하지 않음 | 320·768·1280에서 pane 수, max-width, overflow, 정보 손실을 측정 |
| [Chrome I/O 2026 Web UI](https://developer.chrome.com/blog/new-in-web-ui-io26?hl=en), [View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API) | route/state 전환은 이동 경로와 상태 변화를 설명할 때만 선택 | 일반 링크 fallback, focus·reading position·live region, reduced motion 확인 |
| [Chrome scroll-driven animation](https://developer.chrome.com/docs/css-ui/scroll-driven-animations?hl=en), [scroll-triggered animation](https://developer.chrome.com/blog/scroll-triggered-animations?hl=en) | 선언형·compositor 친화 효과만 목적이 있을 때 사용 | 장식용 parallax 금지, 실제 작업 개선과 50ms 이상 프레임을 측정 |
| [Chrome Long Animation Frames](https://developer.chrome.com/docs/web-platform/long-animation-frames) | 모션 예산과 측정 경로를 계획에 포함 | Long Animation Frames·CLS를 실제 렌더에서 기록하고 미측정 INP를 주장하지 않음 |
| [W3C WCAG 2.2](https://www.w3.org/WAI/WCAG22/understanding/) | reflow·focus appearance·target·animation from interactions를 화면 계약으로 고정 | 키보드 focus, 24 CSS px target, 320px reflow, 감속 대체를 통과 조건으로 확인 |
| [W3C Tabs APG](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/), [W3C Grid APG](https://www.w3.org/WAI/ARIA/apg/patterns/grid/) | 컴포넌트별 키보드 패턴과 자동 활성화 조건을 임의로 만들지 않음 | 역할·aria 상태·키보드 순서·지연 없는 자동 활성화를 실제 조작으로 확인 |
| [CHI 2026](https://chi2026.acm.org/), [Google Research: adaptive generative interfaces](https://research.google/pubs/self-evolving-systems-moving-beyond-deterministic-interfaces-to-adaptive-generative-interfaces/) | 적응형·생성형 UI는 연구 가설과 평가 방법으로만 사용 | 고정된 route/state 계약과 사용자 과업 평가 없이 레이아웃을 동적으로 발명하지 않음 |
| [Google GUIDE](https://research.google/pubs/guide-a-benchmark-for-user-context-understanding-and-assistance-in-gui-workflow-videos/), [Design Theater](https://arxiv.org/abs/2607.22928), [FlowEval](https://arxiv.org/abs/2605.04165) | 계획의 사용자 의도·상태·흐름을 실제 구현·검증 trace와 대조 | 화면 캡처만 보지 않고 경로·행동·상태 전이를 독립 기준으로 확인 |

모션은 `restrained` 또는 `expressive` 중 하나를 제품 근거로 선택합니다. 두 방향의 장점·버린 대안·목적·트리거·duration/easing·예산·감속 대체를 `design-plan.md`에 적지 않으면 계획을 통과시키지 않습니다. Chrome의 실험적 Grid lanes·masonry 문법은 지원 범위와 fallback을 확인하기 전 기본 레이아웃으로 쓰지 않습니다.

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
