# 04 컨텍스트 예산

- IDE 디렉터리 요약이나 파일 트리 탐색 결과는 소스 인테이크로 인정되지 않으며, `view_file`로 실제 파일의 첫 줄부터 마지막 줄까지 틈 없이 읽어야 합니다.
- `/GTG` 변경 작업은 영향 범위의 실제 소스와 관련 테스트를 끝까지 읽은 뒤, README·docs·계획서는 마지막에 대조합니다. 문서를 먼저 읽고 현재 동작을 단정하지 않습니다.
- `cat`, `sed`, `head`, `tail`, `rg`, `find`, `git show`, `git diff`, Python/Node 쉘 명령으로 소스 확인 전 문서를 먼저 훑는 우회는 차단됩니다.
- `/GTG` UI 구현은 소스·테스트 확인 후 `docs/plans/design-plan.md`, `implementation-plan.md`, `verification-plan.md`를 먼저 작성합니다.
- 검색·요약·주석은 구현 증거가 아니며, 실제 코드·설정·테스트 실행 결과를 우선합니다.
- 외부 저장소 설명 시 GitHub 소스를 직접 교차 확인하며, 출력 전용 명령(`echo`, `printf`)으로 증거를 날조하지 않습니다.
