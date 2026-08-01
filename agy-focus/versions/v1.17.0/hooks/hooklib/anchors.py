from __future__ import annotations

import re

from .config import (
    ARCHITECTURE_TRIGGER_RE,
    CHANGE_TRIGGER_RE,
    COPY_TRIGGER_RE,
    DESIGN_TRIGGER_RE,
)
from .payloads import prompt_matches
from .state import read_state


def one_time_anchor_needed(payload: dict, state_key: str, pattern) -> bool:
    conversation_id = str(payload.get("conversationId", ""))
    if not conversation_id or not prompt_matches(payload, pattern):
        return False
    return read_state().get(state_key) != conversation_id


def one_time_anchor_response(
    payload: dict,
    state_key: str,
    pattern,
    message: str,
) -> tuple[dict, dict | None]:
    if not one_time_anchor_needed(payload, state_key, pattern):
        return {}, None
    return (
        {"injectSteps": [{"ephemeralMessage": message}]},
        {state_key: str(payload.get("conversationId", ""))},
    )


def scope_intake_response(payload: dict) -> tuple[dict, dict | None]:
    return one_time_anchor_response(
        payload,
        "scopeIntakeConversationId",
        CHANGE_TRIGGER_RE,
        "변경 작업: README·계획서·검색 결과부터 읽고 판단하지 마세요. 전체 파일 지도를 만든 뒤 저장소 지침과 빌드·실행 진입점을 확인하고, 영향 범위의 실제 소스·호출·데이터·상태 경계와 테스트를 파일별로 처음부터 끝까지 읽으세요. 설정·자산·문서는 마지막에 대조하세요. 목록·rg·일부 줄·요약은 전체 파일을 읽은 증거가 아니며 문서 설명은 실제 코드 동작의 증거가 아닙니다. 관련 없는 기능·과거 버전·생성물을 전부 주입해 집중력을 흩뜨리지 마세요.",
    )


def architecture_context_response(payload: dict) -> tuple[dict, dict | None]:
    return one_time_anchor_response(
        payload,
        "architectureContextConversationId",
        ARCHITECTURE_TRIGGER_RE,
        "구현 작업: 대상 파일·타입의 LOC와 현재 책임, 상태 소유자, 입출력, 부작용을 확인한 뒤 코드를 추가하세요. UI·도메인 정책·API·DB·파일 IO·영속성·외부 프로세스·표현을 한 객체에 누적하지 말고 별개 변경 이유는 가장 작은 응집 단위로 먼저 분리하세요. LOC만 줄이는 wrapper·빈 계층·불필요한 repository·microservice는 만들지 말고 기존 구조와 공개 계약을 지키면서 변경 뒤 주요 파일의 책임과 검증을 다시 확인하세요.",
    )


def design_context_response(payload: dict) -> tuple[dict, dict | None]:
    return one_time_anchor_response(
        payload,
        "designContextConversationId",
        DESIGN_TRIGGER_RE,
        "UI 작업: 구현 전에 실제 사용자·주 행동·데이터·전체 상태·기존 화면과 디자인 시스템을 확인하세요. 제품 근거 없이 중앙 히어로+그라데이션 제목+목업+동일 카드 3개, 카드 중첩, 같은 radius·간격, pill·glow·blob·유리 효과, Inter 기본값, 요술봉·별·추상 아이콘, 가짜 지표·후기·AI 배지·3D 장식을 만들지 마세요. 의미 구조와 위계를 먼저 만들고 320 CSS px·키보드 focus·색상 외 상태·감속 설정·실제 렌더링까지 확인하세요.",
    )


def copy_context_response(payload: dict) -> tuple[dict, dict | None]:
    return one_time_anchor_response(
        payload,
        "copyContextConversationId",
        COPY_TRIGGER_RE,
        "카피 작업: 제목은 화면의 일을, 버튼은 사용자의 동작을, 오류는 문제와 복구 방법을 직접 말하세요. 한 문장에는 한 가지 정보만 두고 중요한 말을 앞에 두세요. 추상 슬로건·AI 자기소개·서술형 분위기 문단·과장된 환영 문구·가짜 수치·사용자 탓·농담을 넣지 마세요.",
    )


def visual_evidence_response(payload: dict) -> tuple[dict, dict | None]:
    quality_pattern = re.compile(
        f"(?:{DESIGN_TRIGGER_RE.pattern}|{COPY_TRIGGER_RE.pattern})", re.IGNORECASE
    )
    return one_time_anchor_response(
        payload,
        "uiEvidenceConversationId",
        quality_pattern,
        "UI·카피 결과: 첫 생성물을 승인하지 말고 실제 화면을 좁은·중간·넓은 폭에서 조작하세요. 제품 고유 작업과 데이터가 위계에 반영되는지, loading·empty·error·success·disabled·focus·selected 상태가 있는지, 키보드·대비·타깃 크기·감속 설정·layout shift를 확인하세요. 화면을 보지 않았거나 성능을 재지 않았다면 통과와 수치를 주장하지 마세요.",
    )
