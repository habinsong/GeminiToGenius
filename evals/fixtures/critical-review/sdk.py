"""가상 SDK의 전체 공개 표면입니다. PNG 시그니처만 확인합니다."""

__all__ = ["is_png"]


def is_png(data: bytes) -> bool:
    return data.startswith(b"\x89PNG\r\n\x1a\n")
