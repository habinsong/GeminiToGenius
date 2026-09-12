<div align="center">

<h1>GeminiToGenius</h1>

<p>A plugin that makes Gemini a little smarter—or at least less dumb.</p>

<p><a href="../README.md">한국어</a> · English</p>

<p><a href="README.md">Documentation</a> · <a href="verification/README.md">Verification & Limits</a> · <a href="../CHANGELOG.md">Changelog</a></p>

<p>GTG is a reliability plugin for Antigravity and Gemini CLI. When a task spans multiple turns, the model registers explicit completion criteria first, executes them as actual shell commands, and only claims success once they pass. Each completed task produces a tamper-evident certificate containing the executed commands, exit codes, and cryptographic fingerprints of all inspected files. Anyone with access to the workspace can independently replay and verify the certificate without an external database.</p>

<p>No custom slash commands or rigid spec files are required. Simply prompt naturally.</p>

</div>

## What it does

| Feature | Description |
|---|---|
| Immutable finish conditions | Once registered, verification commands are locked. No-op commands like `echo` or `true` are rejected upfront. |
| Real execution | Registered commands run directly in your environment. Exit codes, wall-clock duration, and file hashes are logged. If a watched file changes later, prior passes are invalidated. |
| Completion certificate | Binds claims and concrete execution proof into a single document. `replay` verifies outcomes without requiring a state database, evaluating strictly to `pass`, `invalid`, or `inconclusive`. Inconclusive runs never pass. |
| Transparent unverified scope | Files not executed during verification are explicitly reported. When an unobservable language runtime is in scope, GTG discloses the gap rather than claiming full verification. |
| Cross-session continuity | Goals, verification records, and scratchpad notes persist across restarts. New sessions seamlessly attach to ongoing tasks. |
| Crash-resilient recovery | Task execution status relies on file locks rather than ephemeral PIDs. Sudden reboots or process terminations will not leave tasks hung. |

Platform hooks never invoke background models or trigger unauthorized test suites on their own. Auto-resume operates under a strict default budget of two retries to protect your token quota.

## Installation

Requires macOS or Linux, Python 3.10+, and Git. Zero third-party Python dependencies.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
bash GeminiToGenius/scripts/install.sh
```

The installer detects existing host configurations on your machine and installs into every discovered environment. Restart your host application after installation.

| Host | Installation path |
|---|---|
| Antigravity Desktop & IDE | `~/.gemini/config/plugins/geminitogenius/` |
| Antigravity CLI (`agy`) | `~/.gemini/antigravity-cli/plugins/geminitogenius/` |
| Gemini CLI | `~/.gemini/extensions/geminitogenius/` |

For Antigravity CLI, copying files alone does not activate the plugin; the installer automatically invokes `agy plugin install`. If `agy` is not found on `$PATH`, the installer skips this step gracefully and prints the command to run manually.

Gemini CLI discontinued individual account endpoints on 2026-06-18, so auto-detection is disabled for it. Pass `--platform gemini-cli` to install explicitly.

See [Getting started](product/getting-started.md) for full setup instructions.

## Verification & Real-World Results

All findings reflect tests run on real host environments.

On Antigravity 2.12.2, the model autonomously registered tasks, verified them, generated certificates, and replayed them. Modifying a single line in a verified file broke certificate replay as expected; reverting the change restored verification. On Antigravity CLI 1.1.28, the package passed official validation and emitted both lifecycle hooks.

We evaluated four harnesses across 64 benchmark trials with identical test cases, prompts, and grading logic:

| Arm | Auto-graded | Passed | Consistent pass rate |
|---|---|---|---|
| `agy` with GTG (Gemini 3.8 Flash High) | 14 | 14 | 7/7 |
| `agy` without GTG (same model) | 14 | 14 | 7/7 |
| Claude Code (Sonnet 5) | 14 | 12 | 6/7 |
| Codex CLI (gpt-5.6-terra) | 14 | 13 | 6/7 |

**With GTG enabled vs. disabled on the same model, pass rates were identical. On quick, single-turn tasks, GTG provides no noticeable delta in finished artifacts.** In 11 of 16 runs, the model chose not to register tasks—which was the intended behavior. Attaching full verification conditions to trivial two-file edits adds unnecessary overhead.

Where GTG proves its value is multi-turn tasks: across all five multi-step registrations, it executed checks and minted verifiable certificates. In session resumption tests, it consistently linked parent tasks and tracked progress notes.

Because Claude Code and Codex ran different foundation models, these benchmarks reflect harness characteristics rather than model superiority. Unmeasured dimensions are documented in [what is not checked](verification/README.md).

## Documentation

| Guide | Description |
|---|---|
| [Getting started](product/getting-started.md) | Setup, host configuration, and uninstallation |
| [How it works](product/how-it-works.md) | Execution lifecycle from prompt to registration and certification |
| [CLI Reference](reference/cli.md) | Supported `run.py` subcommands and exit codes |
| [Completion Certificate](reference/certificate.md) | Certificate specification and `replay` validation states |
| [Architecture](architecture/overview.md) | Boundary design between host hooks and core execution |
| [All Documentation](README.md) | Complete documentation index |

Detailed architectural and developer docs are maintained in Korean.

## Development

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
python3 scripts/catalog.py --check
```

The test suite covers 317 unit and integration tests. Historical research includes 94 primary sources, with repository snapshot integrity tracked in the inventory. Review [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## License

MIT License. See [LICENSE](../LICENSE). Not affiliated with or endorsed by Google, Antigravity, or Gemini. Product names are referenced strictly for compatibility context.
