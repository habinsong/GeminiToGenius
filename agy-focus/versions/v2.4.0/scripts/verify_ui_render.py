#!/usr/bin/env python3
"""Render a page with installed Chrome and audit narrow, medium, and wide UI contracts."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

from ui_render_audit import OVERFLOW_SCRIPT, PERFORMANCE_SCRIPT, UI_AUDIT_SCRIPT, keyboard_focus_audit


VIEWPORTS = ((320, 800, "mobile"), (768, 900, "medium"), (1280, 900, "desktop"))
CHROME_CANDIDATES = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
)


def chrome_path(explicit: str | None) -> Path:
    candidates = [Path(explicit).expanduser()] if explicit else []
    candidates.extend(CHROME_CANDIDATES)
    for name in ("google-chrome", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError("Google Chrome or Chromium was not found")


def target_url(value: str) -> str:
    if re.match(r"^https?://", value, re.IGNORECASE):
        return value
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"target page not found: {path}")
    return path.as_uri()


def receive_exact(stream: socket.socket, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = stream.recv(remaining)
        if not chunk:
            raise ConnectionError("Chrome DevTools connection closed")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


class DevTools:
    def __init__(self, websocket_url: str) -> None:
        parsed = urllib.parse.urlparse(websocket_url)
        self.stream = socket.create_connection(
            (parsed.hostname or "127.0.0.1", parsed.port or 80), timeout=10
        )
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            f"GET {parsed.path} HTTP/1.1\r\nHost: {parsed.netloc}\r\n"
            f"Upgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.stream.sendall(request.encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response:
            response += receive_exact(self.stream, 1)
        if b" 101 " not in response.split(b"\r\n", 1)[0]:
            raise ConnectionError(f"Chrome DevTools WebSocket rejected connection: {response[:160]!r}")
        self.next_id = 0

    def send_frame(self, payload: bytes) -> None:
        mask = os.urandom(4)
        size = len(payload)
        header = bytearray([0x81])
        if size < 126:
            header.append(0x80 | size)
        elif size < 65536:
            header.extend([0xFE])
            header.extend(struct.pack("!H", size))
        else:
            header.extend([0xFF])
            header.extend(struct.pack("!Q", size))
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self.stream.sendall(bytes(header) + mask + masked)

    def receive_frame(self) -> dict:
        first, second = receive_exact(self.stream, 2)
        opcode = first & 0x0F
        size = second & 0x7F
        if size == 126:
            size = struct.unpack("!H", receive_exact(self.stream, 2))[0]
        elif size == 127:
            size = struct.unpack("!Q", receive_exact(self.stream, 8))[0]
        mask = receive_exact(self.stream, 4) if second & 0x80 else b""
        payload = receive_exact(self.stream, size)
        if mask:
            payload = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        if opcode == 0x9:
            self.stream.sendall(bytes([0x8A, len(payload)]) + payload)
            return self.receive_frame()
        if opcode != 0x1:
            return self.receive_frame()
        return json.loads(payload.decode("utf-8"))

    def call(self, method: str, params: dict | None = None) -> dict:
        self.next_id += 1
        request_id = self.next_id
        self.send_frame(json.dumps({"id": request_id, "method": method, "params": params or {}}).encode("utf-8"))
        while True:
            message = self.receive_frame()
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise RuntimeError(f"Chrome DevTools {method}: {message['error']}")
            return message.get("result", {})

    def close(self) -> None:
        self.stream.close()


def wait_for_debug_port(profile: Path) -> int:
    marker = profile / "DevToolsActivePort"
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        try:
            return int(marker.read_text(encoding="utf-8").splitlines()[0])
        except (OSError, ValueError, IndexError):
            time.sleep(0.05)
    raise RuntimeError("Chrome DevTools port did not become ready")


def page_websocket(port: int) -> str:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5) as response:
        targets = json.load(response)
    for target in targets:
        if target.get("type") == "page" and target.get("webSocketDebuggerUrl"):
            return str(target["webSocketDebuggerUrl"])
    raise RuntimeError("Chrome DevTools page target was not found")


def wait_for_page(client: DevTools) -> None:
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        result = client.call("Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True})
        if result.get("result", {}).get("value") == "complete":
            return
        time.sleep(0.05)
    raise RuntimeError("page load did not complete")


def evaluate(client: DevTools, expression: str) -> dict:
    result = client.call("Runtime.evaluate", {"expression": expression, "returnByValue": True})
    value = result.get("result", {}).get("value")
    if not isinstance(value, dict):
        raise RuntimeError("Chrome did not return UI audit metrics")
    return value


def render_viewport(client: DevTools, url: str, output_dir: Path, width: int, height: int, label: str) -> dict:
    client.call(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False, "screenWidth": width, "screenHeight": height},
    )
    client.call("Page.navigate", {"url": url})
    wait_for_page(client)
    time.sleep(0.1)
    metrics = evaluate(client, OVERFLOW_SCRIPT)
    audit = evaluate(client, UI_AUDIT_SCRIPT)
    performance = evaluate(client, PERFORMANCE_SCRIPT)
    screenshot = output_dir / f"screenshot_{label}.png"
    captured = client.call("Page.captureScreenshot", {"format": "png", "fromSurface": True})
    screenshot.write_bytes(base64.b64decode(captured["data"]))
    focus = keyboard_focus_audit(client)
    if focus["failures"]:
        audit["failures"].append({"type": "visible-focus", "controls": focus["failures"]})
    audit["focusChecked"] = focus["checked"]
    metrics.update({"width": width, "height": height, "screenshot": str(screenshot), "audit": audit, "performance": performance})
    return metrics


def verify(target: str, output_dir: Path, chrome: Path) -> dict:
    url = target_url(target)
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gtg-chrome-") as temporary:
        profile = Path(temporary)
        process = subprocess.Popen(
            [str(chrome), "--headless", "--disable-gpu", "--disable-background-networking",
             "--no-first-run", "--remote-allow-origins=*", "--remote-debugging-port=0",
             f"--user-data-dir={profile}", "about:blank"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        client: DevTools | None = None
        try:
            client = DevTools(page_websocket(wait_for_debug_port(profile)))
            client.call("Page.enable")
            viewports = [render_viewport(client, url, output_dir, width, height, label) for width, height, label in VIEWPORTS]
        finally:
            if client:
                client.close()
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
    return {"ok": not any(item["overflow"] or item["audit"].get("failures") for item in viewports), "viewports": viewports}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="local HTML path or HTTP(S) URL")
    parser.add_argument("--output-dir", default=".", help="screenshot output directory")
    parser.add_argument("--chrome", help="Chrome or Chromium executable")
    args = parser.parse_args()
    try:
        result = verify(args.target, Path(args.output_dir).expanduser().resolve(), chrome_path(args.chrome))
    except (ConnectionError, FileNotFoundError, json.JSONDecodeError, KeyError, OSError, RuntimeError) as error:
        result = {"ok": False, "error": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
