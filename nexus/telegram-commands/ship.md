---
name: Ship / Deploy
triggers:
  - "ship"
  - "ship it"
  - "deploy"
  - "push to prod"
  - "go live"
  - "launch"
---

When founder says "ship" or "deploy":

1. Check what's ready to deploy:
   - Query GitHub for PRs merged to main since last deployment
   - If nothing new: respond "Nothing new to deploy since [last deploy date]. Want me to force a redeploy anyway?"

2. Run Continue CLI checks on latest code:
   ```
   continue check --checks .continue/checks/ --branch main
   ```
   - security.md check
   - code-quality.md check
   - architecture.md check

3. If Continue checks fail:
   - List what failed (in plain language)
   - Ask: "These checks failed: [list]. Reply 'fix it' to have CTO address them, or 'ship anyway' if you want to override."
   - Do NOT deploy without approval if checks fail

4. If Continue checks pass — run security scan:
   ```
   semgrep scan --config auto .
   trufflehog git --only-verified .
   trivy fs . --severity HIGH,CRITICAL
   ```

5. If security scan fails:
   - NEVER auto-override security failures
   - Respond: "🔴 Security issue found: [description]. Not deploying until fixed. CTO is on it."
   - Create Beads task for CTO to fix

6. If all checks pass — trigger Coolify deployment:
   ```
   curl -X POST "$COOLIFY_WEBHOOK_URL" -H "Authorization: Bearer $COOLIFY_TOKEN"
   ```

7. Monitor deployment (poll Coolify status for up to 5 minutes)

8. On successful deployment:
   > Shipped! 🚀 Voice Lab is live at voicelab.yourdomain.com
   > All checks passed. Deploy took 2m 34s.

9. On deployment failure:
   > Deploy failed at the Docker build step. Error: [error].
   > CTO is investigating. I'll update you when it's fixed.

## Force Ship (override checks)

If founder replies "ship anyway" or "override checks":
- Log the override in docs/DECISIONS.md with reason
- Deploy via Coolify
- Add note: "Deployed with override at founder's request"

This should be rare. Only for true emergencies.
