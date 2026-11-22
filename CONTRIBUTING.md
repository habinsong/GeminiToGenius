# 기여 안내

개발 규칙은 [AGENTS.md](AGENTS.md)를, 단계별 계획과 설계는 [개발 문서](docs/development/README.md)를 참고해 주십시오.

`gtg/`는 특정 모델에 종속되지 않는 실행 코어이며, `profile/`은 배포용 규칙과 스킬 원본입니다. 설치된 사본은 커밋 대상에서 제외하고, 외부 모델 API를 직접 부르는 평가는 단위 테스트에 넣지 않습니다.

```bash
bash -n scripts/install.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/catalog.py
python3 scripts/catalog.py --check
```

설치기를 검증하실 때는 실제 사용자 홈 디렉터리 대신 `--home` 또는 `--workspace` 옵션으로 격리된 임시 경로를 지정하십시오. 예외 경로와 기존 설정 보존과 복구(`restore`) 동작을 함께 검증해야 합니다. 작업 후에는 진행 기록과 계획 문서, 코드 카탈로그를 갱신합니다.

버그를 보고하실 때는 버전, 대상 호스트, 모델, 실행 명령과 함께 문제를 다시 일으키는 최소 절차를 명시해 주십시오. API 키와 개인 프롬프트와 인증 토큰은 포함하지 마십시오. 구조 검사 통과 여부와 로컬 실행 결과와 호스트 연동 여부를 나누어 보고해야 합니다.
