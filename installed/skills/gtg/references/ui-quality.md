# GTG UI 품질 계약

## 먼저 확보할 근거

- 실제 사용자와 한 화면의 주 행동
- 실제 제품 기능, 데이터, 제약, 용어, 지원 상태
- 기존 화면, 디자인 토큰, 플랫폼 관례
- loading, empty, error, success, disabled, focus, selected, 긴 콘텐츠 상태

근거가 없으면 새 브랜드·가짜 기능·지표·후기·고객·로고·대시보드를 발명하지 않습니다.

## 실패 패턴 (절대 금지)

- 가짜 윈도우 창틀(트래픽 라이트 점, 윈도우 캡션바)이나 조잡한 데스크톱 앱 흉내
- 좌측 어두운 사이드바 + 우측 1px 사각 테두리 박스(Card/Panel) 무한 나열 덤프
- 형광 초록, 네온 파랑, 형광 시안/보라 등 눈을 피로하게 만드는 네온사인 발광 색상
- 중앙 히어로, 그라데이션 제목, 떠 있는 목업, 동일한 3열 카드 조합
- 보라색→파란색 또는 다색 그라데이션, glow, blob, glass, blur, 부드러운 그림자
- 모든 요소의 12–16px radius, 같은 24px 여백, 카드 안 카드, pill 남용
- `Inter`, `Roboto`, `Arial`을 새 화면의 무근거 기본값으로 선택
- 요술봉, 반짝이, 별, 추상 도형, 작위적 AI 3D 일러스트
- 기능을 설명하지 않는 “Build the future”, “Unlock”, “Seamless”, “혁신”, “차세대” 카피
- hover에서 이유 없이 뜨기·확대·회전·빛나기, 장식용 parallax·scroll animation
- AI SaaS 대신 자동 선택한 GitHub/Vercel풍 다크 문서, 검은 배경+시안/청록 포인트+모노스페이스 terminal 미학, 네오 브루탈리즘
- 다크 문서를 `#f8fafc`·`#0f172a`·`#e2e8f0` 중심 Tailwind Slate 라이트 문서로 단순 반전
- header·main·footer를 같은 중앙 max-width로 맞추고 모든 내용을 세로 문서 섹션으로만 쌓는 안전한 템플릿
- 배경·1px 테두리·동일 패딩 상자를 설치 흐름·증거·구성요소마다 반복하는 무표정한 박스 레이아웃

## 구조

1. 사각 테두리 박스보다 시맨틱 section·목록·구분선·넓은 여백·타이포그래피 대비를 먼저 사용합니다.
2. 콘텐츠의 실제 크기에 `fit-content`, `min-content`, `max-content`와 일반 흐름을 사용합니다. 전체 폭은 관계상 필요한 경우에만 씁니다.
3. desktop 대칭 grid를 줄이는 방식으로 시작하지 않습니다. 작은 화면의 읽기 순서를 먼저 만들고 콘텐츠가 깨지는 지점에서 `min-width` 또는 container query로 확장합니다.
4. 큰 화면에서는 `grid-template-areas`, 불균형한 column, 의도적인 빈 공간, 제한된 overlap을 제품 관계가 설명할 때만 사용합니다.
5. 카드·면 대신 headline 크기 대비, baseline, 구분선, 여백으로 영역을 나눕니다.
6. 고정 sidebar 대신 작업 빈도와 문맥에 맞는 상단 navigation, command bar, context menu, progressive disclosure를 선택합니다.
7. 경계는 기본적으로 0–8px radius, 1px 단색 선, 명확한 면 대비를 사용합니다.
8. 금지 목록 자체를 디자인 시스템으로 쓰지 않습니다.
9. 실제 제품의 자료·언어·도구·사용 장면에서 식별 가능한 방향을 선택합니다.

## 카피 및 언어 원칙

- h1은 페이지가 설명하거나 수행하는 일을 직접 말합니다.
- "AI 특유의 서술 텍스트"와 "AI 기술 서술 텍스트", 장황한 기술 은어 나열, AI Slop 카피를 전면 금지합니다.
- 특별한 사유(버튼 이름 등)가 없는 한 단답형 나열을 금지하며, 친절하고 온전한 문장형 종결어미(~합니다, ~해요 등)를 사용합니다.
- 비전공자나 일반 사용자도 단번에 이해할 수 있는 쉬운 일상 언어로 작성합니다.
- 버튼은 실행 동작, 오류는 문제와 복구 방법, 링크는 목적지를 단독으로 읽어도 알 수 있게 씁니다.
- 한 문장에는 한 정보만 두고 중요한 단어를 앞에 둡니다.

## 접근성·반응형·검증

- 320 CSS px에서 비예외 콘텐츠가 양방향 스크롤 없이 재배치되어야 합니다.
- 768 CSS px 중간 폭에서 모바일과 데스크톱 사이의 전환이 고아 열·겹친 조작·갑작스러운 정보 누락을 만들지 않아야 합니다.
- 보이는 keyboard focus, 문서 언어·charset·title/h1/main, 이미지 alt, 접근 가능한 이름, 색상 외 상태, 본문 4.5:1 대비, 24×24 CSS px 이상 타깃을 확인합니다.
- hover에 필수 정보나 조작을 숨기지 않습니다.
- 움직임은 상태·공간 관계·필수 주의를 설명할 때만 사용하고 `prefers-reduced-motion`에서 비필수 움직임을 제거합니다.
- `python3 ~/.gemini/config/agy-focus/current/scripts/verify_ui_render.py <HTML> --output-dir <DIR>`로 320px·768px·1280px 렌더, `scrollWidth`, 요소 경계, 문서·접근성 계약, CLS·Long Animation Frames와 실제 모션·reduced-motion emulation을 검사합니다.
