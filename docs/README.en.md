<div align="center">

<h1>GeminiToGenius</h1>

<p>A plugin that makes Gemini a little smarter, or at least less dumb.</p>

<p><a href="../README.md">한국어</a> · English</p>

<p><a href="README.md">Documentation</a> · <a href="verification/README.md">Verification & Limits</a> · <a href="../CHANGELOG.md">Changelog</a></p>

<p>GTG 3.1.0 supports Antigravity Desktop and IDE, Antigravity CLI and Gemini CLI. When a task takes more than one turn, the model writes down how it will check the result before it starts, runs those checks as real commands, and reports success only after they pass. The finished task comes with a certificate that lists the commands, their exit codes and fingerprints of the files they checked, so anyone with the workspace can replay it without a separate database.</p>

<p>You do not need slash commands or spec files. Ask the way you normally would.</p>

</div>

## What it does

| Feature | Description |
|---|---|
| Fixed finish conditions | Verification commands are locked once registered, and commands that prove nothing, such as `echo` or `true`, are rejected. |
| Real execution | Registered commands run in your environment. GTG records exit codes, duration and file hashes, and a later change to a watched file invalidates earlier passes. |
| Completion certificate | `certify` puts the claims and the evidence in one file, and `replay` re-runs it to `pass`, `invalid` or `inconclusive`. An inconclusive replay never counts as a pass. |
| Honest gaps | Files that no check executed are listed, and when a runtime cannot be observed GTG says so instead of claiming full coverage. |
| Resumable work | Goals, check results and notes survive restarts, and a new session can attach to an unfinished task. |
| Structure check (3.1) | `structure` blocks empty function bodies, new TODO and FIXME comments, features piled into files over 400 lines and classes growing past 20 methods. It reports single-implementation abstractions, pass-through wrappers and new definitions nobody calls as review signals. |
| Prose check (3.1) | `prose` blocks stock phrases in Korean and English documents and reports overclaims, clustered translationese and choppy or monotone rhythm with line numbers. |
| Lessons (3.1) | When a check exposes a repository-specific mistake, such as a function name the model made up, the model can record a one-line lesson with a file or URL as evidence. The next session sees the latest five at the start of its first turn. |

Hooks never call a model or start test suites on their own. Automatic resumption is capped at two retries by default so it does not burn your quota.

## Target models

The 3.1.0 instructions were written with Gemini 4 Argon (public since 2026-10-13) and Gemini 3.8 Flash (public since 2026-09-02) in mind. Users report that both models, measured against their benchmark scores, invent how a codebase works, call unfinished code done, or break a constraint right after promising to follow it. GTG therefore asks the model to rely on check results and re-opened sources rather than its own account, and, following Google's Gemini prompting guidance, collects the prohibitions at the end of the rule file in concrete terms.

The execution core never branches on model names and does not change the model or thinking level the host chose. Google's documentation sets medium as the default thinking level for both models; the Argon guide recommends high for multi-file software work, while the 3.8 Flash guide recommends medium for complex code and agent tasks and high for hard multi-step reasoning. Gemini 4 Carbon, announced on 2026-10-28, is not generally available yet, so GTG assumes nothing about it. Whether these instructions actually reduce hallucination and overclaiming has not been measured.

## Installation

Requires macOS or Linux, Python 3.10 or later and Git. There are no third-party Python dependencies.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
bash GeminiToGenius/scripts/install.sh
```

The installer looks for host configuration files in your home directory and installs into each host it finds. Restart the host afterwards.

| Host | Installation path |
|---|---|
| Antigravity Desktop & IDE | `~/.gemini/config/plugins/geminitogenius/` |
| Antigravity CLI (`agy`) | `~/.gemini/antigravity-cli/plugins/geminitogenius/` |
| Gemini CLI | `~/.gemini/extensions/geminitogenius/` |

Copying files is not enough for Antigravity CLI, so the installer also runs `agy plugin install`. If `agy` is not on your `PATH`, it skips that step and prints the command to run yourself.

The installer cannot tell a Gemini CLI setup apart from other files in `~/.gemini`, so it does not detect Gemini CLI automatically. Pass `--platform gemini-cli` to install it. This is an installer policy, not a statement about the service.

See [Getting started](product/getting-started.md) for the full setup.

## Verification and results

These results come from earlier releases on real hosts.

On Antigravity 2.12.2 the model registered tasks on its own, ran the checks, produced certificates and replayed them. Changing one line in a verified file broke the replay, and reverting it made the replay pass again. On Antigravity CLI 1.1.28 the package passed the official validator and both lifecycle hooks fired.

We ran four harnesses on the same cases, prompts and graders, 64 runs in total:

| Arm | Auto-graded | Passed | Consistent pass rate |
|---|---|---|---|
| `agy` with GTG (Gemini 3.8 Flash High) | 14 | 14 | 7/7 |
| `agy` without GTG (same model) | 14 | 14 | 7/7 |
| Claude Code (Sonnet 5) | 14 | 12 | 6/7 |
| Codex CLI (gpt-5.6-terra) | 14 | 13 | 6/7 |

**With and without GTG on the same model, the pass rates were identical, so these short tasks show no quality difference.** The model registered a task in only 5 of 16 runs, and in a harder follow-up that required running the code it registered none. Six of the seven auto-graded cases were passed by every arm, which means the suite does not discriminate much. The other two harnesses ran different base models, so the table does not rank the harnesses either.

For 3.1.0, all 411 unit and integration tests pass offline, and the new checks were also tested by deliberately breaking the implementation to confirm the tests catch it. No Gemini model was called. Details and sources are in [3.1.0 verification](verification/3.1.0.md), and what remains unchecked is in [Verification & Limits](verification/README.md).

## Documentation

| Guide | Description |
|---|---|
| [Getting started](product/getting-started.md) | Setup, host selection and uninstalling |
| [How it works](product/how-it-works.md) | From a request to registration, checks and certificates |
| [CLI reference](reference/cli.md) | `run.py` subcommands and exit codes |
| [Completion certificate](reference/certificate.md) | Certificate format and `replay` verdicts |
| [Architecture](architecture/overview.md) | The boundary between host hooks and the core |
| [All documentation](README.md) | Full index |

Detailed design and developer documents are written in Korean.

## Development

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
python3 scripts/catalog.py --check
```

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## License

MIT License. See [LICENSE](../LICENSE). GTG is not affiliated with or endorsed by Google, Antigravity or Gemini; product names appear only to describe compatibility.
