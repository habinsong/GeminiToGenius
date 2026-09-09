# `gtg/coverage.py`

- 형식: `100644`
- 바이트: 11046
- SHA-256: `7c5cee96a47f58e8e515916f464c05ca76737fa1cfb2e1156d674d3e332c599e`
- 인코딩: `utf-8`

```
"""검사가 실제로 실행한 코드 파일을 기록합니다.

통과한 검사도 무엇을 실행하지 않았는지 함께 밝혀야 근거가 됩니다. 이 모듈은 실행 사실만
관찰하며 표준 라이브러리와 각 런타임의 기본 기능만 사용합니다. Python은 `sys.monitoring`,
Node는 `module.registerHooks`로 관찰합니다. 파일 단위 실행 관찰이므로 줄·분기 수준의 검증이
아니고, 실행했다는 사실이 그 파일의 요구를 모두 확인했다는 뜻도 아닙니다. 관찰할 수 없는
언어가 범위에 있으면 미실행을 주장하지 않습니다.
"""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import tempfile

from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

from .spec import private, relative

DIRECTORY = "GTG_COVERAGE_DIR"
# 실행을 실제로 관찰할 수 있는 확장자입니다.
OBSERVABLE = (".py", ".js", ".mjs", ".cjs")
# 네이티브로 실행하면 관찰되고 컴파일해서 실행하면 보이지 않습니다. 실행 방식은 관측으로 판단합니다.
AMBIGUOUS = (".ts", ".mts", ".cts")
# 관찰할 수 없는 코드입니다. 범위에 있으면 미실행을 주장하지 않습니다.
UNOBSERVED_CODE = (".tsx", ".jsx", ".go", ".rs", ".rb", ".java", ".kt", ".swift",
                   ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".php", ".sh", ".bash", ".zsh", ".pl", ".lua")
# 넓은 검증 범위에서 목록 작성 자체가 비싸지지 않게 막습니다. 상한을 넘으면 범위를 주장하지 않습니다.
MAX_WATCHED_FILES = 2000
# 왜 판단하지 못했는지 알리기 위한 표본입니다. 전체 목록이 아닙니다.
MAX_UNOBSERVABLE = 8

# 인터프리터 시작 시점에 등록해야 사용자 코드의 첫 실행부터 관찰합니다.
# 다른 sitecustomize를 가리지 않도록 남은 경로에서 원본을 이어서 불러옵니다.
BOOTSTRAP = '''"""GTG가 검사 실행 중에만 사용하는 임시 관찰기입니다."""

import atexit
import json
import os
import sys

# 중첩 실행에서 두 번 등록하지 않습니다. 바깥 관찰기가 이미 붙어 있으면 그대로 둡니다.
_target = os.environ.get("GTG_COVERAGE_DIR") if not getattr(sys, "_gtg_coverage_active", False) else None
if _target:
    sys._gtg_coverage_active = True
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
        # 다른 GTG 부트스트랩 폴더는 같은 내용이므로 건너뛰고 사용자 파일을 찾습니다.
        if os.path.isfile(os.path.join(_entry, "gtg-node-coverage.js")):
            continue
        if os.path.isfile(_candidate_path):
            _spec = importlib.util.spec_from_file_location("_gtg_prior_sitecustomize", _candidate_path)
            break
    if _spec is not None and _spec.loader is not None:
        _module = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_module)
except Exception:
    pass
'''


NODE_BOOTSTRAP = '''"use strict";
// GTG가 검사 실행 중에만 사용하는 임시 관찰기입니다.
try {
  const target = process.env.GTG_COVERAGE_DIR;
  if (target) {
    const nodeModule = require("node:module");
    if (typeof nodeModule.registerHooks === "function") {
      const seen = new Set();
      nodeModule.registerHooks({
        load(url, context, next) {
          if (typeof url === "string" && url.startsWith("file://")) { seen.add(url); }
          return next(url, context);
        },
      });
      process.on("exit", () => {
        try {
          const fs = require("node:fs");
          const path = require("node:path");
          const name = "node-" + process.pid + "-" + Date.now() + ".json";
          fs.writeFileSync(path.join(target, name), JSON.stringify([...seen]));
        } catch (error) { /* 관찰 실패는 검사를 방해하지 않습니다. */ }
      });
    }
  }
} catch (error) { /* 관찰 실패는 검사를 방해하지 않습니다. */ }
'''


class Session:
    """한 검사 실행 동안의 관찰 결과입니다."""

    def __init__(self, directory: Path):
        self.directory = directory
        self._files: set[Path] | None = None

    def environment(self) -> dict:
        bootstrap = self.directory / "bootstrap"
        existing = os.environ.get("PYTHONPATH")
        path = str(bootstrap)
        # 사용자의 기존 설정을 지우지 않고 앞에 덧붙입니다.
        node = "--require " + str(bootstrap / "gtg-node-coverage.js")
        node_existing = os.environ.get("NODE_OPTIONS")
        return {**os.environ, DIRECTORY: str(self.directory / "records"),
                "PYTHONPATH": path + os.pathsep + existing if existing else path,
                "NODE_OPTIONS": node + " " + node_existing if node_existing else node,
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
                    if not isinstance(name, str):
                        continue
                    if name.startswith("file://"):
                        name = url2pathname(unquote(urlparse(name).path))
                    if os.path.isabs(name):
                        try:
                            found.add(Path(name).resolve())
                        except OSError:
                            continue
            self._files = found
        return self._files

    def observed(self) -> bool:
        """실행을 하나라도 관찰했는지입니다. 거짓이면 미실행을 주장하지 않습니다."""
        return bool(self.files())


@contextmanager
def collector():
    directory = Path(tempfile.mkdtemp(prefix="gtg-coverage-"))
    try:
        bootstrap = directory / "bootstrap"
        bootstrap.mkdir()
        (bootstrap / "sitecustomize.py").write_text(BOOTSTRAP, encoding="utf-8")
        (bootstrap / "gtg-node-coverage.js").write_text(NODE_BOOTSTRAP, encoding="utf-8")
        (directory / "records").mkdir()
        yield Session(directory)
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def watched_code_files(root: Path, watched: list[str], *, native: bool = False) -> tuple[list[Path], list[Path]]:
    """관찰 가능한 코드 파일과, 판단을 막은 관찰 불가 파일을 돌려줍니다.

    두 번째 값이 비어 있지 않으면 미실행 목록을 만들 수 없습니다. 어떤 파일 때문인지
    알려야 검증 범위를 좁혀 다시 시도할 수 있습니다.

    `native`는 이번 실행에서 TypeScript가 직접 실행되는 것을 관측했는지입니다. 관측하지
    못했다면 컴파일 산출물을 실행했을 수 있으므로 원본 TypeScript의 미실행을 주장하지 않습니다.
    """
    observable = OBSERVABLE + AMBIGUOUS if native else OBSERVABLE
    found, opaque = [], []
    for name in watched:
        target = root / relative(name)
        if target.is_file():
            candidates = [target]
        elif target.is_dir():
            candidates = [path for path in sorted(target.rglob("*")) if path.is_file()]
        else:
            continue
        for path in candidates:
            if private(path.relative_to(root)):
                continue
            suffix = path.suffix.casefold()
            if suffix in UNOBSERVED_CODE or (suffix in AMBIGUOUS and not native):
                if len(opaque) < MAX_UNOBSERVABLE:
                    opaque.append(path)
            elif suffix in observable and path not in found:
                found.append(path)
                if len(found) >= MAX_WATCHED_FILES:
                    return found, opaque
    return found, opaque


def executed_watch(root: Path, watched: list[str],
                   files: set[Path]) -> tuple[list[str], list[str] | None, list[str]]:
    """실행한 대상, 실행하지 않은 대상, 그리고 그 판단을 막은 관찰 불가 대상입니다.

    두 번째 값이 없는 이유는 두 가지입니다. 관찰할 수 없는 언어가 범위에 있거나
    범위가 너무 커서 다 세지 못한 경우이며, 앞의 경우에만 세 번째 값이 채워집니다.
    """
    # 실행 기록 어디에든 TypeScript가 있으면 이 실행은 네이티브로 돌린 것입니다.
    native = any(path.suffix.casefold() in AMBIGUOUS for path in files)
    candidates, opaque = watched_code_files(root, watched, native=native)
    complete = len(candidates) < MAX_WATCHED_FILES and not opaque
    ran, missed = [], []
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        (ran if resolved in files else missed).append(path.relative_to(root).as_posix())
    return (sorted(ran), sorted(missed) if complete else None,
            sorted(path.relative_to(root).as_posix() for path in opaque))
```
