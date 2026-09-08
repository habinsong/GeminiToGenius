# `gtg/coverage.py`

- 형식: `100644`
- 바이트: 6649
- SHA-256: `e5194dbb5b5710a8e93dee006f5ce962ef7cb2d8f64986a212ec2a9b624b6137`
- 인코딩: `utf-8`

```
"""검사가 실제로 실행한 Python 파일을 기록합니다.

통과한 검사도 무엇을 실행하지 않았는지 함께 밝혀야 근거가 됩니다. 이 모듈은 실행 사실만
관찰하며 표준 라이브러리만 사용합니다. 파일 단위 실행 관찰이므로 줄·분기 수준의 검증이
아니고, 실행했다는 사실이 그 파일의 요구를 모두 확인했다는 뜻도 아닙니다.
"""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import tempfile

from .spec import private, relative

DIRECTORY = "GTG_COVERAGE_DIR"
# 넓은 검증 범위에서 목록 작성 자체가 비싸지지 않게 막습니다. 상한을 넘으면 범위를 주장하지 않습니다.
MAX_WATCHED_FILES = 2000

# 인터프리터 시작 시점에 등록해야 사용자 코드의 첫 실행부터 관찰합니다.
# 다른 sitecustomize를 가리지 않도록 남은 경로에서 원본을 이어서 불러옵니다.
BOOTSTRAP = '''"""GTG가 검사 실행 중에만 사용하는 임시 관찰기입니다."""

import atexit
import json
import os
import sys

_target = os.environ.get("GTG_COVERAGE_DIR")
if _target:
    _seen = set()

    def _dump():
        try:
            path = os.path.join(_target, "%d-%d.json" % (os.getpid(), id(_seen)))
            with open(path, "w", encoding="utf-8") as stream:
                json.dump(sorted(_seen), stream)
        except Exception:
            pass

    monitoring = getattr(sys, "monitoring", None)
    if monitoring is not None:
        _tool = None
        for _candidate in range(6):
            try:
                if monitoring.get_tool(_candidate) is None:
                    _tool = _candidate
                    break
            except Exception:
                break
        if _tool is not None:
            try:
                monitoring.use_tool_id(_tool, "gtg-coverage")

                def _started(code, offset):
                    _seen.add(code.co_filename)
                    return monitoring.DISABLE

                monitoring.register_callback(_tool, monitoring.events.PY_START, _started)
                monitoring.set_events(_tool, monitoring.events.PY_START)
                atexit.register(_dump)
            except Exception:
                pass
    else:
        def _traced(frame, event, arg):
            _seen.add(frame.f_code.co_filename)
            return None

        try:
            sys.settrace(_traced)
            atexit.register(_dump)
        except Exception:
            pass

# 우리 폴더를 뺀 나머지 경로에서 원래 sitecustomize를 이어서 실행합니다.
try:
    import importlib.util

    _here = os.path.dirname(os.path.abspath(__file__))
    _rest = [entry for entry in sys.path if entry and os.path.abspath(entry) != _here]
    _spec = None
    for _entry in _rest:
        _candidate_path = os.path.join(_entry, "sitecustomize.py")
        if os.path.isfile(_candidate_path):
            _spec = importlib.util.spec_from_file_location("_gtg_prior_sitecustomize", _candidate_path)
            break
    if _spec is not None and _spec.loader is not None:
        _module = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_module)
except Exception:
    pass
'''


class Session:
    """한 검사 실행 동안의 관찰 결과입니다."""

    def __init__(self, directory: Path):
        self.directory = directory
        self._files: set[Path] | None = None

    def environment(self) -> dict:
        existing = os.environ.get("PYTHONPATH")
        path = str(self.directory / "bootstrap")
        return {**os.environ, DIRECTORY: str(self.directory / "records"),
                "PYTHONPATH": path + os.pathsep + existing if existing else path,
                # 관찰기는 바이트코드를 남기지 않습니다.
                "PYTHONDONTWRITEBYTECODE": "1"}

    def files(self) -> set[Path]:
        if self._files is None:
            found = set()
            records = self.directory / "records"
            for path in sorted(records.glob("*.json")) if records.is_dir() else []:
                try:
                    names = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                for name in names if isinstance(names, list) else []:
                    if isinstance(name, str) and os.path.isabs(name):
                        try:
                            found.add(Path(name).resolve())
                        except OSError:
                            continue
            self._files = found
        return self._files

    def observed(self) -> bool:
        """Python 실행을 하나라도 관찰했는지입니다. 거짓이면 미실행을 주장하지 않습니다."""
        return bool(self.files())


@contextmanager
def collector():
    directory = Path(tempfile.mkdtemp(prefix="gtg-coverage-"))
    try:
        bootstrap = directory / "bootstrap"
        bootstrap.mkdir()
        (bootstrap / "sitecustomize.py").write_text(BOOTSTRAP, encoding="utf-8")
        (directory / "records").mkdir()
        yield Session(directory)
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def watched_python_files(root: Path, watched: list[str]) -> list[Path]:
    """검증 대상 중 실행 관찰이 가능한 Python 파일만 모읍니다."""
    found = []
    for name in watched:
        target = root / relative(name)
        if target.is_file():
            candidates = [target]
        elif target.is_dir():
            candidates = [path for path in sorted(target.rglob("*.py")) if path.is_file()]
        else:
            continue
        for path in candidates:
            if path.suffix == ".py" and not private(path.relative_to(root)) and path not in found:
                found.append(path)
                if len(found) >= MAX_WATCHED_FILES:
                    return found
    return found


def executed_watch(root: Path, watched: list[str], files: set[Path]) -> tuple[list[str], list[str] | None]:
    """실행한 대상과 실행하지 않은 대상입니다. 범위를 다 세지 못하면 두 번째 값이 없습니다."""
    candidates = watched_python_files(root, watched)
    complete = len(candidates) < MAX_WATCHED_FILES
    ran, missed = [], []
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        (ran if resolved in files else missed).append(path.relative_to(root).as_posix())
    return sorted(ran), sorted(missed) if complete else None
```
