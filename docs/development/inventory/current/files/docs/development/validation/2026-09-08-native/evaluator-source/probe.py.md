# `docs/development/validation/2026-09-08-native/evaluator-source/probe.py`

- 형식: `100644`
- 바이트: 1161
- SHA-256: `0c124848ea6df51f4ac97ce7d545767ce338aa6b9f9e3c35d61141070396f71b`
- 인코딩: `utf-8`

```
"""평가 대상 모듈은 채점 부모 프로세스와 분리해서 실행합니다."""

import contextlib
import importlib.util
import json
from pathlib import Path
import sys


def main():
    workspace, module_name, function_name = sys.argv[1:]
    sys.path.insert(0, workspace)
    request = json.load(sys.stdin)
    with contextlib.redirect_stdout(sys.stderr):
        spec = importlib.util.spec_from_file_location("candidate", Path(workspace) / module_name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        function = getattr(module, function_name)
        responses = []
        for case in request:
            args = case["args"]
            before = json.dumps(args, sort_keys=True)
            try:
                value = function(*args)
                result = {"value": value}
            except Exception as error:
                result = {"error": type(error).__name__}
            result["arguments_preserved"] = json.dumps(args, sort_keys=True) == before
            responses.append(result)
    print(json.dumps(responses, ensure_ascii=False))


if __name__ == "__main__":
    main()
```
