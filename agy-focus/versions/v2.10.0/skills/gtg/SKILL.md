---
name: gtg
description: Activates the GeminiToGenius strict execution harness for complete code inspection, persistent implementation, anti-AI-Slop UI, human product copy, and rendered verification. Invoke explicitly with /GTG for coding, debugging, refactoring, UI, UX, website, app, or multi-file tasks where shallow completion is unacceptable.
---

# GTG

`/GTG`가 선택되면 이 계약을 현재 작업의 완료 시점까지 유지합니다. 첫 계획이나 첫 생성물을 결과로 취급하지 않습니다.

## 실행 계약

1. 사용자 목표·허용 범위·완료 조건을 각각 한 문장으로 고정합니다. 현재 workspace와 사용자 변경을 먼저 확인합니다.
2. 변경 작업은 전체 파일 지도를 만든 뒤 저장소 지침과 빌드·실행 진입점을 확인합니다. README·docs·계획·변경 기록은 발견된 영향 범위의 실제 소스와 기존 관련 테스트를 모두 끝까지 읽은 뒤 대조합니다. 문서부터 읽고 현재 동작을 결론 내리지 않습니다. IDE의 `list_dir` 결과나 파일명 목록을 읽은 것으로 보고하지 않습니다.
3. 영향 범위의 파일은 `view_file` 구간이 서로 이어지도록 처음부터 마지막 줄까지 읽습니다. 파일명, `rg`, 일부 줄, 검색 결과, 문서 요약은 전체 읽기의 대체물이 아닙니다. 읽지 않은 파일을 읽었다고 쓰지 않습니다.
4. `cat`, `sed`, `head`, `tail`, `rg`, `git show`, `git diff`, Python·Node 파일 읽기로 README·docs·Markdown을 먼저 훑지 않습니다. 소스 확인 전 shell 문서 읽기는 훅이 차단하며, 마지막 변경 뒤에는 실제 성공 결과가 있는 검증 명령이 필요합니다.
5. IDE-native analyze·inspect·explore로 README·docs를 먼저 분석하지 않습니다. 이 경로도 전역 훅이 차단하며, 실제 소스·테스트 전체 읽기가 우선입니다.
6. 실제 호출·데이터·상태·IO·오류 경계를 따라 관련 파일을 넓힙니다. 이름만 보고 동작을 추측하지 않습니다. 발견된 기존 관련 테스트는 모두 끝까지 읽습니다. 문서와 코드가 다르면 실행 가능한 코드와 테스트를 기준으로 합니다.
7. 가장 작은 일관된 변경만 합니다. 기능을 기존 대형 객체에 누적하지 않고 UI 상태·도메인 정책·IO·영속성·외부 프로세스·표현의 변경 이유가 갈리면 가장 작은 응집 단위로 분리합니다. wrapper와 빈 계층으로 줄 수만 옮기지 않습니다.
8. UI·웹 구현이면 실제 소스·테스트를 읽은 뒤 `docs/plans/design-plan.md`, `implementation-plan.md`, `verification-plan.md`를 먼저 작성하고 `verify_plan.py --require-multi-page --require-ui-evidence`를 통과시킵니다. 계획에는 adaptive reflow/reveal/presentation, compact 전환 조건, 키보드 패턴, evidence matrix의 결정·근거 발견·구현 영향·검증 게이트·버린 대안을 넣습니다. website·webpage·landing page·repository site·static page는 흐름 수와 상관없이 `Route:`를 둘 이상 계획하고 다중 페이지로 만듭니다. 진짜 단일 화면 앱만 예외이며, 그 이유와 상태 계약을 적습니다.
9. 실패를 재현하고 한 가설씩 수정·검증합니다. 쓴 파일은 마지막 쓰기 뒤 현재 내용을 다시 끝까지 읽고, 그 뒤 실제 성공 결과가 있는 테스트·빌드·lint·typecheck·실행·화면 검증을 수행합니다. 확인하지 않았으면 성공으로 쓰지 않습니다. 빨리 끝내기 위해 완료 조건을 줄이지 않습니다.
10. 최신·공식 사실은 현재 날짜로 검색하고 1차 출처 본문을 읽습니다. UI 작업은 공식 URL 4개 이상·서로 다른 호스트 3개 이상·플랫폼/접근성/성능/HCI 분야 3개 이상을 대조하고 계획의 evidence matrix에 결정·근거 발견·구현 영향·검증 방법을 남깁니다. MCP·플러그인은 연결 자체가 작업 목적일 때만 사용합니다.
11. 최종 답변은 핵심 원인, 변경 내용, 실제 검증, 남은 리스크만 한국어 존댓말로 짧게 씁니다. 내부 추론·AI 자기소개·분위기 문단은 쓰지 않습니다.

## UI·UX 작업

UI, UX, 웹페이지, 앱 화면, CSS, 카피 작업이면 코드를 쓰기 전에 [UI 품질 계약](references/ui-quality.md)을 끝까지 읽고 적용합니다. 실제 제품 소스에서 사용자·기능·수치·제약·용어를 수집한 뒤 콘텐츠와 위계를 정합니다. 외부 `owner/repository`를 설명하는 페이지면 검색 결과를 근거로 쓰지 않습니다. 현재 workspace가 해당 저장소가 아니면 GitHub 원문에서 README, 설치 스크립트, manifest 또는 실제 소스를 직접 읽고 수치·명령·버전을 교차 확인한 뒤 씁니다.

AI SaaS 템플릿을 피했다는 이유로 GitHub/Vercel풍 다크 문서, 검은 배경+시안 포인트+모노스페이스 terminal 미학, 네오 브루탈리즘, 긴 규칙 표, 스킬 카탈로그를 자동 선택하지 않습니다. 이를 Tailwind Slate 라이트 팔레트, 중앙 max-width 문서 틀, 동일한 배경·테두리·패딩 상자 반복으로 바꾸지도 않습니다. “clean modern developer aesthetic”는 디자인 근거가 아닙니다. 정적 설명 페이지에는 요청하지 않은 scroll spy·복사 버튼·필터·애니메이션 JavaScript를 추가하지 않습니다. 제품의 한 문장 정의, 실제 설치, 동작 증거, 한계가 먼저 보이게 하고 세부 목록은 필요할 때만 둡니다.

구현 뒤 `python3 ~/.gemini/config/agy-focus/current/scripts/verify_ui_render.py <HTML> --output-dir <DIR>`를 실행합니다. 이 명령은 별도 패키지 설치 없이 현재 설치된 Chrome으로 320px·768px·1280px 스크린샷과 수평 overflow를 함께 검사합니다. `ok: true`를 확인하고 모든 이미지 파일을 직접 엽니다. 그 다음 Computer Use 또는 vision으로 각 Route·상태를 실제 화면에서 관찰·조작하고, 관찰 뒤 `search_web`와 공식 UI URL의 `read_url_content`를 실행해 화면 판단을 외부 기준과 대조합니다. HTTP 200, HTML 파서, `curl`, 소스 검토는 화면 검증으로 세지 않습니다. 키보드 focus, 긴 콘텐츠, loading·empty·error·success·disabled·selected 상태, 감속 설정을 해당 화면에 존재하는 범위에서 조작합니다. 첫 렌더를 그대로 통과시키지 않습니다.
