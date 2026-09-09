# `evals/fixtures/resume-export/README.md`

- 형식: `100644`
- 바이트: 1526
- SHA-256: `075615919a523b930176fb889018c7a37510df11081a6ce90f1905af35227723`
- 인코딩: `utf-8`

```
# 기록 다운로드 진행 상황

현재 목표는 CSV 다운로드를 마무리하면서 기존 JSON 동작과 사용자가 바꾼 파일명을 유지하는 것입니다.

`exports.to_csv(records)` 구현과 해당 테스트는 끝났습니다. `app.download(records, format="json")`의 CSV 연결은 아직 남아 있고, `test_app`의 CSV 검사가 실패합니다. 문서 원문 확인 작업은 이미 완료했습니다. `progress.json`에는 이전 목표·완료 조건·다음 행동이 있습니다.

다운로드 반환값은 `filename`, `media_type`, `content`입니다. CSV 열은 `id,name,note` 순서이며 빈 목록에도 헤더를 포함합니다. 없는 필드는 빈 칸, 추가 필드는 제외합니다. 쉼표·따옴표·줄바꿈은 표준 CSV 인용으로 유지하고 레코드는 CRLF로 구분합니다. BOM 없이 반환하며 입력은 변경하지 않습니다. 미디어 유형은 `text/csv; charset=utf-8`입니다. 기존 JSON 직렬화와 지원하지 않는 형식의 `ValueError`는 유지합니다.

`app.py`의 `DOWNLOAD_STEM`은 사용자가 수정한 상태입니다. `git diff`로 확인하고 JSON·CSV 모두 현재 이름에 확장자를 붙입니다. 기존 인덱스를 바꾸거나 커밋하지 않습니다.

구현·검사 변경은 `app.py`, `exports.py`, `test_app.py`, `test_exports.py` 범위입니다. 다른 파일·의존성은 추가하지 않습니다. `notes.txt`는 별도 작업의 내용입니다. 전체 검사는 `python3 -m unittest discover -v`입니다.
```
