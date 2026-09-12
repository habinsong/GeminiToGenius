# `docs/development/README.md`

- 형식: `100644`
- 바이트: 3438
- SHA-256: `3e49dbb7794a00dad297d28c76746505f3c2790c70be1bb8d21050031146dd1e`
- 인코딩: `utf-8`

````
# GeminiToGenius 재개발 기록

기준일: 2026-09-08. 기준 커밋: `5cd1c5a5ca98a06fd8640ce35398ab0552341c04` (`v2.15.0`).

이 프로젝트의 목표는 Gemini가 단일 자연어 요청만으로 탐색, 구현, 검증, 복구 수명주기를 완결할 수 있도록 지원하는 신뢰성 하네스를 구축하는 것입니다. 과거 구현에 얽매이지 않고, 실질적 검증 효과가 없는 규칙, 결함이 있는 검증 경로, 중복된 배포 사본을 검증 가능한 구조로 전면 개편했습니다.

현재 상태는 [진행 기록](status.md), 단계별 일정과 완료 기준은 [개발 계획](plan/roadmap.md)에 지속적으로 갱신합니다.

컨텍스트 압축 후 또는 세션 자동 재개 시에는 [현재 작업과 재개 기준](current-work.md)을 가장 먼저 검토합니다. 직전 요약문에만 의존하지 않고 실제 파일 변경 사항, 실행 프로세스, 터미널 출력을 교차 확인한 뒤 작업을 재개합니다.

[전체 완료 점검](plan/completion-audit.md) 문서는 원 요구사항과 실제 확보된 검증 증거를 대조합니다. 미완료 항목을 단순히 통과한 단위 테스트 개수로 합리화하지 않습니다.

- [기존 구현 조사](inventory/architecture.md): 과거 실행 경로와 실제 재현된 결함 내역
- [기준 원본 전체](inventory/baseline/README.md): 재개발 착수 전 113개 경로의 파일별 전체 원본 아카이브
- [현재 전체](inventory/current/README.md): 최신 파일별 소스 및 무결성 카탈로그 (`python3 scripts/catalog.py`로 갱신)
- [아키텍처 설계](plan/architecture.md): 상태 저장소, 검증 증명서, 플랫폼 경계 설계
- [검증 계획](plan/verification.md): 로컬 회귀 테스트, 플랫폼 계약 호환성, 하네스 비교 기준
- [연구 원장](research/sources.json): 검토한 공식 기술 문서, 연구 논문, 오픈소스 프로젝트 및 적용 판단 근거
- [플랫폼 계약 분석](research/platform-contracts.md): Antigravity와 Gemini CLI의 세부 런타임 차이점
- [기술적 의사결정](research/decisions.md): 기술 스택 선택 및 폐기 결정의 배경과 근거

## 카탈로그 기록 방식

기준 원본 아카이브는 절대 변경하지 않습니다. 현재 인벤토리 목록은 Git 추적 파일과 신규 미추적 파일을 모두 수집하며, 텍스트는 전체 코드 블록, 바이너리는 Base64, 심볼릭 링크는 링크 대상 문자열로 보존합니다. 각 파일의 경로, 바이트 크기, SHA-256 해시, 줄 수, Python 심볼 선언 위치를 투명하게 기록합니다.

Git 내부 파일(`.git`), 인벤토리 자체의 순환 복제본, `.gitignore` 대상 파일, 비밀 정보 경로는 제외 사유를 명시하여 격리합니다. 문서화 범위의 완전성은 모델이 모든 파일을 항상 읽었다는 주장과 구분해야 합니다.

```bash
python3 scripts/catalog.py
python3 scripts/catalog.py --check
python3 scripts/catalog.py --baseline 5cd1c5a5ca98a06fd8640ce35398ab0552341c04 --check
```

실제 Gemini 및 Antigravity API 호출은 반드시 필요한 호환성 실증에 한정합니다. 로컬 단위 테스트, 계약 테스트, 공개 자료 조사를 주된 개발 근거로 삼으며, 동일 조건 하의 실측 비교가 이루어지기 전까지는 모델 품질이나 타 제품 대비 우월성을 임의로 주장하지 않습니다.

````
