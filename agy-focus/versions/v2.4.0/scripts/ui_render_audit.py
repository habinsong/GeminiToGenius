"""Browser-side contracts used by verify_ui_render without enlarging its runner."""

from __future__ import annotations

from typing import Any


OVERFLOW_SCRIPT = """(() => {
  const root = document.documentElement;
  const body = document.body;
  const viewport = root.clientWidth;
  const offenders = [];
  for (const element of document.querySelectorAll('body *')) {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    if (style.display === 'none' || style.visibility === 'hidden' || rect.width < 1 || rect.height < 1) continue;
    if (rect.left >= -1 && rect.right <= viewport + 1) continue;
    let scrollContainer = false;
    for (let parent = element.parentElement; parent; parent = parent.parentElement) {
      const overflow = getComputedStyle(parent).overflowX;
      if (overflow === 'auto' || overflow === 'scroll') { scrollContainer = true; break; }
    }
    if (!scrollContainer) offenders.push({
      tag: element.tagName.toLowerCase(), id: element.id || '',
      className: typeof element.className === 'string' ? element.className.slice(0, 80) : '',
      left: Math.round(rect.left * 10) / 10, right: Math.round(rect.right * 10) / 10
    });
    if (offenders.length === 8) break;
  }
  const scrollWidth = Math.max(root.scrollWidth, body ? body.scrollWidth : 0);
  return {viewport, scrollWidth, overflow: scrollWidth > viewport + 1 || offenders.length > 0, offenders};
})()"""

UI_AUDIT_SCRIPT = """(() => {
  const failures = [];
  const visible = element => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
  };
  const labelledBy = element => {
    const ids = (element.getAttribute('aria-labelledby') || '').split(/\\s+/).filter(Boolean);
    return ids.map(id => document.getElementById(id)?.textContent || '').join(' ').trim();
  };
  const accessibleName = element => {
    const explicit = element.getAttribute('aria-label') || labelledBy(element);
    if (explicit.trim()) return explicit.trim();
    if (element.tagName === 'INPUT' && ['submit', 'button', 'reset'].includes((element.type || '').toLowerCase())) {
      return (element.value || '').trim();
    }
    if (element.labels?.length) return Array.from(element.labels).map(label => label.textContent || '').join(' ').trim();
    return (element.textContent || element.getAttribute('alt') || element.getAttribute('title') || '').trim();
  };
  const controls = Array.from(document.querySelectorAll(
    'a[href], button, input, select, textarea, summary, [role="button"]'
  )).filter(element => visible(element) && element.type !== 'hidden');
  const sizedControls = controls.filter(element =>
    ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'SUMMARY'].includes(element.tagName) ||
    element.getAttribute('role') === 'button'
  );
  for (const element of controls) {
    if (!accessibleName(element)) {
      failures.push({type: 'accessible-name', tag: element.tagName.toLowerCase(), id: element.id || ''});
    }
    const rect = element.getBoundingClientRect();
    if (element.tagName !== 'A' && (rect.width < 24 || rect.height < 24)) {
      failures.push({
        type: 'target-size', tag: element.tagName.toLowerCase(), id: element.id || '',
        width: Math.round(rect.width * 10) / 10, height: Math.round(rect.height * 10) / 10
      });
    }
  }
  for (const image of Array.from(document.images).filter(visible)) {
    if (!image.hasAttribute('alt')) failures.push({type: 'image-alt', src: image.currentSrc || image.src || ''});
  }
  if (!document.documentElement.lang.trim()) failures.push({type: 'document-lang'});
  if (!document.title.trim()) failures.push({type: 'document-title'});
  if (!document.querySelector('main, [role="main"]')) failures.push({type: 'main-landmark'});
  if (document.querySelectorAll('h1').length !== 1) failures.push({type: 'single-h1', count: document.querySelectorAll('h1').length});
  return {failures, controlCount: sizedControls.length, focusChecked: 0};
})()"""

KEYBOARD_FOCUS_SCRIPT = """(() => {
  const element = document.activeElement;
  if (!element || element === document.body || element === document.documentElement) return {found: false};
  const style = getComputedStyle(element);
  return {
    found: true,
    tag: element.tagName.toLowerCase(),
    id: element.id || '',
    href: element.getAttribute('href') || '',
    visible: element.matches(':focus-visible') || (
      style.outlineStyle !== 'none' && style.outlineWidth !== '0px'
    ) || style.boxShadow !== 'none'
  };
})()"""

PERFORMANCE_SCRIPT = """(() => {
  const shifts = performance.getEntriesByType('layout-shift').filter(entry => !entry.hadRecentInput);
  const longFrames = performance.getEntriesByType('long-animation-frame');
  return {
    cls: Math.round(shifts.reduce((sum, entry) => sum + entry.value, 0) * 1000) / 1000,
    longAnimationFrames: longFrames.length,
    maxLongAnimationFrame: longFrames.length ? Math.round(Math.max(...longFrames.map(entry => entry.duration))) : 0,
    supportsLongAnimationFrames: PerformanceObserver.supportedEntryTypes?.includes('long-animation-frame') || false
  };
})()"""


def keyboard_focus_audit(client: Any) -> dict:
    client.call(
        "Runtime.evaluate",
        {"expression": "document.body.setAttribute('tabindex', '-1'); document.body.focus();"},
    )
    targets: list[dict] = []
    failures: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for _ in range(64):
        for event_type in ("keyDown", "keyUp"):
            client.call(
                "Input.dispatchKeyEvent",
                {
                    "type": event_type,
                    "key": "Tab",
                    "code": "Tab",
                    "windowsVirtualKeyCode": 9,
                    "nativeVirtualKeyCode": 9,
                },
            )
        result = client.call("Runtime.evaluate", {"expression": KEYBOARD_FOCUS_SCRIPT, "returnByValue": True})
        current = result.get("result", {}).get("value")
        if not isinstance(current, dict) or not current.get("found"):
            break
        identity = (str(current.get("tag", "")), str(current.get("id", "")), str(current.get("href", "")))
        if identity in seen:
            break
        seen.add(identity)
        targets.append(current)
        if not current.get("visible"):
            failures.append(current)
    return {"checked": len(targets), "failures": failures[:8]}
