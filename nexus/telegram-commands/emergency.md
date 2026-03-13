---
name: Emergency Stop
triggers:
  - "stop everything"
  - "emergency"
  - "kill everything"
  - "halt"
  - "pause everything"
  - "stop all agents"
  - "shut it down"
---

## EMERGENCY HALT PROTOCOL

When founder sends any emergency trigger:

### IMMEDIATE (within 5 seconds):
1. Send acknowledgement to Telegram first:
   > 🛑 Emergency halt initiated. Stopping all agents now...

### WITHIN 30 SECONDS:
2. Send SIGTERM to all ZeroClaw daemons:
   ```bash
   sudo systemctl stop nexus-sales nexus-marketing nexus-support \
     nexus-market-scout nexus-finance nexus-legal \
     nexus-product-analyst nexus-watchdog
   ```

3. Pause all Claude Code Web sessions (via Agent Mail signal)

4. Cancel all in-progress Beads tasks (mark as PAUSED, not cancelled)

5. Stop all pending cron jobs (mark as SUSPENDED)

6. Log the halt event:
   - Timestamp
   - Which tasks were interrupted
   - Current state of each agent

7. Final confirmation to Telegram:
   > 🛑 All agents stopped.
   > Tasks paused: X (not deleted, resumable)
   > Agents halted: Sales, Marketing, Support, Scout, Finance, Legal, Product, Watchdog
   > All cron jobs suspended.
   >
   > Send 'resume' when ready to restart. Or tell me what to change first.

## RESUME PROTOCOL

When founder sends "resume" after an emergency halt:

1. Ask for confirmation (don't auto-resume):
   > Ready to resume. All agents will restart from where they left off.
   > Paused tasks: [list]
   > Reply 'resume all' to restart everything, or tell me which to restart.

2. On "resume all":
   - Start all systemd services
   - Restore cron schedule
   - Unpause Beads tasks
   - Send confirmation

3. On partial resume (e.g., "resume everything except sales"):
   - Start all except specified agents
   - Confirm what's running and what's not

## PARTIAL STOP

If founder says "pause sales" or "stop the marketing agent":
- Stop only that specific agent
- Respond: "✅ [Agent] paused. All other agents still running. Send 'resume [agent]' to restart."

## DO NOT USE FOR:
- Deploying after a bad deploy (use Coolify rollback instead)
- Fixing a bug (create a task for CTO instead)
- Rate limit issues (Watchdog handles this automatically)

Emergency halt is for true emergencies only: data breach, runaway costs, legal threat, founder override.
