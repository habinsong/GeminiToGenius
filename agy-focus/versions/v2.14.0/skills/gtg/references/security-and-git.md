# 보안 및 Git 안전 규칙 (Security & Git Rules)

이 문서는 GEMINI.md의 보안 및 비밀 보호 규칙과 Git 조작 안전 수칙을 원문 그대로 정의합니다.

---

## 13. Git Rules

* Never commit unless explicitly asked.
* Never force-push unless explicitly asked.
* Never rewrite history unless explicitly asked.
* Never discard user changes.
* Leave unrelated modified files alone.

When asked to commit:

```bash
git status --short
git diff
git add <specific-files>
git commit -m "<clear message>"
```

Good commit messages:

* fix: prevent settings panel overflow
* feat: add model routing selector
* docs: update audio pipeline plan
* refactor: simplify dashboard navigation state

---

## 14. Security Rules

Never read, print, modify, or exfiltrate secrets.

Treat these as sensitive:

```text
.env
.env.*
*.pem
*.key
id_rsa
id_ed25519
~/.ssh/**
~/.aws/**
~/.config/gh/**
~/.kube/**
```

Do not run:

```bash
sudo *
rm -rf /
rm -rf ~
chmod -R 777 *
curl * | sh
wget * | sh
```

Before adding a dependency:

1. Check if the project already has an equivalent.
2. Prefer standard library or existing utilities.
3. Explain why the dependency is necessary.
4. Avoid large dependency changes unless requested.
