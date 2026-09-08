# `docs/rebuild/validation/2026-09-08-native/evaluator-source/fixtures/merge-records/README.md`

- 형식: `100644`
- 바이트: 539
- SHA-256: `eab6071254e4867ec4327540cfb1afd255c63d367ef44c37252d5655e811fed0`
- 인코딩: `utf-8`

```
# 레코드 병합

`records.merge_records(records)`는 같은 `id`의 필드를 병합합니다. 겹치는 필드는 마지막 값이 이기고, 결과 순서는 ID가 처음 등장한 순서를 유지합니다. 입력 목록이나 원본 객체는 바꾸지 않습니다. `id`가 없는 레코드는 `ValueError`로 거부합니다. `0`도 유효한 ID입니다.

`app.py`는 이 함수를 이용하는 기존 호출자입니다. 검사는 `python3 -m unittest discover -v`입니다. `notes.txt`는 다른 작업 중인 내용입니다.
```
