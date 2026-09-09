# `docs/development/validation/2026-09-08-native-stop/preflight-missing-caller.txt`

- 형식: `100644`
- 바이트: 1081
- SHA-256: `e737e9ffef94fd9eb3eda20bfdab9bebd942eb77188f47a42acc4a4255e17149`
- 인코딩: `utf-8`

```
test_records (unittest.loader._FailedTest.test_records) ... ERROR

======================================================================
ERROR: test_records (unittest.loader._FailedTest.test_records)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_records
Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/unittest/loader.py", line 426, in _find_test_path
    module = self._get_module_from_name(name)
  File "/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/unittest/loader.py", line 367, in _get_module_from_name
    __import__(name)
    ~~~~~~~~~~^^^^^^
  File "/private/var/folders/wt/88c641tj50z4rzrm6pfdld6c0000gn/T/gtg-native-stop-nb0skej3/test_records.py", line 3, in <module>
    from app import summarize
ModuleNotFoundError: No module named 'app'


----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```
