# `docs/development/README.md`

- 형식: `100644`
- 바이트: 3053
- SHA-256: `ca99ff6b9bf61d394112469ba858dafd8dd05b63630be1a1245c0fa12e868de6`
- 인코딩: `utf-8`

````
# GeminiToGenius 재개발 기록

기준일: 2026-09-08. 기존 기준 커밋: `5cd1c5a5ca98a06fd8640ce35398ab0552341c04` (`v2.15.0`).

목표는 Gemini가 자연어 요청 하나로 조사·구현·검증·복구를 수행하는 하네스입니다. 기존 코드의 연장은 의무가 아닙니다. 실제 효과가 없는 규칙, 깨진 검증 경로, 중복 배포 사본은 검증 가능한 대체 구현으로 교체합니다.

현재 상태는 [진행 기록](status.md), 순서와 완료 기준은 [개발 계획](plan/roadmap.md)에 기록합니다.

컨텍스트 압축 뒤와 자동 목표 재개 시에는 [현재 작업과 재개 기준](current-work.md)을 먼저 읽습니다. 마지막 요약만 믿지 않고 실제 파일·실행·화면을 확인한 뒤 이어갑니다.

[전체 완료 점검](plan/completion-audit.md)은 원래 요구와 현재 증거를 대조합니다. 미완료 항목은 통과한 로컬 검사의 개수로 대체하지 않습니다.

- [기존 구현 조사](inventory/architecture.md): 현재 실행 경로와 재현한 결함입니다.
- [기준 원본 전체](inventory/baseline/README.md): 수정 전 113개 추적 경로의 파일별 전체 코드·내용입니다.
- [현재 전체](inventory/current/README.md): 최신 파일별 코드·내용입니다. `python3 scripts/catalog.py`로 갱신합니다.
- [아키텍처](plan/architecture.md): 실행 상태·증거·플랫폼 경계입니다.
- [검증 계획](plan/verification.md): 로컬 회귀, 플랫폼 호환성, 실제 품질 비교의 기준입니다.
- [조사 원장](research/sources.json): 확인한 공식 문서·논문·오픈소스와 적용 판단입니다.
- [플랫폼 계약](research/platform-contracts.md): Antigravity와 Gemini CLI의 구체적인 차이입니다.
- [선택 및 폐기](research/decisions.md): 근거가 구현에 미치는 영향입니다.

## 기록 방식

기준 원본은 변경하지 않습니다. 현재 목록은 Git 추적 파일과 무시되지 않은 신규 파일을 모두 수집하며, 텍스트는 전체 코드 블록, 바이너리는 Base64, 심볼릭 링크는 대상 문자열로 남깁니다. 경로·바이트·SHA-256·줄 수·Python 선언 위치를 함께 기록합니다.

Git 내부 데이터, 이 목록 자체의 재귀 복제, ignored 파일의 내용, 민감 경로는 제외 사유를 명시합니다. ignored 파일명은 로컬 조사에 기록하며 환경별로 달라지는 캐시를 배포 코드와 비교하지 않습니다. 문서화 범위의 완전성은 모델이 모든 파일을 매번 읽었다는 주장과 다릅니다.

```bash
python3 scripts/catalog.py
python3 scripts/catalog.py --check
python3 scripts/catalog.py --baseline 5cd1c5a5ca98a06fd8640ce35398ab0552341c04 --check
```

실제 Gemini·Antigravity 사용은 꼭 필요한 호환성 확인에 한정합니다. 로컬 재현·계약 테스트·공개 자료 조사를 기본으로 하며, 실모델 품질과 경쟁 제품 우월성은 동일 조건 평가 전까지 미검증으로 표시합니다.
````
