<div align="center">

<h1>GeminiToGenius</h1>

<p>Gemini를 조금 더 똑똑하게(덜 멍청하게) 만드는 하네스 플러그인입니다.</p>

<p>한국어 · <a href="docs/README.en.md">English</a></p>

<p><a href="https://github.com/habinsong/GeminiToGenius/releases">릴리즈</a> · <a href="docs/product/getting-started.md">설치 안내</a> · <a href="docs/verification/README.md">검증 기록과 한계</a> · <a href="CHANGELOG.md">변경 기록</a></p>

<p>GTG 3.3.3은 Antigravity 데스크톱과 IDE, Antigravity CLI, Gemini CLI를 지원합니다.</p>

</div>

## 하는 일

- **작업 계약 고정**: 작업 시작 전 완료 조건과 검증 명령을 고정하여, 도중에 임의로 검사를 건너뛰거나 완화하지 못하게 막습니다.
- **실제 명령 검증 (`verify`)**: 등록된 검증 명령을 실제로 실행하고 종료 코드, 실행 시간, 파일 지문을 투명하게 기록합니다.
- **독립 재현 증명서 (`certify`, `replay`)**: 완료 주장과 실행 근거를 단일 파일로 묶어, 외부 데이터베이스 없이 작업 공간만으로 검증을 재현합니다.
- **코드 구조 검사 (`structure`)**: 빈 함수, 신규 TODO, 대형 파일 누적, 거대 클래스, 쓰이지 않는 정의를 차단합니다.
- **문체 및 AI 슬롭 검사 (`prose`)**: 한국어와 영문 상투구, 번역투, 3항 나열(Tricolon) 강박, 기계적 문단 균일성, em dash(`—`) 삽입구를 찾아 0~100점 점수로 환산합니다. 원문과 대조하여 수치와 인용구 누락 여부도 함께 검증합니다.
- **저장소별 교훈 축적 (`lesson`)**: 작업 도중 드러난 실패와 오류를 근거와 함께 남겨, 다음 세션에서 같은 실수를 되풀이하지 않도록 전달합니다.

## 설치

macOS 또는 Linux 환경, Python 3.10 이상, Git이 필요합니다. 외부 Python 패키지는 요구하지 않습니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
cd GeminiToGenius
bash scripts/install.sh
```

설치 상태 확인과 제거는 아래 명령으로 수행합니다.

```bash
python3 scripts/install.py doctor
python3 scripts/install.py uninstall
```

## 쓰는 법

설치 후에는 평소처럼 자연어로 요청하시면 됩니다. 슬래시 명령이나 별도의 명세 파일을 작성하실 필요가 없습니다.

코드 동작이나 타입을 변경하는 작업은 파일 하나만 수정하더라도 실제 빌드와 필수 시험을 완료 계약에 연결하도록 안내합니다.

### 문체 검사 CLI 직접 실행

저장소 내 문서를 검사하거나 원문과 대조할 때 직접 실행하실 수 있습니다.

```bash
# 일반 문서 문체 검사
python3 -m gtg prose docs/product/getting-started.md

# 학술/보고서 갈래 검사
python3 -m gtg prose --register academic paper.md

# 윤문 전후 사실 대조 (수치·인용 누락 검사)
python3 -m gtg prose --original draft.md polished.md

# 표준 입력 검사
python3 -m gtg prose - <<'EOF'
검사할 본문을 여기에 입력합니다.
EOF
```

## 대상 모델과 주의사항

### Gemini 4 Argon · Neon · Carbon
소프트웨어 작업과 다단계 추론에 적합합니다. 기본 사고 수준은 medium이며, 여러 파일에 걸친 복잡한 작업에는 high 설정을 권장합니다.

### Gemini 3.8 Flash · Gemini 4 Hydrogen 사용 금지 (비권장)
**Gemini 3.8 Flash와 Gemini 4 Hydrogen 모델은 추론 강도(low, medium, high)와 무관하게 실사용을 권장하지 않으며, 특히 윤문 작업에는 절대 사용하지 마십시오.**

실측 결과, 다음과 같은 치명적 결함이 반복 확인되었습니다:
1. **전역 규칙 무시**: 시스템 지시와 제약 조건이 명시되어 있어도 이를 무시하고 학습된 페르소나 가중치에 따라 제멋대로 행동합니다.
2. **없는 사실과 배경 날조 (Fabrication)**: '인간다운 글'을 흉내 낸답시고 원문에 전혀 없는 사물, 타사 도구 경험담, 개인적 고통과 사연을 지어내서 끼워 넣습니다.
3. **싸구려 구어체 감정 과장**: 객관적 사실 서술을 왜곡하여 저급한 구어체 불평이나 인위적인 감정 표현을 주입합니다.

따라서 신뢰할 수 있는 코드 작업이나 윤문이 필요할 때는 Gemini 3.8 Flash와 Gemini 4 Hydrogen을 쓰지 마시고, Gemini 4 Argon, Neon, Carbon이나 상위 추론 모델을 사용하십시오.

## 문서

- [설치와 첫 사용](docs/product/getting-started.md)
- [동작 방식](docs/product/how-it-works.md)
- [CLI 명령 목록](docs/reference/cli.md)
- [완료 증명서 규격](docs/reference/certificate.md)
- [검증 기록과 한계](docs/verification/README.md)
- [전체 문서 색인](docs/README.md)

## 라이선스

MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE)를 참고해 주십시오. Google, Antigravity, Gemini와 공식 제휴나 후원 관계가 아닙니다.
