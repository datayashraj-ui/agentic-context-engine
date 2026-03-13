---
name: Status Check
triggers:
  - "status"
  - "what's happening"
  - "whats happening"
  - "how's it going"
  - "update"
---

When founder sends any of the trigger phrases:

1. Query Beads API for tasks grouped by status:
   - Count active (in-progress) tasks
   - Count completed tasks today
   - Count blocked tasks
   - List any BLOCKED tasks with brief descriptions

2. Check ZeroClaw daemon health via Docker:
   - List all agent daemons that are running
   - Note any daemons that are stopped/crashed

3. Query Stripe for revenue:
   - Today's revenue
   - Weekly revenue
   - MRR if available

4. Check GlitchTip for unresolved errors:
   - Count of errors in last 24 hours
   - Any CRITICAL errors (mention specifically)

5. Format as conversational Telegram message (under 150 words):
   - Lead with overall health (🟢 all good / 🟡 some issues / 🔴 problems)
   - Quick numbers: tasks, revenue, errors
   - Call out any blockers or issues specifically
   - End with what's happening right now

## Example Response

> Hey Yash! Everything's running smooth. 🟢
>
> **Today:** 3 tasks done, 2 in progress (landing page + TTS API). No blockers.
>
> **Revenue:** $0 this week (pre-launch), $0 MRR. First paying customer coming soon!
>
> **Agents:** All 9 running. Sales scraped 40 leads overnight, queued outreach for 9 AM.
>
> **Errors:** 2 minor warnings in GlitchTip (both non-critical, logged).
>
> CTO is mid-way through the TTS endpoint — estimates done by 6 PM.

## Response Format Rules
- No code blocks
- No technical jargon
- Use emojis sparingly (1-2 max)
- Sound like a CEO updating their boss, not a system report
- If something is wrong, name it clearly without alarm
