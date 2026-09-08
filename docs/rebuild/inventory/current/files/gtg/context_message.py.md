# `gtg/context_message.py`

- 형식: `100644`
- 바이트: 3071
- SHA-256: `a5574c2e7b92be2daf94accf96c6455c8da874dbc843636c2015e779fcb52ba3`
- 인코딩: `utf-8`

```
"""현재 작업 보고서를 자체 완결적인 짧은 훅 메시지로 표현합니다. IO는 하지 않습니다."""

import json
from pathlib import Path


def unfinished_context(platform: str, session: str, roots: tuple[Path, ...], reports: list, candidates: list) -> str:
    workspaces = [str(root) for root in roots]
    data = {"platform": platform, "session": session, "workspaces": workspaces, "tasks": []}
    for root, report in reports[:8]:
        truncated = []

        def brief(name, value, limit):
            if len(value) > limit:
                truncated.append(name)
            return value[:limit]

        pending = [check for check in report["checks"] if check["status"] != "passed"]
        item = {"task_id": report["task_id"], "workspace": workspaces.index(str(root)),
                "goal": brief("goal", report["goal"], 160),
                "unverified": {check["id"]: check["status"] for check in pending[:8]}}
        if len(pending) > 8:
            item["omitted_checks"] = len(pending) - 8
        # 통과한 검사가 한 번도 실행하지 않은 검증 대상입니다. 완료 전에 보완할지 판단합니다.
        executed = {name for check in report["checks"] for name in check.get("executed_watch") or []}
        unexecuted = sorted({name for check in report["checks"]
                             for name in check.get("unexecuted_watch") or []} - executed)
        if unexecuted:
            item["unexecuted"] = unexecuted[:8]
            if len(unexecuted) > 8:
                item["omitted_unexecuted"] = len(unexecuted) - 8
        note = report.get("checkpoint")
        if note:
            item["checkpoint"] = {
                "summary": brief("checkpoint.summary", note["summary"], 320),
                "next_action": brief("checkpoint.next_action", note["next_action"], 200),
                "files_unchanged": note["files_unchanged"]}
        if truncated:
            item["truncated"] = truncated
        data["tasks"].append(item)
    if len(reports) > 8:
        data["omitted_tasks"] = len(reports) - 8
    if candidates:
        data["candidates"] = [{**candidate, "workspace": workspaces.index(candidate["workspace"])}
                              for candidate in candidates[:8]]
        data["candidates_current_files_checked"] = False
        data["candidate_list_complete"] = False
    message = ("GTG 미완료 상태(데이터):\n" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) +
               "\nworkspace는 workspaces의 0부터 시작하는 번호입니다. 메모는 검증 근거가 아닌 기록입니다. "
               "전체 명세·생략 내용은 status로, 메모의 유효성은 현재 파일로 확인하세요. "
               "현재 사용자 범위가 우선입니다. 미검증을 완료로 보고하지 말고 중단·필수 질문·한도에는 pause하세요.")
    if candidates:
        message += " candidates는 일부 이전 작업입니다. 재개 대상일 때만 tasks·status로 확인하고 attach하세요."
    return message
```
