# 배송비 계산

`shipping.shipping_fee(weight_kg, express=False)`의 요금 규칙입니다.

- 기본 요금 3000원.
- 5kg를 **초과하는** 무게에 대해 1kg마다 500원을 더합니다. 정확히 5kg는 추가 요금이 없습니다.
- `express`가 참이면 마지막에 2배로 합니다.

현재 검사는 `python3 -m unittest discover -v`로 실행합니다. `notes.txt`는 진행 중인 다른 작업의 내용입니다.
