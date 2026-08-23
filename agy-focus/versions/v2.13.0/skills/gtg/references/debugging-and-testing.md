# 디버깅 및 테스팅 규율 (Debugging & Testing Rules)

이 문서는 GEMINI.md의 디버깅 7단계 원칙과 테스트 작성·유지보수 규율을 원문 그대로 정의합니다.

---

## 12. Debugging Rules

When debugging:

Verify the actual problem before solving it; do not rely on speculation or hypotheses.

1. Reproduce the issue.
2. Locate the smallest failing surface.
3. Read logs and stack traces.
4. Form one hypothesis at a time.
5. Patch the likely cause.
6. Re-run the failing check.
7. Continue until resolved or honestly blocked.

Do not shotgun unrelated changes.

When stuck, report:

* What was tested.
* What failed.
* What was ruled out.
* The next most likely cause.

---

## 17. Testing Rules

Tests should verify behavior, not implementation trivia.

When adding behavior:

* Add or update tests if the repository has a test pattern.
* Prefer targeted tests close to the changed code.
* Cover failure paths for bug fixes.
* Do not delete failing tests to make the suite pass.
* If a test is obsolete, explain why before changing it.

If automated tests are unavailable, perform the most relevant manual verification and say exactly what was checked.
