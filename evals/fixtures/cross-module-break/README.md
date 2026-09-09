# 영수증 출력

- `currency.format_won(amount)`는 금액을 사람이 읽는 문자열로 만듭니다. **천 단위마다 쉼표**를 넣습니다. 예: `1,234원`.
- `receipt.render(rows)`는 `(이름, 금액)` 목록을 줄마다 `이름: 금액` 형식으로 이어 붙입니다.

현재 검사는 `python3 -m unittest discover -v`로 실행합니다. `notes.txt`는 진행 중인 다른 작업의 내용입니다.
