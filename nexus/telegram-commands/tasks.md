---
name: Task List
triggers:
  - "tasks"
  - "show tasks"
  - "what are we building"
  - "backlog"
  - "what's in progress"
  - "todo"
---

When founder asks about tasks:

1. Query Beads API for all tasks, grouped by status:
   - ✅ Done (completed today or this week)
   - 🔨 In Progress (currently being worked on)
   - ⏳ Queued (next up, assigned)
   - 🔴 Blocked (stuck, needs decision)
   - 💡 Backlog (future ideas, not scheduled)

2. For each task include:
   - Task ID and title
   - Assigned agent
   - Brief status note (optional, for in-progress)

3. Format as clean Telegram list (not a wall of text):

## Example Response

> 📋 Here's the task board:
>
> **✅ Done today:**
> • TASK-001: InsForge schema — CTO ✓
>
> **🔨 In Progress:**
> • TASK-002: Landing page — CTO (70% done, frontend components)
> • TASK-003: TTS API endpoint — starts after landing page
>
> **⏳ Queued:**
> • TASK-004: Dashboard UI
> • TASK-005: Stripe integration
>
> **🔴 Blocked:**
> • Nothing blocked 🟢
>
> **🗂 Backlog:**
> • Voice preview feature (you suggested)
> • API key management page
>
> 5 of 7 MVP tasks remaining. ETA to v1.0: ~4 days.

## If Asking About Specific Task

If founder asks "what happened with task 3" or "status of the TTS endpoint":
- Look up that specific task in Beads
- Give detailed status: who's working on it, last update, estimated completion
- If blocked: explain why and your recommendation

## Task Count Summary

Always end with a brief progress summary:
- "X of Y MVP tasks remaining. On track / slightly behind / ahead of schedule."
