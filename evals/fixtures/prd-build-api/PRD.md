# 내보내기 요구

- BUILD-01: `build.py`가 검사하는 모든 소스가 컴파일되어야 합니다. 실행하지 않은 진입점도 제외하지 않습니다.
- UT-01: `test_export.ExportTests.test_text_and_dimensions`에서 문자열과 크기가 SDK 반환 계약대로 보존되어야 합니다.
- UT-02: `test_export.ExportTests.test_invalid_dimensions`에서 0 이하 크기는 `ValueError`여야 합니다.
- UT-03: `test_export.ExportTests.test_startup`에서 제품 진입점이 `{"text": "sample", "width": 1, "height": 1}`을 반환해야 합니다.

SDK 공개 정의는 `sdk.py`에 있습니다. 시험 삭제·skip·기대값 완화·없는 API의 추가는 허용하지 않습니다. PRD 변경 없이 현재 계약을 충족합니다.
