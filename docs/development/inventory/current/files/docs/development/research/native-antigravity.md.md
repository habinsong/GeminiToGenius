# `docs/development/research/native-antigravity.md`

- 형식: `100644`
- 바이트: 2525
- SHA-256: `7c09367d8606c1e8cbca2f6d67cecb3eee31ba076df0d618f58a0c06fbab420b`
- 인코딩: `utf-8`

```
# 설치된 Antigravity의 실제 발견 계약

확인일: 2026-09-08. 앱 버전: Antigravity 2.11.0. 프로젝트에 임시로 설치한 뒤 설정 화면만 확인했습니다. 모델 프롬프트를 보내지 않았습니다.

## 관찰

1. 설치 전 프로젝트의 스킬은 16개, 메타데이터는 1,677 토큰으로 표시됐습니다.
2. 플러그인 설치 후 스킬 19개, 2,005 토큰으로 표시됐습니다. 상세 목록에 `gtg-build` 125, `gtg-interface` 116, `gtg-research` 87이 나타났습니다.
3. 처음 생성한 `rules/gtg.md`는 규칙 목록에 포함되지 않았습니다. 규칙은 기존 2개·3,636 토큰 그대로였습니다.
4. 앱이 함께 제공하는 공식 문서에서 `rules/AGENTS.md` 통합 진입점을 확인했습니다. 이 경로로 패키징을 바꾼 뒤 설정을 재조회하자 규칙 3개·4,208 토큰으로 바뀌었습니다.
5. 점검 후 프로젝트 설치를 제거 명령으로 보존 폴더에 옮겼습니다. 전역 프로필·모델·권한 설정을 바꾸지 않았습니다.

이는 실제 파일 발견과 컨텍스트 구성의 증거입니다. 모델이 스킬을 적절히 선택하거나 훅이 모델 실행 중 올바르게 발행됐다는 증거는 아닙니다. 표시된 토큰은 설정의 컨텍스트 크기이며 계정 사용량이 아닙니다.

## 내장 공식 문서

기준 디렉터리는 `~/.gemini/antigravity/builtin/skills/agy-customizations/`입니다. 문서는 읽기만 했으며 아래 SHA-256은 조회 당시 내용입니다.

| 문서 | SHA-256 | 확인한 계약 |
| --- | --- | --- |
| `SKILL.md` | `79c8885e76ce449e82016b37b53dfcc3ff5afefd90a23ea83b24148f41f33fa1` | 발견 위치, 우선순위, 점진적 로딩 |
| `docs/rules.md` | `969a834145a09398b53cd63b7d473d8a915bf80928726650a6d2efc602e33bbe` | AGENTS.md와 GEMINI.md의 디렉터리 범위 적용 |
| `docs/plugins.md` | `481c2612f4729fb4fab600aebc5eb0d4eda6e00d5b45084bc7523718514bf19e` | 플러그인 규칙의 rules/AGENTS.md 권장 배치 |
| `docs/hooks.md` | `6c76fe162f89527b7494213f11fdb268eb508bfca22a7af61f86ced285340bf4` | camelCase, 훅 파일 위치를 기준으로 하는 명령 작업 디렉터리 |

공개 개요와 설치된 버전의 내장 문서 사이에 상세 설명 차이가 있었습니다. [공개 규칙 문서](https://antigravity.google/docs/rules-workflows)와 [플러그인 문서](https://antigravity.google/docs/plugins)를 출발점으로 삼되, 최종 배치는 위 실제 발견 시험으로 확인했습니다.
```
