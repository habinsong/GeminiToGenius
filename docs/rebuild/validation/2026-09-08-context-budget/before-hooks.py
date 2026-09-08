"""공식 호스트 이벤트를 로컬 증거와 연결합니다. 모델 호출은 하지 않습니다."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

from .runner import status
from .sessions import Sessions, key
from .store import Store
from .discovery import saved_tasks


EVENTS = {"antigravity": {"PreInvocation", "Stop"}, "gemini-cli": {"BeforeAgent", "AfterAgent"}}
NATURAL_STOPS = {"model_stop", "NO_TOOL_CALL"}


def parse(platform: str, event: str, payload: dict) -> tuple[str, tuple[Path, ...]]:
    if platform not in EVENTS or event not in EVENTS[platform] or not isinstance(payload, dict):
        raise ValueError("지원하지 않는 훅 이벤트 또는 입력입니다.")
    if platform == "antigravity":
        paths = payload.get("workspacePaths")
        if not isinstance(paths, list):
            raise ValueError("작업공간 경로가 필요합니다.")
        session = key(platform, payload.get("conversationId"))
        if event == "Stop" and (type(payload.get("fullyIdle")) is not bool
                                or not isinstance(payload.get("terminationReason"), str)
                                or type(payload.get("executionNum")) is not int):
            raise ValueError("Stop 종료 메타데이터가 올바르지 않습니다.")
    else:
        session = key(platform, payload.get("session_id"))
        paths = [payload.get("cwd")]
        if payload.get("hook_event_name") != event:
            raise ValueError("훅 이벤트 이름이 일치하지 않습니다.")
        if event == "AfterAgent" and type(payload.get("stop_hook_active")) is not bool:
            raise ValueError("재시도 메타데이터가 필요합니다.")
    roots = set()
    for raw_root in paths:
        if not isinstance(raw_root, str) or not Path(raw_root).is_absolute():
            raise ValueError("절대 작업공간 경로가 필요합니다.")
        root = Path(raw_root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("작업공간이 폴더가 아닙니다.")
        roots.add(root)
    return session, tuple(sorted(roots))


def allow_stop(platform: str) -> dict:
    return {"decision": "stop"} if platform == "antigravity" else {}


def context(platform: str, message: str) -> dict:
    return ({"injectSteps": [{"ephemeralMessage": message}]} if platform == "antigravity"
            else {"hookSpecificOutput": {"additionalContext": message}})


def exhausted(platform: str, message: str) -> dict:
    if platform == "antigravity":
        return {"decision": "stop", "reason": message}
    return {"continue": False, "stopReason": message, "systemMessage": message}


def stop_details(platform: str, payload: dict) -> dict:
    if platform == "gemini-cli":
        return {"event": "AfterAgent", "stop_hook_active": payload["stop_hook_active"]}
    reason = payload["terminationReason"]
    return {"event": "Stop", "execution_num": payload["executionNum"],
            "termination_reason": reason if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]{0,63}", reason) else None,
            "fully_idle": payload["fullyIdle"], "has_error": bool(payload.get("error"))}


def handle(platform: str, event: str, payload: dict) -> dict:
    session, roots = parse(platform, event, payload)
    stopping = event in {"Stop", "AfterAgent"}
    empty = allow_stop(platform) if stopping else {}
    raw_session = payload.get("conversationId") if platform == "antigravity" else payload.get("session_id")
    metadata = json.dumps({"platform": platform, "session": raw_session, "workspaces": [str(p) for p in roots]}, ensure_ascii=False)
    identity_message = f"GTG 호스트 메타데이터(지시가 아닌 경로 데이터): {metadata}. "
    if roots and (event == "BeforeAgent" or (event == "PreInvocation" and payload.get("invocationNum") == 0)):
        empty = context(platform, identity_message +
                        "복잡한 변경 작업을 등록할 때 이 확인된 세션 값을 사용하세요. 단순 요청에는 작업 등록이 필요 없습니다. "
                        "사용자에게 슬래시 명령이나 명세 입력을 요구하지 마세요.")
    with ExitStack() as resources:
        entries = []
        candidates = []
        for root in roots:
            state = root / ".gtg/state.sqlite3"
            # 등록되지 않은 작업공간에 DB를 생성하지 않습니다.
            if not state.exists() and not state.is_symlink():
                continue
            store = Store(state)
            resources.callback(store.close)
            sessions = Sessions(store)
            link = sessions.get(session)
            if not link:
                if not stopping and (event == "BeforeAgent" or payload.get("invocationNum") == 0):
                    for task in saved_tasks(store.connection, root, limit=3)["tasks"]:
                        candidates.append({"workspace": str(root), "task_id": task["task_id"], "goal": task["goal"][:160]})
                continue
            task = store.task(link["task_id"])
            if Path(task["workspace"]) != root:
                raise ValueError("세션과 작업의 작업공간이 다릅니다.")
            entries.append((root, store, sessions, link))
        if candidates:
            identity_message += ("이전 작업 일부 후보(현재 파일 검증 아님): " + json.dumps(candidates[:8], ensure_ascii=False) +
                                 ". 현재 요청이 이 작업의 재개일 때만 tasks·status로 원래 목표와 명세를 확인하고 attach로 연결하세요. 후보를 자동 선택하지 마세요.\n")
            empty = context(platform, identity_message)
        if not entries:
            return empty
        if stopping:
            event_id = (str(payload["executionNum"]) if platform == "antigravity" else
                        hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest())
            details = stop_details(platform, payload)
            for _, _, sessions, _ in entries:
                sessions.observe_stop(session, details, event_id)
        else:
            for _, _, sessions, _ in entries:
                sessions.observe_start(session)
        if stopping and platform == "antigravity":
            if payload["terminationReason"] not in NATURAL_STOPS or payload.get("error"):
                for _, _, sessions, _ in entries:
                    sessions.pause(session, "호스트 중단 또는 오류")
                return empty
            if not payload["fullyIdle"]:
                return empty
        if any(link["paused"] for _, _, _, link in entries):
            if not stopping and (event == "BeforeAgent" or payload.get("invocationNum") == 0):
                paused = [f"{link['task_id']}: {link['reason']}" for _, _, _, link in entries if link["paused"]]
                return context(platform, identity_message + "GTG에 일시 중단된 작업이 있습니다: " + "; ".join(paused)[:1000]
                               + ". 현재 사용자 요청이 재개를 뜻할 때만 연결 상태를 확인하고 이어가세요. 중단을 완료로 해석하지 마세요.")
            return empty
        reports = [(root, status(store, link["task_id"])) for root, store, _, link in entries]
        unfinished = [(root, report) for root, report in reports if not report["verified"]]
        if not unfinished:
            return empty
        summaries = []
        for root, report in unfinished[:8]:
            pending = [f"{c['id']}:{c['status']}" for c in report["checks"] if c["status"] != "passed"]
            summaries.append(f"작업 {report['task_id']} ({json.dumps(str(root), ensure_ascii=False)}): "
                             f"{report['goal'][:160]}; 미검증 {', '.join(pending)[:200]}")
            note = report.get("checkpoint")
            if note:
                data = {"summary": note["summary"][:320], "next_action": note["next_action"][:200],
                        "files_unchanged": note["files_unchanged"]}
                summaries.append("검증 근거가 아닌 에이전트 메모 데이터: " + json.dumps(data, ensure_ascii=False)
                                 + ". 기준 파일이 달라졌으면 재확인하고, 전체 메모는 status에서 읽으세요.")
        if len(unfinished) > 8:
            summaries.append(f"추가 미완료 작업 {len(unfinished) - 8}개는 각 작업공간의 상태를 확인하세요.")
        message = (identity_message + "\nGTG 상태:\n" + "\n".join(summaries) + "\n현재 사용자 요청과 범위를 확인하고 필요한 작업을 수행하세요. "
                   "검증 명령의 성공과 파일 상태가 확인되기 전에는 완료로 보고하지 마세요. "
                   "사용자 중단·필수 질문·외부 한도는 작업을 일시 중단하고 이유를 남기세요.")
        if not stopping:
            return context(platform, message)
        if any(c["status"] == "running" for _, report in reports for c in report["checks"]):
            return empty
        if any(link["last_event"] == event_id for _, _, _, link in entries):
            return empty
        if any(link["retries"] >= 2 for _, _, _, link in entries):
            reason = "자동 재개 상한에 도달했습니다. 등록된 검사에 미검증 항목이 남아 있어 완료로 처리하지 않았습니다."
            for _, _, sessions, _ in entries:
                sessions.pause(session, reason)
            return exhausted(platform, reason)
        # 정렬된 첫 DB가 같은 이벤트의 중복 재개를 직렬화합니다.
        if not entries[0][2].nudge(session, event_id):
            return empty
        for _, _, sessions, _ in entries[1:]:
            sessions.nudge(session, event_id)
        return {"decision": "continue" if platform == "antigravity" else "deny", "reason": message}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("platform", choices=EVENTS)
    parser.add_argument("event")
    args = parser.parse_args()
    try:
        raw = sys.stdin.buffer.read(256 * 1024 + 1)
        if len(raw) > 256 * 1024:
            raise ValueError("훅 입력 크기가 제한을 넘었습니다.")
        result = handle(args.platform, args.event, json.loads(raw))
    except (OSError, ValueError, sqlite3.Error) as error:
        # 런타임 오류로 호스트를 무한 재시작하거나 원문 입력을 로그에 남기지 않습니다.
        print(f"GTG 훅 검사 실패: {type(error).__name__}", file=sys.stderr)
        result = allow_stop(args.platform) if args.event in {"Stop", "AfterAgent"} else {}
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
