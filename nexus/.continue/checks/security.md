---
name: Security Review
description: Flag hardcoded secrets and missing input validation
---

Review this pull request for security issues. Flag as FAILING if any of these are true:

1. **Hardcoded Secrets** — API keys, tokens, passwords, or secrets directly in source files (not in environment variables). Look for patterns like `sk-`, `pk_live`, `Bearer `, long hex strings assigned to variables.

2. **Missing Input Validation** — New API endpoints that accept user input without validating type, length, or format. Especially: text inputs without max length, file uploads without type/size checks, numeric inputs without range checks.

3. **SQL Injection** — Any SQL queries built with string concatenation or f-strings instead of parameterized queries or ORM methods.

4. **Sensitive Data in Logs** — User emails, passwords, tokens, payment info, or personal data logged to stdout, console.log, or log files.

5. **Missing Auth Checks** — New API routes that return user data or perform actions without requiring authentication. All routes except public landing page endpoints need auth.

6. **File Upload Vulnerabilities** — File upload endpoints that don't validate: file type (whitelist: wav, mp3, m4a only), file size (max 10MB), and don't sanitize filenames.

7. **CORS Misconfiguration** — Allow-origin: * on endpoints that handle authenticated data or mutations.

8. **Path Traversal** — File read/write operations that use user-provided paths without sanitization.

If ALL of the above are clear, respond with:
**PASS** ✅ No security issues found.

If any are found, respond with:
**FAIL** ❌ Security issues found:
- [Issue 1]: [file:line] [description]
- [Issue 2]: [file:line] [description]

Then: "These must be fixed before merging. Create a task for CTO if help is needed."
