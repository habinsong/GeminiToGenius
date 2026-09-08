"""에이전트가 사용하는 로컬 작업·검증 명령입니다."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3

from .runner import CommandCancelled, cancellation_signals, execute, status
from .sessions import Sessions, key
from .spec import sensitive
from .store import Store
from .certificate import build as certificate, replay
from .checkpoints import record as record_checkpoint
from .inspection import inspect
from .discovery import discover
from .platforms import PLATFORMS


def read_document(path: Path) -> dict:
    if sensitive(path) or any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError("민감 경로나 심볼릭 링크를 작업 문서로 읽지 않습니다.")
    return json.loads(path.read_text(encoding="utf-8"))


def write_document(path: Path, document: dict):
    if sensitive(path) or any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError("민감 경로나 심볼릭 링크에 문서를 쓰지 않습니다.")
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    inspection = commands.add_parser("inspect", help="여러 텍스트 파일을 읽고 범위·잘림·해시를 반환합니다.")
    inspection.add_argument("paths", nargs="+")
    inspection.add_argument("--workspace", type=Path)
    inspection.add_argument("--max-bytes", type=int, default=65536)
    inspection.add_argument("--start-line", type=int, default=1)
    inspection.add_argument("--end-line", type=int)
    start = commands.add_parser("start", help="완료 조건을 고정한 작업을 시작합니다.")
    start.add_argument("--workspace", type=Path)
    start.add_argument("--spec", type=Path, required=True)
    start.add_argument("--platform", choices=PLATFORMS)
    start.add_argument("--session")
    tasks = commands.add_parser("tasks", help="저장된 작업·메모·연결 후보를 읽기 전용으로 조회합니다.")
    tasks.add_argument("--workspace", type=Path)
    tasks.add_argument("--limit", type=int, default=10)
    tasks.add_argument("--offset", type=int, default=0)
    attach = commands.add_parser("attach", help="기존 작업과 검증·메모를 현재 호스트 세션에 연결합니다.")
    attach.add_argument("task_id")
    attach.add_argument("--workspace", type=Path)
    attach.add_argument("--platform", choices=PLATFORMS, required=True)
    attach.add_argument("--session", required=True)
    attach.add_argument("--previous-host-stopped", action="store_true",
                        help="이전 호스트가 끝난 것을 확인한 경우에만 지정합니다. 실행 중인 검사는 덮어쓰지 않습니다.")
    verify = commands.add_parser("verify", help="등록된 검증 명령을 직접 실행합니다.")
    verify.add_argument("task_id")
    verify.add_argument("--workspace", type=Path)
    verify.add_argument("--check", help="지정한 검사만 실행합니다. 전체 완료 상태는 verified로 구분합니다.")
    verify.add_argument("--all", action="store_true",
                        help="첫 실패에서 멈추지 않고 등록된 모든 검사를 실행합니다.")
    for name in ("status", "recover"):
        command = commands.add_parser(name)
        command.add_argument("task_id")
        command.add_argument("--workspace", type=Path)
    certify = commands.add_parser("certify", help="완료 주장을 실행 명령·파일 지문에 묶은 증명서를 만듭니다.")
    certify.add_argument("task_id")
    certify.add_argument("--workspace", type=Path)
    certify.add_argument("--output", type=Path, help="증명서를 저장할 경로입니다. 없으면 표준 출력만 사용합니다.")
    replaying = commands.add_parser("replay", help="증명서만 읽어 명령을 다시 실행하고 주장을 재구성합니다.")
    replaying.add_argument("--certificate", type=Path, required=True)
    replaying.add_argument("--workspace", type=Path)
    replaying.add_argument("--trust-commands", action="store_true",
                           help="증명서에 기록된 작업공간과 다른 폴더에서 명령을 실행할 때만 지정합니다.")
    checkpoint = commands.add_parser("checkpoint", help="검증 결과와 별개인 재개용 메모를 저장합니다.")
    checkpoint.add_argument("task_id")
    checkpoint.add_argument("--note", type=Path, required=True)
    checkpoint.add_argument("--workspace", type=Path)
    for name in ("pause", "resume"):
        command = commands.add_parser(name)
        command.add_argument("--platform", choices=PLATFORMS, required=True)
        command.add_argument("--session", required=True)
        command.add_argument("--workspace", type=Path)
        if name == "pause":
            command.add_argument("--reason", required=True)
    args = parser.parse_args()
    store = None
    try:
        # --workspace를 생략하면 현재 폴더를 씁니다. --state를 함께 주면 그 경로가 우선합니다.
        args.workspace = args.workspace or Path.cwd()
        if args.command == "inspect":
            result = inspect(args.workspace, args.paths, args.max_bytes, args.start_line, args.end_line)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "replay":
            # 상태 DB를 읽지 않습니다. 증명서와 현재 파일만으로 다시 실행합니다.
            report = replay(read_document(args.certificate), args.workspace, trust_commands=args.trust_commands)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return int(not report["reconstructed"])
        state_root = args.workspace.resolve(strict=True)
        if not state_root.is_dir() or sensitive(state_root):
            raise ValueError("비민감 작업공간 폴더가 필요합니다.")
        state_path = (args.state or state_root / ".gtg/state.sqlite3").absolute()
        if sensitive(state_path):
            raise ValueError("민감 경로를 작업 상태로 읽지 않습니다.")
        if args.command == "tasks":
            print(json.dumps(discover(state_root, state_path, args.limit, args.offset), ensure_ascii=False, indent=2))
            return 0
        if (args.command == "attach" or (args.command == "start" and args.session)) and state_path != state_root / ".gtg/state.sqlite3":
            raise ValueError("호스트 연결에는 해당 작업공간의 .gtg/state.sqlite3 경로를 사용하세요.")
        if args.command == "attach" and not state_path.exists():
            raise ValueError("연결할 작업 상태가 없습니다.")
        if args.command != "start" and not state_path.exists():
            # 조회·검증 명령은 새 상태 DB를 만들지 않습니다.
            raise ValueError("이 경로에 GTG 작업 상태가 없습니다. 해당 작업공간에서 실행하거나 --workspace로 지정하세요.")
        store = Store(state_path)
        if args.command == "start":
            spec = read_document(args.spec)
            if bool(args.platform) != bool(args.session):
                raise ValueError("호스트와 세션은 함께 지정해야 합니다.")
            if args.session:
                task_id = Sessions(store).start(key(args.platform, args.session), args.workspace, spec)
            else:
                task_id = store.create(args.workspace, spec)
            result = status(store, task_id)
        elif args.command == "attach":
            Sessions(store).attach(key(args.platform, args.session), args.task_id, state_root, args.previous_host_stopped)
            result = {"attached": True, **status(store, args.task_id)}
        elif args.command == "verify":
            checks = store.task(args.task_id)["spec"]["checks"]
            ids = [args.check] if args.check else [check["id"] for check in checks]
            with cancellation_signals():
                for check_id in ids:
                    outcome = execute(store, args.task_id, check_id)
                    if outcome["status"] != "passed" and not args.all:
                        break
            result = status(store, args.task_id)
            result["requested_checks"] = ids
            result["requested_verified"] = all(check["status"] == "passed" for check in result["checks"] if check["id"] in ids)
        elif args.command == "recover":
            result = {"recovered": store.recover(args.task_id), **status(store, args.task_id)}
        elif args.command == "certify":
            document = certificate(store, args.task_id)
            if args.output:
                write_document(args.output, document)
            print(json.dumps({**document, "state_path": str(state_path),
                              "output": str(args.output) if args.output else None}, ensure_ascii=False, indent=2))
            # 표준 출력의 편의 필드는 digest 본문이 아닙니다. 저장 파일은 본문만 담습니다.
            return int(not document["verified"])
        elif args.command == "checkpoint":
            checkpoint_id = record_checkpoint(store, args.task_id, read_document(args.note))
            result = {"checkpoint_id": checkpoint_id, **status(store, args.task_id)}
        elif args.command in {"pause", "resume"}:
            sessions = Sessions(store)
            session = key(args.platform, args.session)
            if args.command == "pause":
                sessions.pause(session, args.reason)
            else:
                sessions.resume(session)
            result = {"ok": True, "paused": args.command == "pause"}
        else:
            result = status(store, args.task_id)
        if "task_id" in result:
            result["continuation"] = Sessions(store).for_task(result["task_id"])
        result["state_path"] = str(state_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(args.command == "verify" and not result["requested_verified"])
    except (OSError, ValueError, sqlite3.Error) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1
    except CommandCancelled as error:
        print(json.dumps({"ok": False, "error": "중단 신호로 검사를 종료했습니다.", "signal": error.signum}, ensure_ascii=False))
        return 128 + error.signum
    except KeyboardInterrupt:
        print(json.dumps({"ok": False, "error": "사용자가 검사를 중단했습니다."}, ensure_ascii=False))
        return 130
    finally:
        if store is not None:
            store.close()


if __name__ == "__main__":
    raise SystemExit(main())
