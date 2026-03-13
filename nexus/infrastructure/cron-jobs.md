# NEXUS Cron Jobs

All cron jobs run through OpenClaw's built-in scheduler (configured in `openclaw-config.json5`).
No separate crontab needed — OpenClaw manages scheduling.

## Schedule Overview

| Time | Job | Agent | Description |
|------|-----|-------|-------------|
| Every 5 min | Watchdog health check | Watchdog | Monitor all agents, costs, errors |
| 2:00 AM daily | Jules maintenance | CTO (Jules) | Dependency updates, test coverage |
| 3:00 AM daily | Market Scout scan | Market Scout | Product Hunt, HN, Reddit research |
| 7:00 AM daily | Morning briefing | CEO | Telegram briefing to founder |
| 9:00 AM Monday | Finance weekly report | Finance | P&L report to CEO |
| 12:00 PM daily | Midday update | CEO | Task progress Telegram update |
| 6:00 PM daily | Evening summary | CEO | Day summary Telegram message |
| 8:00 AM Sunday | Product insights | Product Analyst | Weekly UX/funnel analysis |

## Adding New Cron Jobs

Add to `infrastructure/openclaw-config.json5` under the `"cron"` array:

```json5
{
  "name": "job-name",           // unique identifier
  "schedule": "0 9 * * 1",     // cron expression (UTC)
  "prompt": "What to do...",   // prompt for the agent
  "channel": "telegram",       // "telegram", "internal", or "whatsapp"
  "agent": "ceo"               // optional: specific agent to run as
}
```

## Cron Expression Reference

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23, UTC)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *
```

Common patterns:
- `0 7 * * *` — Every day at 7:00 AM UTC
- `*/5 * * * *` — Every 5 minutes
- `0 9 * * 1` — Every Monday at 9 AM UTC
- `0 8 * * 0` — Every Sunday at 8 AM UTC

**Note:** Times are UTC. India Standard Time (IST) = UTC+5:30
- 7:00 AM IST = 1:30 AM UTC
- 12:00 PM IST = 6:30 AM UTC
- 6:00 PM IST = 12:30 PM UTC

Adjust the cron expressions in `openclaw-config.json5` for your timezone.
