# `CONTRIBUTING.md`

- 형식: `100644`
- 바이트: 1127
- SHA-256: `4fc141c079d8b9979c2a05cd732670b0b9c65b2fc4c09423b34b621207b898b3`
- 인코딩: `utf-8`

````
# 기여 안내

현재 개발 규칙은 [AGENTS.md](AGENTS.md), 단계별 계획은 [재개발 문서](docs/rebuild/README.md)를 확인합니다.

`gtg/`는 모델과 독립적인 실행 코어, `profile/`은 규칙·스킬의 원본입니다. 설치 사본을 저장소에서 중복 관리하지 않습니다. 모델을 호출하는 평가를 일반 테스트에 추가하지 않습니다.

```bash
bash -n scripts/install.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/catalog.py
python3 scripts/catalog.py --check
```

설치는 실제 사용자 홈 대신 `--home` 또는 `--workspace`로 임시 경로를 지정해 시험합니다. 실패 경로·기존 사용자 파일·복구를 함께 확인합니다. 작업 후 진행 기록·계획·전체 코드 목록을 갱신합니다.

이슈에는 버전, 호스트, 실제 사용한 모델, 명령, 재현 절차, 확인하지 못한 항목을 적습니다. 비밀값·개인 프롬프트·인증 파일은 포함하지 않습니다. 구조 검사·로컬 실행·호스트 동작·모델 품질 검증을 구분해 보고합니다.
````
