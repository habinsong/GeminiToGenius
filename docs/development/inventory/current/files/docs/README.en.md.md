# `docs/README.en.md`

- 형식: `100644`
- 바이트: 6409
- SHA-256: `18f49e6b36e9f7bb0804bb7052c9f038c006c60cb3ee65b1981c520de220650b`
- 인코딩: `utf-8`

````
<div align="center">

<h1>GeminiToGenius</h1>

<p>A local harness that makes Gemini verify its own work before it says it is done.</p>

<p><a href="../README.md">한국어</a> · English</p>

<p><a href="README.md">Documentation</a> · <a href="verification/README.md">What is checked and what is not</a> · <a href="../CHANGELOG.md">Changelog</a></p>

<p>GTG is a plugin for Antigravity and Gemini CLI. When a request looks like it will take more than one turn, the model first pins down what counts as finished, runs those conditions as real commands, and only then reports completion. The report comes with a certificate that ties the claim to the commands it ran, their exit codes, and fingerprints of the files under test. Anyone holding that file can check it again.</p>

<p>No slash commands. No spec files to fill in. Ask the way you normally would.</p>

</div>

## Why this exists

"I fixed it" and "it is fixed" are different things. Agents report completion without running the tests, and when they say they ran them there is no way for you to tell.

GTG 2.x handled this with prompts. There was no executable that dealt with goals or verification results, and the structure check accepted an empty hook configuration as valid. 3.0.0 removed all of that and rebuilt it around a Python execution core.

The idea is one thing. **Pin the finish conditions first, run them for real, and leave the run in a form someone else can reproduce.** The conditions cannot be moved somewhere easier afterwards, and there is no way to mark an unrun check as passed.

## What it does

| | |
|---|---|
| Fixed finish conditions | Once registered, the verification commands cannot change. Commands like `echo` or `true` are rejected at registration. |
| Real execution | The registered command runs as written. Exit code, duration, and file hashes are recorded. If a watched file changes, the earlier success is void. |
| Completion certificate | Claim and evidence in one file. `replay` reproduces it without the state database. The verdict is `pass`, `invalid`, or `inconclusive`, and inconclusive is never reported as a pass. |
| Unverified scope | Files a passing check never executed are reported as they are. When a language it cannot observe is in scope, it does not claim anything about execution and says what blocked the judgment instead. |
| Work across sessions | Goals, check results, and notes survive a disconnect. A new session attaches to the same task. |
| Interrupted runs | Whether a check is still running is decided by a file lock, not a PID. A reboot or a hard kill does not leave the task stuck. |

Hooks never call a model or run tests on their own. Automatic resume spends your quota, so the default is two.

## Install

macOS or Linux, Python 3.10 or later, and Git. No third-party Python packages.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
bash GeminiToGenius/scripts/install.sh
```

The installer looks for configuration files the hosts wrote themselves and installs into every host it finds. Restart the host afterwards.

| Host | Install path |
|---|---|
| Antigravity desktop and IDE | `~/.gemini/config/plugins/geminitogenius/` |
| Antigravity CLI (`agy`) | `~/.gemini/antigravity-cli/plugins/geminitogenius/` |
| Gemini CLI | `~/.gemini/extensions/geminitogenius/` |

Antigravity CLI does not read a plugin just because the files sit at that path. The installer runs `agy plugin install` as well. If `agy` is missing, the install is not treated as a failure and the command you need is printed instead.

Gemini CLI stopped serving individual accounts on 2026-06-18, so it is not auto-detected. It installs only when you pass `--platform gemini-cli`.

More in [Getting started](product/getting-started.md).

## What has been checked

Only results from real hosts.

On Antigravity 2.12.2 the model registered a task, verified it, produced a certificate, and replayed it on its own. Changing one line in a file under test broke the reproduction; restoring it made the reproduction work again. On Antigravity CLI 1.1.28 the official validator accepted the package and both hooks fired.

Four harnesses ran 64 trials on the same cases, the same prompts, and the same grader.

| Arm | Auto-graded | Passed | Passed every time |
|---|---|---|---|
| `agy` with GTG (Gemini 3.8 Flash High) | 14 | 14 | 7/7 |
| `agy` without GTG (same model) | 14 | 14 | 7/7 |
| Claude Code (Sonnet 5) | 14 | 12 | 6/7 |
| Codex CLI (gpt-5.6-terra) | 14 | 13 | 6/7 |

**With GTG on and off against the same model the results are identical. On short tasks GTG showed no advantage in the finished artifact.** The model registered a task in 5 of 16 trials, and for those tasks not registering was the right call. Attaching finish conditions and a certificate to a two-file fix only adds cost.

All five registrations ran their checks and produced certificates. On the case that resumes a previous session's work it registered every time, linked two tasks, and left a note. Work that does not finish in one turn is where GTG earns its place.

Claude Code and Codex ran different models, so this table cannot rank the products. What was not measured is listed in [what is not checked](verification/README.md).

## Documentation

| Document | Read it when |
|---|---|
| [Getting started](product/getting-started.md) | You want to install it and try it |
| [How it works](product/how-it-works.md) | You want the path from one request to registration, verification, and certificate |
| [Commands](reference/cli.md) | You need what `run.py` accepts and its exit codes |
| [Completion certificate](reference/certificate.md) | You need the certificate format and the `replay` verdicts |
| [Architecture](architecture/overview.md) | You want the boundary between the hooks and the execution core |
| [All documentation](README.md) | Anything not above |

Documentation below the top level is written in Korean.

## Development

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
python3 scripts/catalog.py --check
```

317 tests. The research ledger holds 94 sources, and the full text of every implemented file is kept under the inventory. Working rules are in [CONTRIBUTING.md](../CONTRIBUTING.md).

## License

MIT. See [LICENSE](../LICENSE). Not affiliated with or sponsored by Google, Antigravity, or Gemini. Product names are used only to point at what this works with.
````
