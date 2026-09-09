# 가격 계산

`pricing.py`의 `member_total(items, rate)`·`guest_total(items)`·`staff_total(items)`은 공개 함수입니다. 이름·인자·반환값·예외는 `checkout.py`와 다른 코드가 의존하므로 그대로 유지해야 합니다.

- 각 함수는 `{"price": 숫자, "count": 정수}` 목록을 받습니다.
- `count`가 음수면 `ValueError`를 냅니다.
- 합계에서 할인율을 뺀 값을 소수점 두 자리로 반올림해 돌려줍니다. 음수는 0으로 만듭니다.
- 할인율은 회원이 인자로 받은 값, 손님은 0, 직원은 0.3입니다.

검사: `python3 -m unittest discover -s .`
