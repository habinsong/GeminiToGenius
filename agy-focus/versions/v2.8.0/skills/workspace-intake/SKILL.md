---
name: workspace-intake
description: Performs a complete, ordered workspace intake before changing code, configuration, documentation, tests, or UI. Use automatically for 고쳐, 수정, 추가, 만들어, 구현, 변경, 작성, 리팩터링, 삭제, fix, edit, add, build, implement, update, change, write, remove, or refactor without requiring @mentions or slash commands.
---

# 작업 범위 인테이크

1. 변경 전에 `git status --short`로 작업 상태를 확인하고, 훅이 계산한 영향 범위 후보를 기준으로 실제 파일을 고정합니다. 소스 인테이크 전에는 `find`, `ls`, `tree`, `fd`, `rg --files`, `git ls-files`와 IDE의 workspace/file-tree 탐색을 사용하지 않습니다. 관련 없는 기능·과거 버전·생성물을 컨텍스트에 밀어 넣지 않습니다.
2. 바이너리·캐시·의존성·빌드 산출물·비밀 파일은 제외 이유를 남깁니다. `/GTG` 코드 작업의 영향 범위는 저장소 지침 → 빌드·실행 진입점 → 발견된 실제 소스·스크립트 전체 → 호출·데이터·상태 경계의 관련 소스 전체 → 기존 관련 테스트·fixture 전체 → 설정·관련 자산 → 문서 → README·계획·변경 기록 순서로 읽습니다. 코드 작업에서 README·docs를 먼저 열어 현재 동작을 결론 내리지 않습니다.
3. 각 관련 텍스트 파일은 `view_file`로 처음부터 끝까지 읽습니다. 긴 파일은 여러 구간으로 나눠도 되지만 첫 줄부터 마지막 줄까지 겹치거나 이어지게 읽고 중간 줄을 생략하지 않습니다. `rg`, 파일명 목록, 일부 줄, 검색 결과, 요약은 전체 읽기의 대체물이 아닙니다.
4. `cat`, `sed`, `head`, `tail`, `rg`, `find`, `ls`, `tree`, `fd`, `git show`, `git diff`, `git ls-files`, Python·Node로 README·docs·Markdown이나 workspace 목록을 먼저 읽는 shell 우회는 사용하지 않습니다. 소스 전체 읽기와 관련 테스트 확인 뒤에만 문서를 대조합니다.
5. README·문서·주석의 설명은 가설로 취급합니다. 실제 코드·설정·테스트·실행 결과와 대조하기 전에는 현재 동작이나 완료 상태로 확정하지 않습니다.
6. 소스의 호출 흐름·상태 소유자·입출력·부작용·검증 경로를 따라갑니다. 이름이 비슷하다는 이유로 관련성을 추측하거나 구현 파일을 건너뛰지 않습니다.
7. 영향 범위를 모두 읽은 뒤에도 모르는 데이터 흐름·사용자 상태·검증 경로가 있으면 수정 전에 한 단계씩 범위를 넓힙니다. 처음부터 무관한 저장소 전체를 주입하지 않습니다.
8. 그 다음에 한 가지 변경을 하고 실제 성공 결과가 있는 가장 작은 직접 검증을 실행합니다. 읽지 않은 범위나 확인하지 않은 동작이 남으면 완료라고 쓰지 않습니다.
