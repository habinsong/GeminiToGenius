# 10 검증

- 상태 확인 → 한 가지 변경 → 가장 작은 직접 검증 순서로 진행합니다.
- 테스트·빌드·실행·UI 확인을 하지 않았다면 통과라고 쓰지 않습니다. 실패는 원인 가설 하나로 재검증합니다.
- 파일을 쓴 뒤에는 그 파일의 현재 내용을 첫 줄부터 마지막 줄까지 다시 읽습니다. 마지막 쓰기 이후 프로젝트에 맞는 테스트·빌드·lint·typecheck·실행 또는 렌더 검증이 없으면 종료하지 않습니다.
- 코드 변경은 주요 파일의 LOC와 책임을 다시 확인합니다. 새 God Object를 만들지 않았는지, 공개 동작과 의존 방향을 지켰는지, 새 책임에 직접 대응하는 검증이 있는지 확인합니다.
- `/GTG` UI 변경은 `verify_plan.py`의 `ok: true`가 먼저 있어야 합니다. 다중 페이지 대상이면 `verify_multi_page.py`가 모든 HTML 경로의 실제 링크와 렌더를 통과해야 합니다. `prefers-reduced-motion`, 보이는 focus, loading·empty·error·success·disabled·selected 상태를 계획과 화면에서 대조합니다.
- UI는 생성 코드의 금지 패턴을 먼저 검사한 뒤 `python3 ~/.gemini/config/agy-focus/current/scripts/verify_ui_render.py <HTML> --output-dir <DIR>`를 실행해 설치된 Chrome으로 320px·1280px 화면을 렌더링하고 `scrollWidth`·요소 경계를 계측합니다. `ok: true`가 아니거나 이미지를 직접 열지 않았으면 통과시키지 않습니다. HTTP 200·HTML 파서·`curl`은 화면 검증이 아닙니다.
- 내부 사고를 늘어놓지 말고 결론·근거·실행한 검증·남은 리스크만 보고합니다.
