from pathlib import Path


for name in ("exporter.py", "startup.py", "sdk.py", "test_export.py", "build.py"):
    compile(Path(name).read_text(encoding="utf-8"), name, "exec", dont_inherit=True)
