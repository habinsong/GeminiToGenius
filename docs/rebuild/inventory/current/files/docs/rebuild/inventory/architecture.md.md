# `docs/rebuild/inventory/architecture.md`

- 형식: `100644`
- 바이트: 3144
- SHA-256: `9be3d55af527f55873e0d9085f1a406dcd2f9cb40a2bf8eeb9105352e167b5f6`
- 인코딩: `utf-8`

```
# 기존 구현과 재현 결과

조사일: 2026-09-08. 시작 시 작업 트리는 깨끗했습니다.

로컬 ignored 경로 관찰: `.DS_Store`. 내용은 운영체제 메타데이터이므로 읽지 않았습니다. 생성 코드 목록 자체와 `.git/` 내부는 재귀 순회하지 않습니다.

| 영역 | 실제 파일과 책임 | 재개발 판단 |
| --- | --- | --- |
| 배포 진입 | `scripts/install.sh`가 checkout 업데이트, 전역 프로필 이동, 링크 설치, 검증을 순차 실행 | 검증 실패 시 자동 복구가 없어 교체 대상 |
| 활성 프로필 | `agy-focus/current` → `versions/v2.15.0` | 새 배포 전환 시 제거, 기준 원본은 보존 |
| 규칙 | 12개 `rules/*.md`를 `assemble_gemini.py`가 전역 `GEMINI.md`로 결합 | 반복 지시·고정 파일 크기·무조건 다중 페이지·전체 파일 강제 읽기 제거 대상 |
| 훅 | 활성 `hooks/hooks.json`은 `{}` | 새 실행 계층 필요 |
| 설치 사본 | `installed/hooks.json`에는 14개 훅이 있으나 `installed/hooks/hooks.json`은 `{}` | 배포 진실의 중복 제거 대상 |
| 실행 파일 | README의 `hook_runner.py`, `test_hook_runner.py`가 없음 | 존재하지 않는 기능 주장 제거 대상 |
| 스킬 | 11개 스킬과 UI·엔지니어링 참고 문서 | 명확한 작업별 선택과 실험으로 재선정 |
| 검증기 | 프로필 구조, 계획, 다중 페이지, Chrome 렌더·모션 분석 | 문자열·개수 검증과 실제 실행 검증을 분리 |
| 버전 관리 | `sync_version.py`가 현재 프로필 복제와 다른 버전 폴더 삭제 수행 | 재현 가능한 단일 원본 패키징으로 교체 대상 |
| 웹 문서 | 정적 HTML/CSS/JS 및 다국어 README | 제품 구현 확정 후 생성 데이터에 맞춰 갱신 |
| CI | Ubuntu 임시 홈에 설치하고 `verify_profile.py` 실행 | 실제 명령 실행·실패 주입·자료 최신화 검사 추가 |

## 재현한 결함

1. 임시 홈에서 `AGY_INSTALL_HOME=<임시 경로> bash scripts/install.sh --skip-update` 실행: 종료 코드 0, `ok: true`, `hooks: 0`. README는 훅 14개와 훅 검증 완료를 안내하므로 배포된 동작과 불일치합니다. 실제 사용자 홈은 건드리지 않았습니다.
2. `python3 agy-focus/current/scripts/verify_plan.py --help` 실행: 종료 코드 1, `ModuleNotFoundError: No module named 'hooklib'`. `verify_profile.py`의 `ast.parse`는 이 실행 오류를 검출하지 못합니다.
3. `MANIFEST.json`은 훅 개수를 0으로 선언하고, 검증기 역시 0을 기대합니다. 따라서 누락은 기존 테스트에서 실패하지 않습니다.

## 파일별 목록

[기준 manifest](baseline/manifest.json)는 113개 경로를 빠짐없이 나열하고, 모든 원문으로 연결합니다. Python 함수·클래스의 시작과 끝 줄도 기록합니다. 동일 코드가 여러 배포 경로에 존재해도 각 경로를 별도로 기록했습니다.

계획 검증기의 실패를 확인했으며 UI 렌더 도구의 전체 동작을 검증한 것은 아닙니다. 후속 교체 전 개별 호출과 실제 렌더를 별도로 확인합니다.
```
