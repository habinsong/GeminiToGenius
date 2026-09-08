# 기록 다운로드

`app.download(records, format="json")`은 웹 계층에 전달할 `filename`, `media_type`, `content` 객체를 반환합니다. 파일 저장과 HTTP 전송은 호출자가 담당합니다. 기존 JSON은 `exports.to_json`을 사용하며 UTF-8 문자와 두 칸 들여쓰기를 유지합니다. 지원하지 않는 형식은 `ValueError`입니다.

CSV 요청이 들어오면 `exports.to_csv(records)`와 `download(records, "csv")`를 추가합니다. CSV 열은 `id,name,note` 순서이며 헤더는 빈 목록에도 포함합니다. 없는 필드는 빈 칸, 추가 필드는 제외합니다. 쉼표·따옴표·줄바꿈은 표준 CSV 인용으로 보존하고 레코드 구분은 CRLF입니다. 문자열은 BOM 없이 반환하고 입력 목록·객체는 바꾸지 않습니다. CSV의 미디어 유형은 `text/csv; charset=utf-8`입니다.

사용자가 `app.py`의 `DOWNLOAD_STEM`을 수정한 상태로 작업을 시작합니다. `git diff`로 현재 변경을 확인하고 JSON·CSV 모두 현재 파일명에서 확장자만 바꿉니다. 기존 인덱스를 바꾸거나 커밋하지 않습니다.

구현 범위는 `app.py`, `exports.py`이며 기존 `test_app.py` 수정과 새 `test_exports.py` 추가가 가능합니다. 다른 파일과 의존성을 추가하지 않습니다. `notes.txt`는 다른 작업의 내용입니다.

검사는 `python3 -m unittest discover -v`입니다. 현재 검사는 기존 JSON 동작만 확인하므로 CSV 구현 후 관련 검사를 추가해야 합니다.
