# 설계

## 1. 요약

AI 냄새 측정기는 글에서 AI가 쓴 것처럼 읽히는 표현을 찾아 0~100점으로 알려 주는 도구입니다. 찾은 표현 중 안전하게 바꿀 수 있는 것은 직접 바꾸고, 나머지는 어떻게 고칠지 적은 지시문을 만들어 AI 에이전트에게 맡깁니다.

엔진은 **측정기 + 기계적 교정기**이고, 구조적 재작성은 에이전트(LLM)가 합니다. 엔진이 LLM을 호출하지 않기에 네트워크도 키도 필요 없습니다.

## 2. 모듈 (책임별, 파일당 500줄 이하)

| 파일 | 책임 | 할 수 없는 것 |
|---|---|---|
| `model.py` | 자료형(Rule, Finding, Edit, Analysis), 범주표, 가중치 함수 | 다른 모듈 import |
| `textutil.py` | 입력 읽기, 보호 구간(코드, URL, 인용 블록, 무시 표지), 문장, 문단 나누기, 단위 세기 | 규칙 |
| `rules/*.py` | 규칙 데이터. `R(...)` 한 줄이 규칙 하나. 언어, 범주별 파일 | 로직 |
| `fixers.py` | 규칙이 가리키는 교정 함수(repl)와 조건 함수(guard) | 탐지 |
| `analyzers.py` | 정규식으로 못 잡는 빈도, 연속 특성(접속어 쌓임, 3항 나열 및 과다, 같은 어미, 대시, 감정 겹침, 한 문단 안의 말투 혼용, 느낌표 과다, 균일 문단 호흡) | 점수 |
| `cohesion.py` | 문장 사이 이음. 끊긴 단문의 연속과 이음 없는 문단을 찾습니다. 이음의 증거는 문두 접속어, 지시어, 앞 문장 끝말의 되받음입니다. 이음 현황(`metrics.cohesion`)도 만듭니다 | 점수 |
| `habits.py` | 영문 병기, 제목형 콜론, 접속부사, 연결어미 뒤 쉼표, 동의어 돌려쓰기, 문장 길이 대역, 부호 평탄, 제목 되풀이, 문서 전체 말투 혼용. 문서 단위 특징은 길이 0인 구간에 둡니다 | 점수 |
| `guards.py` | 윤문본에 늘어난 지어낸 관점, 중요성, 반론, 솔직함, 극적 장치 표지(`verify`가 씁니다) | 교정 |
| `voice.py` | 필자 표본을 수치로 요약(`voice` 명령, `prompt --voice`). 점수에 넣지 않습니다 | 점수 |
| `linkers.py` | 10개 언어 접속부사, 접속사, 종속접속사, 순서어, 지시어 사전(관계: 추가, 대조, 인과, 시간, 환언), 문단 언어 판별, 언어별 문장 길이 기준, 이어지는 말 목록 | 탐지 |
| `detect.py` | 규칙 실행, min_count, cluster 걸러내기, 겹침 정리, `Analysis` 조립 | 교정 적용 |
| `score.py` | 검출 항목 -> 점수. 문단별 점수 | 탐지 |
| `fix.py` | 교정안 수집, 겹침 정리, 적용, 공백 정리 | 탐지 |
| `verify.py` | 원문과 윤문본 대조 | 교정 |
| `prompt.py` | LLM 윤문 프롬프트, 채팅용 프롬프트 | 실행 |
| `report.py`, `i18n.py` | 사람이 읽는 출력과 JSON | 계산 |
| `cli.py` | 명령줄 | 로직 |
| `installer.py` | 스킬, 에이전트 설치, 설치본 확인, doctor | 윤문 |
| `selftest.py`, `samples.py` | 설치 확인용 내장 시험과 표본 | |
| `tools/evaluate.py`, `tools/build_corpus.py`, `tools/build_recent.py` | 라벨 붙은 공개된 자료로 특징별 사람이 쓴 글 오탐지, AI가 쓴 글 검출 비율을 구한다(저장소 밖 도구, `docs/evaluation.md`) | |

의존 방향은 `model <- textutil <- rules/fixers <- analyzers/detect <- score/fix/verify <- report/prompt <- cli`로 한쪽입니다.

## 3. 점수

```
가중치 w = (규칙 가중치 또는 범주 기본값) x 근거 계수(A 1.0, B 0.75, C 0.45) x 장르 계수
D   = 합( min(범주 상한, 100 x 범주 가중합 / max(단위 수, 60)) )     # 출현 빈도 범주
R   = 합(챗봇 잔재류 가중합)                                         # 건수 범주: 잔재, 아첨, 마크업, 자리표시자
S_d = 100 x (1 - exp(-D / 5)),  S_r = 100 x (1 - exp(-R / 2.2))
점수 = 100 - (100 - S_d)(100 - S_r) / 100
```

- 한 규칙이 한 문서에서 낼 수 있는 가중합은 그 규칙 최대 가중치의 4배까지입니다.
- 겹치는 항목은 가장 가중치가 큰 하나만 반영합니다(shadowing). 가려진 항목의 교정안은 살아 있습니다.
- `min_count`: 문서 전체에서 이 횟수 이상 나올 때만 반영합니다(번역투). `cluster`: 400자 안에 다른 군집 규칙이 이만큼 더 있어야 반영합니다(흔한 낱말).
- 구간: 8 미만 거의 없음, 10 미만 약함, 20 미만 높음, 35 미만 SLOP, 55 미만 쓰레기, 80 미만 디지털 쓰레기, 그 이상 핵폐기물. 이름은 참고용입니다. 10점대도 높은 점수로 봅니다.
- 가중치 0인 규칙(`~를 통해`, `~것이다`)은 점수에 안 넣고 '참고'로만 표시됩니다.
- 문장 길이 변동(burstiness)은 `metrics`에만 두고 점수에 넣지 않습니다(약한 지표). 대신 **짧은 문장이 이음 없이 이어지는 것**은 `cohesion` 범주(상한 4.0)로 반영합니다. 접속어를 지우고 문장을 쪼개면 점수가 내려가는 방향의 쏠림을 막기 위해서입니다.
- 연결 단절 검출은 다른 특징을 가리지도 가려지지도 않는다(`_shadow`에서 제외). 첫 문장에 붙여 둔 위치일 뿐 문장 사이의 성질이기 때문입니다.
- 접속어 쌓임(`transition.stack`)은 C등급입니다. 자동 삭제는 더하기 접속어(또한, Moreover)이면서 지운 뒤에도 지시어나 되받음으로 이어질 때만 합니다.

## 4. 규칙 쓰는 법

```python
R("en.structure.copula", "en", "structure", "B",     # id, 언어, 범주, 근거 등급
  r"\b(?P<v>serves|stands)\s+as\s+(?P<art>an?|the)\b",   # 정규식 (영어는 대소문자 무시)
  "Fancy verb where 'is' works.",                    # 설명 (규칙의 언어로)
  tier="strong", repl=fx.copula,                     # 자동 교정 단계와 교정 함수(또는 치환 틀)
  w=0.6, genre={"academic": 0.5}, min_count=2, cluster=1,
  guard=..., fix_guard=..., scope="sentence", recap=True)
```

- 새 규칙은 `rules/` 해당 파일에 한 줄 추가하고 `tests/test_rules.py`에 맞는 문장과 안 맞는 문장을 하나씩 넣습니다.
- `scope="sentence"`는 매치가 든 문장을 통째로 지웁니다(문장 첫머리에서 시작할 때만).
- `guard`가 False면 검출하지 않고, `fix_guard`가 False면 검출하되 고치지 않습니다.
- 작성자 금지어는 규칙 파일을 고치지 않고 `--ban`, `--ban-file`로 넘깁니다.
- `python3 scripts/ai-smell rules --format md > docs/rules.md`로 목록 문서를 다시 만듭니다.

## 5. 교정 단계

| 단계 | 내용 | 의미 보존 |
|---|---|---|
| safe | 누출 토큰, 보이지 않는 문자, 줄바꿈 없는 공백 | 보존 |
| standard | 잔재, 예고, 공치사 삭제, 장황한 구절 단순화, 이중 피동, 명사+진행 동사 단순화, 불필요한 유보 삭제 | 거의 보존 |
| strong | 부정 대구의 앞 절, 분사 꼬리, 낱말 교체, 대시, 강조어 정리, 접속어 덜기, '~라고 할 수 있다' 단정 | 달라질 수 있음 |

모든 교정은 **삭제 또는 같은 뜻의 단순화**다. 새 낱말을 덧붙이는 교정은 `copula`(is), `word_map`(use, because 같은 평이한 대응어)뿐입니다. 코드, URL, 인용 블록, 무시 구간 안은 고치지 않습니다. 교정 뒤 글이 통째로 사라지면 원문을 돌려줍니다.

## 6. 설치 경로와 불확실성

| 대상 | 사용자 범위 | 프로젝트 범위 | 비고 |
|---|---|---|---|
| Claude Code 스킬 | `~/.claude/skills/ai-smell-polish` | `.claude/skills/ai-smell-polish` | |
| Claude Code 서브에이전트 | `~/.claude/agents/ai-smell-polisher.md` | `.claude/agents/...` | 시작 시 읽으므로 재시작 또는 `/agents` |
| 공통(Codex, Gemini CLI 등) | `~/.agents/skills/...` | `.agents/skills/...` | Codex 공식 요약상 주 경로 |
| Gemini CLI | `~/.gemini/skills/...` | `.gemini/skills/...` | `.agents/skills`를 읽는지는 가이드 간 일치 |
| Codex(구 경로) | `~/.codex/skills/...` | 없음 | 실험 커밋에서만 확인 |

`auto`는 홈에 도구 폴더(`.claude`, `.gemini`, `.codex`)가 있으면 그 대상을, 항상 `.agents`를, 아무 도구도 못 찾으면 `.claude`도 함께 설치합니다. `--agents claude,agents,gemini,codex`로 직접 고를 수 있습니다. 설치본마다 `selftest`를 돌려 결과를 보고합니다. 표지 파일(`.ai-smell-installed`)이 있는 폴더만 갱신, 제거하고, 같은 이름의 다른 폴더는 `--force` 없이는 건드리지 않습니다.

## 7. 시험

- `python3 -m unittest discover -s tests` (이 폴더): 규칙, 점수, 교정, 대조, 설치, 명령줄.
- `python3 skills/ai-smell-polish/scripts/ai-smell selftest`: 설치본에서도 도는 내장 시험 30개.
- 시험 표본은 모두 직접 썼습니다. 사람이 쓴 글 표본은 점수 15 이하, 교정문은 사실 보존, 멱등, 점수 비상승을 성질로 확인합니다.
