# `docs/rebuild/validation/2026-09-08-ide/README.md`

- 형식: `100644`
- 바이트: 1681
- SHA-256: `b2b15aa1ef7fd04f93d9c8573120c704fdcf1be18cad30948c652978e9a42119`
- 인코딩: `utf-8`

```
# Antigravity IDE 발견 확인

2026-09-08, 설치된 Antigravity IDE 2.5.5에서 새 임시 작업공간만 열어 확인했습니다. 모델에게 프롬프트를 보내지 않았습니다. [직접 관찰 기록과 설치·제거 결과](observation.json).

- Customization의 규칙 화면에 `GeminiToGenius` 본문과 `Project · AGENTS.md`가 표시됐습니다.
- 입력창의 스킬 선택 목록에 `gtg-build`, `gtg-interface`, `gtg-research`와 각 설명이 표시됐습니다.
- 목록 확인에 사용한 `/`는 전송하지 않고 지웠습니다. 입력을 지운 뒤 전송 버튼의 비활성 상태를 확인하고 검증 창만 닫았습니다.
- 제거 명령은 임시 플러그인을 보존 폴더로 옮겼습니다. 활성 설치 경로가 사라지고 보존 경로가 존재하는 것을 다시 확인했습니다.

임시 작업공간 자체에 대한 신뢰만 허용했습니다. 상위 임시 폴더 전체의 신뢰는 선택하지 않았습니다. 해당 작업공간의 신뢰 기록은 IDE에 남아 있을 수 있습니다. 기존 프로젝트 파일과 모델 선택은 바꾸지 않았습니다.

이는 IDE가 규칙과 스킬을 발견한다는 증거입니다. IDE에서 모델이 슬래시 없는 요청에 스킬을 자동 선택하거나 실제 실행 중 훅을 발행한 증거는 아닙니다. 설치기가 직접 실행한 훅 검사와 호스트의 훅 발행도 구분합니다.

공개 [IDE 플러그인 문서](https://antigravity.google/docs/ide/plugins)의 구성·탐색 경로와 [공식 Codelab](https://codelabs.developers.google.com/getting-started-agy-ide)의 Customizations·목록 진입 경로를 대조했습니다.
```
