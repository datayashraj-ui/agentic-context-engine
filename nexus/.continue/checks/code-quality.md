---
name: Code Quality
description: Enforce code quality standards
---

Review this pull request for code quality. Flag as FAILING if any of these are true:

1. **Long Functions** — Functions or methods longer than 50 lines without a clear reason (e.g., not a data structure definition, not a mapping/config object). Long functions should be decomposed.

2. **Missing Error Handling** — async/await operations without try/catch, or Promise chains without .catch(). API calls, database operations, and file I/O must handle errors explicitly.

3. **No Tests for New Functionality** — New functions, API endpoints, or services added without corresponding test files. Test files should be in the same location as the source (`*.test.ts`, `*.spec.py`, etc.).

4. **Unused Code** — Imports that are never used, variables declared but never read, functions defined but never called. These should be removed.

5. **Missing TypeScript Types** — TypeScript files using `any` type without a comment justifying why `any` is necessary. All function parameters and return types should be explicitly typed.

6. **Console Statements** — `console.log()`, `console.debug()`, `print()` statements left in production code (not test files). Use proper logging (Python: `logging`, TypeScript: structured logger).

7. **Hardcoded Values** — Configuration values (timeouts, limits, URLs, model names) hardcoded in business logic instead of constants or environment variables.

If ALL of the above are clear, respond with:
**PASS** ✅ Code quality looks good.

If any are found, respond with:
**FAIL** ❌ Code quality issues:
- [Issue 1]: [file:line] [description + how to fix]
- [Issue 2]: [file:line] [description + how to fix]
