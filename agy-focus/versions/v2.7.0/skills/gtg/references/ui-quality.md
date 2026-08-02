# GTG UI 품질 계약

## 먼저 확보할 근거

- 실제 사용자와 한 화면의 주 행동
- 실제 제품 기능, 데이터, 제약, 용어, 지원 상태
- 기존 화면, 디자인 토큰, 플랫폼 관례
- loading, empty, error, success, disabled, focus, selected, 긴 콘텐츠 상태

근거가 없으면 새 브랜드·가짜 기능·지표·후기·고객·로고·대시보드를 발명하지 않습니다.

## 실패 패턴

- 중앙 히어로, 그라데이션 제목, 떠 있는 목업, 동일한 3열 카드 조합
- 보라색→파란색 또는 다색 그라데이션, glow, blob, glass, blur, 부드러운 그림자
- 모든 요소의 12–16px radius, 같은 24px 여백, 카드 안 카드, pill 남용
- `Inter`, `Roboto`, `Arial`을 새 화면의 무근거 기본값으로 선택
- 요술봉, 반짝이, 별, 추상 도형, 작위적 AI 3D 일러스트
- 기능을 설명하지 않는 “Build the future”, “Unlock”, “Seamless”, “혁신”, “차세대” 카피
- hover에서 이유 없이 뜨기·확대·회전·빛나기, 장식용 parallax·scroll animation
- 좌측 카피+우측 앱 캡처, 균등한 12단 grid, 같은 높이 카드의 기계적 반복
- 화면을 채우기 위한 `width: 100%`, `flex-grow: 1`, 고정 sidebar의 습관적 사용
- AI SaaS 대신 자동 선택한 GitHub/Vercel풍 다크 문서, 검은 배경+시안/청록 포인트+모노스페이스 terminal 미학, 네오 브루탈리즘
- 다크 문서를 `#f8fafc`·`#0f172a`·`#e2e8f0` 중심 Tailwind Slate 라이트 문서로 단순 반전
- header·main·footer를 같은 중앙 max-width로 맞추고 모든 내용을 세로 문서 섹션으로만 쌓는 안전한 템플릿
- 배경·1px 테두리·동일 패딩 상자를 설치 흐름·증거·구성요소마다 반복하는 무표정한 박스 레이아웃
- 저장소의 모든 규칙·스킬을 긴 표와 카탈로그로 옮겨 놓고 사용자가 먼저 알아야 할 효과·설치·한계를 뒤로 미루는 구성
- 정적 설명 페이지에 요청하지 않은 scroll spy, 복사 버튼, 필터, parallax, smooth scroll JavaScript 추가

실패 예시: 제품 근거 없이 “강력한 하네스 / 더 빠른 개발 / 완벽한 품질” 카드 세 개와 99% 지표를 보라색 glow 위에 배치합니다.

통과 예시: 저장소에서 확인한 한 문장 정의·실제 설치 명령·읽기/쓰기/종료 게이트·복구 경로를 먼저 보여주고, 세부 규칙 수는 보조 정보로 내립니다. 명령은 설치 스크립트와 대조하고 제한은 짧게 분리합니다.

## 구조

1. 카드보다 시맨틱 section·목록·표·구분선·macro whitespace·타이포그래피 대비를 먼저 사용합니다.
2. 콘텐츠의 실제 크기에 `fit-content`, `min-content`, `max-content`와 일반 흐름을 사용합니다. 전체 폭은 관계상 필요한 경우에만 씁니다.
3. desktop 대칭 grid를 줄이는 방식으로 시작하지 않습니다. 작은 화면의 읽기 순서를 먼저 만들고 콘텐츠가 깨지는 지점에서 `min-width` 또는 container query로 확장합니다.
4. 큰 화면에서는 `grid-template-areas`, 불균형한 column, 의도적인 빈 공간, 제한된 overlap을 제품 관계가 설명할 때만 사용합니다. 비대칭 자체를 장식으로 쓰지 않습니다.
5. 카드·면 대신 headline 크기 대비, baseline, 구분선, 여백으로 영역을 나눕니다. `clamp()`는 글자와 macro spacing의 연속 변화에 사용합니다.
6. 고정 sidebar 대신 작업 빈도와 문맥에 맞는 navigation, command bar, context menu, progressive disclosure를 선택합니다. 숨김 자체가 목표가 되어서는 안 됩니다.
7. 경계는 기본적으로 0–8px radius, 1px 단색 선, 명확한 면 대비를 사용합니다. offset shadow나 질감은 브랜드·상태 근거가 있을 때 한정합니다.
8. 금지 목록 자체를 디자인 시스템으로 쓰지 않습니다. dark, mono, Swiss, brutalist, editorial 중 어느 것도 제품 근거 없는 기본값이 아닙니다.
9. “clean”, “modern”, “professional”, “developer aesthetic” 같은 형용사를 시각 방향으로 쓰지 않습니다. 실제 제품의 자료·언어·도구·사용 장면에서 한 가지 식별 가능한 방향을 선택합니다.

## 카피

- h1은 페이지가 설명하거나 수행하는 일을 직접 말합니다.
- 버튼은 실행 동작, 오류는 문제와 복구 방법, 링크는 목적지를 단독으로 읽어도 알 수 있게 씁니다.
- 한 문장에는 한 정보만 두고 중요한 단어를 앞에 둡니다.
- AI 자기소개, 환영 문단, 분위기 서술, 근거 없는 수식어, 추상 약속을 삭제합니다.
- 같은 높임말 종결을 길게 반복하지 않습니다. 명사형 제목, 짧은 사실, 실제 명령, 제한 문구로 나눕니다.

## 접근성·반응형·검증

- 320 CSS px에서 비예외 콘텐츠가 양방향 스크롤 없이 재배치되어야 합니다.
- 768 CSS px 중간 폭에서 모바일과 데스크톱 사이의 전환이 고아 열·겹친 조작·갑작스러운 정보 누락을 만들지 않아야 합니다.
- 보이는 keyboard focus, 문서 언어·charset·title/h1/main, 이미지 alt, 접근 가능한 이름, 색상 외 상태, 본문 4.5:1 대비, 24×24 CSS px 이상 타깃을 확인합니다.
- hover에 필수 정보나 조작을 숨기지 않습니다.
- 움직임은 상태·공간 관계·필수 주의를 설명할 때만 사용하고 `prefers-reduced-motion`에서 비필수 움직임을 제거합니다.
- `restrained`와 `expressive` 중 하나를 제품 맥락으로 선택하되, 표현성 자체를 품질로 취급하지 않습니다. View Transition·scroll-driven·scroll-triggered 효과는 이동 경로·상태·주의를 설명할 때만 쓰고 trigger·duration/easing·예산·fallback·감속 경로를 계획에 남깁니다. 실험적 masonry/Grid lanes는 지원 범위와 fallback이 확인되기 전 기본값으로 쓰지 않습니다.
- `python3 ~/.gemini/config/agy-focus/current/scripts/verify_ui_render.py <HTML> --output-dir <DIR>`로 320px·768px·1280px 렌더, `scrollWidth`, 요소 경계, 문서·접근성 계약, CLS·Long Animation Frames를 검사하고 모든 이미지를 직접 엽니다. `ok: true`가 아니면 잘린 요소를 고친 뒤 다시 실행합니다. HTTP 200·파서·`curl`은 시각 검증이 아닙니다. 측정하지 않은 INP·CLS·대비 수치를 주장하지 않습니다.
