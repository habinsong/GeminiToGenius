---
name: workspace-intake
description: Performs a complete, ordered workspace intake before changing code, configuration, documentation, tests, or UI. Use automatically for 고쳐, 수정, 추가, 만들어, 구현, 변경, 작성, 리팩터링, 삭제, fix, edit, add, build, implement, update, change, write, remove, or refactor without requiring @mentions or slash commands.
---

# 작업 범위 인테이크

1. 변경 전에 활성 workspace의 범위를 고정합니다. git 저장소면 `git status --short` 뒤 `git ls-files -co --exclude-standard` 목록을 사용합니다. git이 아니면 파일 목록을 경로순으로 만듭니다.
2. 바이너리·캐시·의존성·빌드 산출물·비밀 파일은 제외 이유를 확인합니다. 나머지 텍스트 파일은 경로순으로 `view_file`로 처음부터 끝까지 하나씩 읽습니다.
3. `rg`, 파일명 검색, 일부 줄 읽기, 요약은 전체 파일을 읽은 대체물이 아닙니다. 검색은 위치를 찾는 데만 씁니다.
4. 기존 문서·설정·엔트리포인트·소스·테스트·관련 자산을 모두 읽은 뒤에만 변경 범위와 기존 규칙을 확정합니다.
5. 목록을 다 읽은 뒤에도 모르는 데이터 흐름·사용자 상태·검증 경로가 있으면 수정 전에 추가로 확인합니다.
6. 그 다음에 한 가지 변경을 하고 가장 작은 직접 검증을 실행합니다. 읽지 않은 파일이 남으면 완료라고 쓰지 않습니다.
