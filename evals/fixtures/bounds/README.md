# 범위 제한 함수

`mathlib.clamp(value, lower, upper)`는 값을 닫힌 구간 안으로 제한합니다. 상한과 하한은 포함하며 정수와 실수를 지원합니다. 하한이 상한보다 크면 `ValueError`로 잘못된 설정을 알립니다.

현재 검사는 `python3 -m unittest discover -v`로 실행합니다. `notes.txt`는 진행 중인 다른 작업의 내용입니다.
