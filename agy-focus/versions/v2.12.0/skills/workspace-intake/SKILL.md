---
name: workspace-intake
description: Performs a complete, ordered workspace intake before changing code, configuration, documentation, tests, or UI. Use automatically for 고쳐, 수정, 추가, 만들어, 구현, 변경, 작성, 리팩터링, 삭제, fix, edit, add, build, implement, update, change, write, remove, or refactor without requiring @mentions or slash commands.
---

# 작업 범위 인테이크 및 표준 워크플로 (10. Standard Workflow)

1. **편집 전 집중 검사 (Before editing)**: 변경 전 `git status --short` 및 `rg "target_symbol"`로 작업 상태와 영향 범위를 확인하고 주변 소스 파일을 먼저 읽어 동작을 이해합니다.
2. **풀뷰 소스 인테이크**: 영향 범위의 실제 소스·스크립트 전체 → 호출·데이터·상태 경계의 관련 소스 전체 → 기존 관련 테스트·fixture 전체 → 설정·관련 자산 순서로 읽습니다. 각 텍스트 파일은 `view_file`로 첫 줄부터 끝까지 연속해서 읽습니다.
3. **쉘 우회 및 문서 선행 읽기 금지**: `cat`, `sed`, `head`, `tail`, `rg`, `find`, `ls`, `tree`, `fd`, `git show`, `git diff`, Python·Node로 소스 확인 전 README·docs를 훑지 않습니다. README·문서·주석은 가설일 뿐이며 실제 코드·테스트·실행 결과가 진실 기준입니다.
4. **편집 중 수칙 (During editing)**:
   - 프로젝트 라이선스를 확인하고 웹 검색을 통해 유사 프로젝트/특허/논문/가이드라인 구현과의 유사도 및 안전성을 독립 검증합니다.
   - 가장 작고 일관된 변경만 하며, 새 파일 추가보다 기존 파일 수정을 우선합니다.
   - 주변 코드와 네이밍을 통일하고 주석은 간결하고 유용하게 유지합니다.
   - TODO를 남기지 않으며 플레이스홀더 프로덕션 코드를 추가하지 않습니다.
5. **편집 후 검사 및 직접 검증 (After editing)**:
   - 편집 후 반드시 `git diff --stat` 및 `git diff`로 변경 사항을 검사합니다.
   - 가장 작은 관련 검증을 먼저 실행하고 최종 보고 전 전체 검증을 수행합니다.
   - 확인하지 않은 동작이나 미검증 항목은 성공으로 보고하지 않습니다.

상세 원문: [코딩 표준 및 워크플로](../gtg/references/coding-standards.md)
