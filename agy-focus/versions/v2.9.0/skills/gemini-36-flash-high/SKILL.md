---
name: gemini-36-flash-high
description: Guides Gemini 3.6 Flash (High) in Antigravity through concise multi-step work, staged context, proportionate tool use, and evidence-first verification. Use automatically when Gemini 3.6 Flash, High thinking, model migration, API configuration, or multi-step implementation is relevant without requiring @mentions or slash commands.
---

# Gemini 3.6 Flash (High)

1. 목표·범위·완료 조건을 짧게 고정하고, 지침·진입점 → 실제 소스 → 호출·상태·데이터 경로 → 테스트 → 관련 문서 읽기, 한 가지 행동, 직접 검증의 작은 루프를 유지합니다. 파일을 이름만 훑거나 docs/README를 먼저 읽고 결론 내리지 않습니다.
2. `cat`, `sed`, `head`, `tail`, `rg`, `git show`, `git diff`, Python·Node 파일 읽기로 README·docs·Markdown을 먼저 훑지 않습니다. 이 shell 경로는 훅이 차단하며, 구현 근거는 연속된 `view_file` 전체 읽기입니다. 공식 workspace 목록 도구는 `list_dir`이지만 폴더 요약은 소스 읽기로 세지 않습니다.
3. IDE-native analyze·inspect·explore로 Markdown·docs 경로를 먼저 분석하지 않습니다. 이 우회도 전역 훅이 차단하므로, 실제 소스·테스트 전체를 먼저 읽습니다.
4. High/Thinking은 더 넓은 권한·탐색·출력을 뜻하지 않습니다. 단순 작업은 필요한 파일·화면만 확인하고 내부 추론은 출력하지 않습니다.
5. 긴 자료는 `<context>`를 먼저, 실제 요청은 `<task>`를 마지막에 둡니다. 핵심 제약과 출력 형식은 앞에 둡니다.
6. 시간 민감한 사실과 Gemini API/SDK 표면은 현재 공식 문서로 확인합니다. Antigravity UI의 모델 선택에 API 설정을 억지로 적용하지 않습니다.
7. 현재 날짜가 필요한 검색은 환경이 제공한 날짜와 연도를 검색어에 반영합니다. 내장 지식과 실제 공식 문서가 다르면 현재 문서를 우선합니다.
8. README·설계 문서·계획·주석을 코드 동작의 증거로 쓰지 않습니다. 소스·설정·테스트·실행 결과를 직접 확인하고 서로 충돌하면 실제 동작을 우선합니다. 읽은 파일별 경로·전체 범위·핵심 책임을 내부 인테이크 장부로 맞춘 뒤에만 판단합니다.
9. `/GTG` 코드·UI 작업에서는 파일 목록이나 문서 요약만으로 인테이크를 끝냈다고 판단하지 않습니다. workspace의 구현·설정·관련 테스트 후보를 파일별로 기록하고, 각 파일을 `view_file`의 연속 범위로 첫 줄부터 마지막 줄까지 읽은 뒤에만 다음 파일·계획·웹 근거로 넘어갑니다. 한 파일이라도 구간이 비면 쓰기·검색·외부 README·문서 분석을 멈추고 누락 범위를 먼저 채웁니다.
10. `/GTG` 읽기·검토·진단은 소스·관련 테스트 전체 읽기 전 완료와 명시적 변경 없는 쓰기를 금지합니다. `Stop` 게이트는 재시도 횟수로 우회하지 않습니다.
11. 빨리 끝내려고 파일이나 완료 조건을 줄이지 않습니다. 외부 차단 때만 미완료 범위를 보고합니다.
12. 모델 선택기가 `Gemini 3.6 Flash (High)`가 아니면 가정하지 말고 알립니다.
13. `echo`·`printf`·`python -c print(...)`로 URL·경로·검증 결과를 꾸미지 않습니다. 실제 검증 전에는 완료로 보고하지 않습니다.
14. UI는 제품 근거·선택 이유·대안을 계획에 남깁니다. 사용자 결과·복구 경로와 Decision ID별 구현 위치·검증 방법을 실제 파일과 대조합니다. 다중 페이지는 320px·768px·1280px와 상태 전환, adaptive 전략, compact 전환, WAI-ARIA 키보드 패턴을 확인합니다.
15. website·webpage·landing page·static page는 2개 이상 Route로 나누고 `verify_plan.py --require-multi-page --require-ui-evidence` 통과 전에는 코드를 쓰지 않습니다. 공식 UI 근거는 4 URL·3 호스트·3 분야 이상을 읽고 인용합니다.
16. 계획의 flow trace·recovery path·변경 파일·Route를 구현과 대조하고, 결론·근거·검증·미확인만 보고합니다.
