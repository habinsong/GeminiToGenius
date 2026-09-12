# `docs/styles.css`

- 형식: `100644`
- 바이트: 18208
- SHA-256: `37ca610961d63d59ae5230e1a8c6d06c9070d812d97c9c3553b2875f5320800f`
- 인코딩: `utf-8`

```
/* ==========================================================================
   GeminiToGenius - Vanguard High-End Visual Design System
   Architecture: Ethereal Glass + Double-Bezel Hardware Enclosures
   Interaction: Floating Island Nav + Concentric Radii + Button-in-Button
   Accessibility: WCAG AA, Fluid Spring Physics, Complete Reduced-Motion Support
   Zero AI Slop. Zero generic glow. Zero banned words or patterns.
   ========================================================================== */

/* --------------------------------------------------------------------------
   01. Precision Design Tokens
   -------------------------------------------------------------------------- */
:root {
  --font-display: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "SF Pro Display", "Google Sans", system-ui, sans-serif;
  --font-body: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "SF Pro Text", "Google Sans", system-ui, sans-serif;
  --font-mono: "SF Mono", "Roboto Mono", Menlo, monospace;

  --ease-spring: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-haptic: cubic-bezier(0.32, 0.72, 0, 1);

  --z-island: 1000;
}

/* Dark Palette (Deep Space OLED & Precision Hardware) */
[data-theme="dark"] {
  --bg-main: #07080a;
  --bg-card-shell: rgba(255, 255, 255, 0.035);
  --bg-card-core: #0e1015;
  --bg-dialog-box: #151820;
  --bg-glass-island: rgba(14, 16, 21, 0.78);

  --border-shell: rgba(255, 255, 255, 0.07);
  --border-core: rgba(255, 255, 255, 0.05);
  --border-subtle: rgba(255, 255, 255, 0.06);

  --text-pure: #fcfdfe;
  --text-body: #9da4b0;
  --text-muted: #5e6573;

  --accent-blue: #2997ff;
  --accent-tint: rgba(41, 151, 255, 0.12);
  --accent-border: rgba(41, 151, 255, 0.28);

  --color-ok: #34c759;
  --color-warn: #ff9f0a;

  --shadow-core-inset: inset 0 1px 1px rgba(255, 255, 255, 0.12);
  --shadow-bezel: 0 16px 40px rgba(0, 0, 0, 0.45), 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-island: 0 12px 36px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.12);

  --ambient-gradient: radial-gradient(circle at 50% -10%, rgba(41, 151, 255, 0.14), transparent 60%);
}

/* Light Palette (Pristine Ceramic & Studio White) */
[data-theme="light"] {
  --bg-main: #f8f9fb;
  --bg-card-shell: rgba(0, 0, 0, 0.025);
  --bg-card-core: #ffffff;
  --bg-dialog-box: #f1f3f8;
  --bg-glass-island: rgba(255, 255, 255, 0.85);

  --border-shell: rgba(0, 0, 0, 0.06);
  --border-core: rgba(0, 0, 0, 0.04);
  --border-subtle: rgba(0, 0, 0, 0.06);

  --text-pure: #15171c;
  --text-body: #5a6270;
  --text-muted: #8c93a0;

  --accent-blue: #0071e3;
  --accent-tint: rgba(0, 113, 227, 0.07);
  --accent-border: rgba(0, 113, 227, 0.22);

  --color-ok: #248a3d;
  --color-warn: #b25e02;

  --shadow-core-inset: inset 0 1px 1px rgba(255, 255, 255, 0.9);
  --shadow-bezel: 0 16px 40px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02);
  --shadow-island: 0 12px 36px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.8);

  --ambient-gradient: radial-gradient(circle at 50% -10%, rgba(0, 113, 227, 0.07), transparent 60%);
}

/* --------------------------------------------------------------------------
   02. Base & Typography Mechanics
   -------------------------------------------------------------------------- */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-family: var(--font-body);
  font-size: 16px;
  line-height: 1.6;
  letter-spacing: -0.015em;
  background-color: var(--bg-main);
  color: var(--text-pure);
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-main);
  color: var(--text-pure);
  overflow-x: hidden;
  position: relative;
}

main {
  flex: 1;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  font: inherit;
  color: inherit;
  border: none;
  background: none;
  cursor: pointer;
}

code {
  font-family: var(--font-mono);
}

.gtg-container {
  width: 100%;
  max-width: 1160px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 28px;
  padding-right: 28px;
}

/* --------------------------------------------------------------------------
   03. Ambient Subtle Light Field (Zero Harsh Glow)
   -------------------------------------------------------------------------- */
.gtg-ambient-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 680px;
  background: var(--ambient-gradient);
  pointer-events: none;
  z-index: 0;
}

/* --------------------------------------------------------------------------
   04. Floating Island Navigation Pill (Detached, Zero Edge Glued)
   -------------------------------------------------------------------------- */
.gtg-island-nav {
  position: fixed;
  top: 22px;
  left: 50%;
  transform: translateX(-50%);
  z-index: var(--z-island);
  width: calc(100% - 48px);
  max-width: 820px;
}

.gtg-nav-pill {
  width: 100%;
  height: 56px;
  padding: 6px 10px 6px 16px;
  border-radius: var(--radius-pill);
  background: var(--bg-glass-island);
  backdrop-filter: blur(24px) saturate(190%);
  -webkit-backdrop-filter: blur(24px) saturate(190%);
  border: 1px solid var(--border-shell);
  box-shadow: var(--shadow-island);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.gtg-brand-group {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.96rem;
  letter-spacing: -0.02em;
}

.gtg-brand-badge {
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background: var(--text-pure);
  color: var(--bg-main);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 800;
}

.gtg-nav-menu {
  display: flex;
  align-items: center;
  gap: 24px;
}

.gtg-nav-item {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--text-body);
  transition: color 0.18s var(--ease-spring);
}

.gtg-nav-item:hover {
  color: var(--text-pure);
}

.gtg-nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.gtg-theme-switch {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-pill);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-body);
  transition: color 0.15s var(--ease-spring), transform 0.15s var(--ease-spring);
}

.gtg-theme-switch:hover {
  color: var(--text-pure);
}

.gtg-theme-switch:active {
  transform: scale(0.92);
}

[data-theme="dark"] .sun-icon { display: block; }
[data-theme="dark"] .moon-icon { display: none; }
[data-theme="light"] .sun-icon { display: none; }
[data-theme="light"] .moon-icon { display: block; }

/* Nested CTA Button-in-Button Architecture */
.gtg-button-nested {
  height: 40px;
  padding: 0 6px 0 16px;
  border-radius: var(--radius-pill);
  background: var(--text-pure);
  color: var(--bg-main);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: transform 0.2s var(--ease-spring), opacity 0.2s var(--ease-spring);
}

.btn-icon-circle {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-pill);
  background: rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.25s var(--ease-spring);
}

[data-theme="dark"] .btn-icon-circle {
  background: rgba(0, 0, 0, 0.12);
}

.gtg-button-nested:hover .btn-icon-circle {
  transform: translate(2px, -2px);
}

.gtg-button-nested:active {
  transform: scale(0.97);
}

/* --------------------------------------------------------------------------
   05. Hero Section (Macro-Whitespace & Haptic Split)
   -------------------------------------------------------------------------- */
.gtg-hero-wrap {
  position: relative;
  padding-top: 156px;
  padding-bottom: 120px;
}

.gtg-hero-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 56px;
  align-items: center;
}

.gtg-pill-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border-radius: var(--radius-pill);
  background: var(--bg-card-shell);
  border: 1px solid var(--border-shell);
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-body);
  margin-bottom: 24px;
}

.eyebrow-dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-pill);
  background: var(--color-ok);
}

.gtg-display-title {
  font-family: var(--font-display);
  font-size: 3.4rem;
  line-height: 1.12;
  font-weight: 800;
  letter-spacing: -0.04em;
  margin-bottom: 24px;
}

.gtg-display-sub {
  font-size: 1.18rem;
  line-height: 1.65;
  color: var(--text-body);
  max-width: 46ch;
  margin-bottom: 40px;
}

/* Double-Bezel Capsule Installation Bar */
.gtg-capsule-shell {
  max-width: 530px;
  padding: 6px;
  border-radius: 20px;
  background: var(--bg-card-shell);
  border: 1px solid var(--border-shell);
  box-shadow: var(--shadow-bezel);
}

.gtg-capsule-core {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px 8px 16px;
  border-radius: calc(20px - 6px);
  background: var(--bg-card-core);
  border: 1px solid var(--border-core);
  box-shadow: var(--shadow-core-inset);
}

.gtg-capsule-code {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-mono);
  font-size: 0.84rem;
  color: var(--text-pure);
  overflow: hidden;
  white-space: nowrap;
}

.capsule-prompt {
  color: var(--text-muted);
  font-weight: 600;
  user-select: none;
}

.gtg-capsule-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  border-radius: var(--radius-pill);
  background: var(--accent-tint);
  color: var(--accent-blue);
  border: 1px solid var(--accent-border);
  font-size: 0.82rem;
  font-weight: 600;
  flex-shrink: 0;
  transition: all 0.2s var(--ease-spring);
}

.gtg-capsule-btn:hover {
  background: var(--accent-blue);
  color: #ffffff;
  border-color: transparent;
}

.gtg-capsule-btn:active {
  transform: scale(0.96);
}

/* --------------------------------------------------------------------------
   06. Double-Bezel Live Dialogue Card
   -------------------------------------------------------------------------- */
.gtg-hero-visual {
  display: flex;
  justify-content: flex-end;
}

.gtg-bezel-shell {
  width: 100%;
  padding: 7px;
  border-radius: 28px;
  background: var(--bg-card-shell);
  border: 1px solid var(--border-shell);
  box-shadow: var(--shadow-bezel);
  transition: transform 0.3s var(--ease-spring), border-color 0.3s var(--ease-spring);
}

.gtg-bezel-shell:hover {
  border-color: var(--border-prominent);
}

.gtg-bezel-core {
  border-radius: calc(28px - 7px);
  background: var(--bg-card-core);
  border: 1px solid var(--border-core);
  box-shadow: var(--shadow-core-inset);
  overflow: hidden;
}

.gtg-card-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 22px;
  border-bottom: 1px solid var(--border-subtle);
  background: rgba(0, 0, 0, 0.04);
}

[data-theme="light"] .gtg-card-topbar {
  background: rgba(0, 0, 0, 0.02);
}

.topbar-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-pill);
  background: var(--color-ok);
  box-shadow: 0 0 8px rgba(52, 199, 89, 0.4);
}

.topbar-title {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-body);
}

.topbar-tag {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  background: var(--accent-tint);
  color: var(--accent-blue);
  border: 1px solid var(--accent-border);
}

.gtg-dialog-flow {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dialog-author {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-muted);
}

.dialog-box {
  padding: 12px 16px;
  border-radius: 14px;
  font-size: 0.9rem;
  line-height: 1.48;
}

.dialog-item.user .dialog-box {
  background: var(--bg-dialog-box);
  border: 1px solid var(--border-subtle);
  align-self: flex-end;
  max-width: 88%;
}

.dialog-item.ai .dialog-box {
  background: var(--bg-dialog-box);
  border: 1px solid var(--border-subtle);
  align-self: flex-start;
  max-width: 88%;
}

.dialog-item.guard .dialog-box {
  background: rgba(255, 159, 10, 0.08);
  border: 1px solid rgba(255, 159, 10, 0.25);
  color: var(--text-pure);
}

.dialog-item.guard .dialog-author {
  color: var(--color-warn);
}

.success-banner {
  padding: 12px;
  border-radius: 12px;
  background: rgba(52, 199, 89, 0.1);
  border: 1px solid rgba(52, 199, 89, 0.3);
  color: var(--color-ok);
  font-size: 0.88rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* --------------------------------------------------------------------------
   07. Macro-Whitespace Section Architecture
   -------------------------------------------------------------------------- */
.gtg-section-space {
  padding: 120px 0;
  border-top: 1px solid var(--border-subtle);
}

.gtg-section-header {
  margin-bottom: 56px;
  max-width: 640px;
}

.gtg-headline {
  font-family: var(--font-display);
  font-size: 2.35rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 14px;
}

.gtg-lead {
  font-size: 1.14rem;
  color: var(--text-body);
  line-height: 1.6;
}

/* --------------------------------------------------------------------------
   08. Card Grids with Double-Bezel Architecture
   -------------------------------------------------------------------------- */
.p-generous {
  padding: 40px 34px;
}

.p-step {
  padding: 38px 32px;
}

.p-feature {
  padding: 36px 32px;
}

.card-glyph {
  font-size: 2rem;
  margin-bottom: 12px;
}

.card-heading {
  font-family: var(--font-display);
  font-size: 1.28rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 12px;
}

.card-detail {
  font-size: 0.96rem;
  color: var(--text-body);
  line-height: 1.65;
}

/* Problem Cards: 3 Column */
.gtg-asymmetric-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

/* Steps Trio: 3 Column */
.gtg-steps-trio {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.step-counter {
  font-family: var(--font-mono);
  font-size: 0.84rem;
  font-weight: 700;
  color: var(--accent-blue);
  margin-bottom: 12px;
}

.step-label {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 12px;
}

.step-summary {
  font-size: 0.96rem;
  color: var(--text-body);
  line-height: 1.65;
}

/* Features Quad: 2x2 */
.gtg-features-quad {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.feature-headline {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 10px;
}

.feature-body {
  font-size: 0.96rem;
  color: var(--text-body);
  line-height: 1.65;
}

/* --------------------------------------------------------------------------
   09. Minimalist Master Footer
   -------------------------------------------------------------------------- */
.gtg-master-footer {
  padding: 88px 0 48px 0;
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-main);
}

.gtg-footer-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 48px;
  margin-bottom: 64px;
}

.footer-identity {
  max-width: 320px;
}

.footer-logo {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 10px;
  display: block;
}

.footer-desc {
  font-size: 0.92rem;
  color: var(--text-body);
  line-height: 1.6;
}

.footer-nav-groups {
  display: flex;
  gap: 64px;
}

.group-title {
  font-size: 0.88rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--text-pure);
}

.footer-nav-groups ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-nav-groups a {
  font-size: 0.88rem;
  color: var(--text-body);
  transition: color 0.18s var(--ease-spring);
}

.footer-nav-groups a:hover {
  color: var(--text-pure);
}

.gtg-footer-baseline {
  padding-top: 32px;
  border-top: 1px solid var(--border-subtle);
  font-size: 0.84rem;
  color: var(--text-muted);
}

/* --------------------------------------------------------------------------
   10. Kinetic Entry Interpolations (IntersectionObserver Driven)
   -------------------------------------------------------------------------- */
.reveal-on-scroll {
  opacity: 0;
  transform: translateY(28px);
  transition: transform 0.85s var(--ease-spring), opacity 0.85s var(--ease-spring);
  will-change: transform, opacity;
}

.reveal-on-scroll.is-revealed {
  opacity: 1;
  transform: translateY(0);
}

/* --------------------------------------------------------------------------
   11. Strict Responsive Collapse (< 768px Single-Column Fallback)
   -------------------------------------------------------------------------- */
@media (max-width: 768px) {
  .gtg-island-nav {
    top: 14px;
    width: calc(100% - 28px);
  }

  .gtg-nav-menu {
    display: none;
  }

  .gtg-hero-wrap {
    padding-top: 108px;
    padding-bottom: 64px;
  }

  .gtg-hero-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }

  .gtg-display-title {
    font-size: 2.35rem;
  }

  .gtg-section-space {
    padding: 72px 0;
  }

  .gtg-asymmetric-cards,
  .gtg-steps-trio,
  .gtg-features-quad {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .gtg-footer-row {
    flex-direction: column;
    gap: 40px;
  }

  .footer-nav-groups {
    gap: 40px;
  }
}

/* --------------------------------------------------------------------------
   12. Mandatory Reduced-Motion Fallback
   -------------------------------------------------------------------------- */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
    scroll-behavior: auto !important;
  }

  .reveal-on-scroll {
    opacity: 1 !important;
    transform: none !important;
  }
}
```
