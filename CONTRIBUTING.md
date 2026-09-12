# 기여 안내

개발 규칙은 [AGENTS.md](AGENTS.md), 단계별 계획과 설계는 [개발 문서](docs/development/README.md)를 참고하세요.

`gtg/`는 모델 독립적인 실행 코어이며, `profile/`은 배포용 규칙과 스킬 원본입니다. 설치된 사본을 저장소에 중복 커밋하지 않으며, 외부 모델 API를 직접 호출하는 평가는 일반 단위 테스트에 포함하지 않습니다.

```bash
bash -n scripts/install.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/catalog.py
python3 scripts/catalog.py --check
```

설치기 검증 시에는 실제 사용자 홈 디렉터리 대신 `--home` 또는 `--workspace` 옵션으로 격리된 임시 경로를 지정해야 합니다. 예외 발생 경로, 기존 사용자 설정 보존, 복구(`restore`) 동작을 반드시 함께 검증하세요. 작업 완료 후에는 진행 기록, 계획 문서, 코드 카탈로그를 갱신합니다.

버그 리포트 작성 시 버전, 대상 호스트, 실제 사용한 모델, 실행 명령, 최소 재현 절차, 미확인 범위를 명시해 주세요. API 키, 개인 프롬프트, 인증 토큰은 일체 포함하지 마세요. 구조 검사 통과, 로컬 실행 결과, 호스트 연동 여부, 모델 품질 검증을 분리하여 보고해야 합니다.

