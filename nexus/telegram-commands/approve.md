---
name: Approve / Reject Decision
triggers:
  - "approve"
  - "i approve"
  - "yes do it"
  - "go ahead"
  - "do it"
  - "reject"
  - "no don't"
  - "i reject"
  - "don't do it"
  - "cancel that"
---

When founder sends an approval or rejection:

1. Find the most recent pending decision:
   - Check docs/FEEDBACK.md for items marked "PENDING"
   - Look for the most recent one (by timestamp)

2. If approval message:
   - Mark decision as APPROVED in docs/FEEDBACK.md
   - Add timestamp and "Approved by founder"
   - Unblock the action that was waiting:
     - If it was a Beads task: change status from BLOCKED to QUEUED
     - If it was a deploy: trigger Coolify webhook
     - If it was a message to send: send it
     - If it was a code change: assign to CTO
   - Respond confirming what's now happening

3. If rejection message:
   - Mark decision as REJECTED in docs/FEEDBACK.md
   - Add timestamp and "Rejected by founder"
   - Cancel or modify the blocked action
   - Ask for guidance if needed

4. If no pending decisions:
   - Respond: "Nothing pending your approval right now! If you're approving something specific, let me know what."

## Example Flows

**Approve a blocked task:**
> ✅ Approved! I've unblocked the Kaggle notebook pre-warm task. CTO will add it to the queue and start tonight. I'll confirm when it's done.

**Approve a content piece:**
> ✅ Done! Published the blog post to the site and scheduled Twitter/LinkedIn for 10 AM. Should drive some traffic from the "self-hosted ElevenLabs" search results.

**Reject with guidance:**
Founder: "Reject. Price it at $29 not $49."

> Got it, rejected the $49 Pro plan price. Updating to $29 and adjusting the Stripe product. Landing page copy will be updated too. Confirming the new pricing:
> Free: $0 | Starter: $19 | Pro: $29 | Enterprise: $199

## If Multiple Pending Decisions

List them:
> You have 2 pending approvals:
> 1. Add Kaggle cron job (I recommend: approve)
> 2. Outreach to 15 beta users from waiting list (I recommend: approve)
>
> Which one are you approving? Or "approve both"?
