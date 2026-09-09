# `.github/ISSUE_TEMPLATE/bug_report.yml`

- 형식: `100644`
- 바이트: 1023
- SHA-256: `406051895ca7b3926e17f507681f97eec60dbdfa28db67dfa136e91fc949183f`
- 인코딩: `utf-8`

```
name: Bug report
description: Report a reproducible problem with the profile, hook, or skill.
title: "[Bug] "
labels:
  - bug
body:
  - type: markdown
    attributes:
      value: |
        Do not paste tokens, private prompts, private paths, or personal data.
  - type: input
    id: version
    attributes:
      label: Profile version
      placeholder: v1.17.0
    validations:
      required: true
  - type: input
    id: target
    attributes:
      label: Model and app
      placeholder: Gemini 3.6 Flash (High) / Antigravity or Antigravity IDE
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Reproduction steps
      description: List the shortest sequence that reproduces the problem.
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: Actual behavior
    validations:
      required: true
```
