# 10 검증

- 상태 확인 → 한 가지 변경 → 가장 작은 직접 검증 순서로 진행합니다.
- 테스트·빌드·실행·UI 확인을 하지 않았다면 통과라고 쓰지 않습니다. 실패는 원인 가설 하나로 재검증합니다.
- 파일을 쓴 뒤에는 현재 내용을 첫 줄부터 끝까지 다시 읽고, 마지막 쓰기 이후 테스트·빌드·렌더 검증을 반드시 실행합니다.
- `/GTG` UI 변경은 `verify_plan.py --require-multi-page --require-ui-evidence`의 `ok: true`가 필수이며, 다중 경로(`verify_multi_page.py`) 렌더링 무결성을 증명해야 합니다.
- UI는 `verify_ui_render.py <HTML> --output-dir <DIR>`로 320px·768px·1280px 화면을 렌더링하여 `scrollWidth` 및 오버플로우를 계측하고 `ok: true`를 확인합니다.
- 내부 사고를 늘어놓지 말고 결론·근거·실행한 검증·남은 리스크만 간결하게 보고합니다.
