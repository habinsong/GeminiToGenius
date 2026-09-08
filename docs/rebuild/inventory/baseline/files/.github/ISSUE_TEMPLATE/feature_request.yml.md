# `.github/ISSUE_TEMPLATE/feature_request.yml`

- 형식: `100644`
- 바이트: 725
- SHA-256: `d69cd825cf4fe7f148ae3700af8f5c968b566755212020bc6c8bcb57b05bf446`
- 인코딩: `utf-8`

```
name: Feature request
description: Propose a focused improvement to the profile or documentation.
title: "[Feature] "
labels:
  - enhancement
body:
  - type: markdown
    attributes:
      value: |
        Use Discussions for early ideas. Use this form for a concrete, scoped proposal.
  - type: textarea
    id: problem
    attributes:
      label: Problem
      description: What is difficult, missing, or misleading today?
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: Proposal
      description: Describe the smallest useful change.
    validations:
      required: true
  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives considered
```
