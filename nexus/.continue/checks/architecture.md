---
name: Architecture Compliance
description: Ensure architecture standards are followed
---

Review this pull request for architecture compliance. Flag as FAILING if any of these are true:

1. **Direct Database Calls** — Database queries made outside of InsForge SDK or the established db/ layer. All database access must go through the service layer, not directly from route handlers or components.

2. **Hardcoded URLs** — URLs pointing to specific environments (localhost, staging.domain.com, api.domain.com) hardcoded in source files instead of using environment variables or config constants.

3. **Secrets Not in Env Vars** — API keys, connection strings, tokens, or passwords that are not read from environment variables. Every secret must come from `process.env` (TypeScript) or `os.environ` (Python).

4. **Unjustified Dependencies** — New npm packages or Python packages added to package.json or pyproject.toml without a comment in the PR description explaining why the dependency is needed and what alternatives were considered. This prevents dependency bloat.

5. **Wrong Directory Placement** — Files placed in incorrect directories per project structure:
   - React components → `frontend/components/`
   - API routes → `backend/routes/`
   - Business logic → `backend/services/`
   - Database models → `backend/models/`
   - Kaggle notebooks → `kaggle-notebooks/`
   - Agent personas → `agents/`
   - Telegram skills → `telegram-commands/`

6. **Frontend-Backend Coupling** — Frontend components making direct database calls, or backend services containing HTML/CSS rendering logic.

7. **Breaking API Contract** — Changes to existing API endpoint signatures (URL, method, request body, response format) without versioning. The ElevenLabs-compatible endpoints must maintain their exact format.

If ALL of the above are clear, respond with:
**PASS** ✅ Architecture looks correct.

If any are found, respond with:
**FAIL** ❌ Architecture issues:
- [Issue 1]: [file:line] [description + correct approach]
- [Issue 2]: [file:line] [description + correct approach]
