"""평가 CLI와 기존 Python 호출 진입점을 유지합니다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "evals"

from .comparison import compare
from .definitions import CASES, PROBE, ROOT, case_by_id, definition_digest
from .execution import run_arm
from .grading import csv_rows, evaluate_function, grade, same_output, same_value, terminate
from .preparation import prepare
from .workspace import digest, environment_info, git_command, git_state, private, seed_user_edits, snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("prepare")
    start.add_argument("case_id")
    start.add_argument("target", type=Path)
    start.add_argument("--profile", choices=("baseline", "gtg"), default="baseline")
    start.add_argument("--arm", help="비교 보고서에 쓸 하네스 라벨입니다. 기본값은 프로필 이름입니다.")
    start.add_argument("--model", help="비교 보고서에 쓸 모델 라벨입니다. 선언 값이며 검증하지 않습니다.")
    execute = commands.add_parser("run", help="준비된 요청을 그대로 전달해 하네스를 실행하고 관측을 기록합니다.")
    execute.add_argument("target", type=Path)
    execute.add_argument("--timeout", type=float, default=1800)
    execute.add_argument("argv", nargs="+", help="`--` 뒤에 실행할 명령입니다. {prompt} 자리에 준비된 요청이 들어갑니다.")
    score = commands.add_parser("grade")
    score.add_argument("target", type=Path)
    contrast = commands.add_parser("compare", help="같은 조건의 시행만 하네스별로 모읍니다.")
    contrast.add_argument("trials", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "run":
            observed = run_arm(args.target, args.argv, timeout=args.timeout)
            print(json.dumps(observed, ensure_ascii=False, indent=2))
            return int(not observed["ok"])
        if args.command == "compare":
            report = compare(args.trials)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return int(not report["comparable"])
        result = (prepare(args.case_id, args.target, args.profile, arm=args.arm, model=args.model)
                  if args.command == "prepare" else grade(args.target))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(args.command == "grade" and not result["artifact_passed"])
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
