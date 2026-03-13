---
name: Morning Briefing (On-Demand)
triggers:
  - "briefing"
  - "morning briefing"
  - "daily summary"
  - "what happened"
  - "catch me up"
  - "weekly summary"
---

When founder requests a briefing:

1. Gather all data sources in parallel:
   - docs/PROGRESS_LOG.md — last 48 hours of activity
   - Beads — task completions, new tasks, blockers
   - Stripe — revenue events, new subscriptions, churn
   - GlitchTip — error summary, resolved issues
   - Langfuse — LLM cost summary
   - Chatwoot — customer support tickets, satisfaction

2. Compile into a comprehensive briefing document (< 500 words)

3. Generate audio summary via NotebookLM CLI (if available):
   ```
   notebooklm generate-audio --input briefing.md --duration 2min
   ```
   - If NotebookLM unavailable: skip audio, send text only

4. Send audio file to Telegram (or text if audio unavailable)

5. Follow with text version as a message

## Briefing Structure

```
🌅 NEXUS Briefing — [DATE]

📊 BUSINESS
• Revenue: $X MRR (+/-X% vs last week)
• New customers: X | Churned: X
• Next target: $X MRR

🔨 PRODUCT
• Shipped: [list]
• In progress: [list]
• Blocked: [list or "nothing blocked"]

📈 METRICS
• Signups this week: X
• Active users: X
• Support tickets: X open, X resolved

🎯 DECISIONS NEEDED
• [list or "no decisions pending"]

📅 TODAY'S PRIORITIES
1. [task 1]
2. [task 2]
3. [task 3]
```

## Weekly Briefing (Mondays)

If triggered on Monday or with "weekly" keyword:
- Include full week summary
- Month-to-date revenue vs. goal
- Team performance (agents uptime, tasks completed)
- Market intelligence highlights from Scout
- Forward planning for the week

## Audio Briefing

When audio is generated:
- 90-second summary (like a podcast)
- Natural, conversational tone
- Key numbers + what matters most
- Ends with today's top priority

Send audio file as Telegram voice message (not file attachment) for easy listening on phone.
