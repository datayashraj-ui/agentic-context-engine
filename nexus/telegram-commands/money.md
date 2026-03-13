---
name: Revenue / Money Check
triggers:
  - "money"
  - "revenue"
  - "how much"
  - "mrr"
  - "stripe"
  - "earnings"
  - "profit"
  - "costs"
---

When founder asks about money:

1. Query Stripe MCP for:
   - Monthly Recurring Revenue (MRR)
   - Revenue this month (actual, not projected)
   - Revenue today
   - New subscriptions this week
   - Churned subscriptions this week
   - Top 3 customers by spend

2. Query Langfuse for LLM costs:
   - Total LLM cost this month
   - Breakdown by agent/model (CEO/CTO/Sales/etc.)
   - Daily average

3. Calculate costs:
   - Claude Max: $100/mo (fixed)
   - LLM API costs (Groq/Gemini = $0, others from Langfuse)
   - Infrastructure: $0 (all free tier / self-hosted)
   - Total monthly cost

4. Calculate net profit:
   - Net = Revenue - Total Costs
   - Break-even MRR = Total Fixed Costs

5. Format conversational response (under 120 words):

## Example Response

> 💰 Here's the money picture:
>
> **Revenue:** $847 MRR ($312 this month so far, $47 today)
> New subs: 3 this week. Churns: 1. Net: +2 customers.
>
> **Costs:** $100 (Claude Max) + $0 (everything else is free)
> Net profit this month: $212 🟢
>
> **Top customer:** dev@startup.io — $49/mo (Pro plan)
>
> Break-even: $100 MRR. We're past that. Next target: $1,000 MRR.

## If Pre-Revenue

> 💰 Revenue: $0 (pre-launch, as expected!)
> Costs: $100/mo (Claude Max subscription)
> Net: -$100/mo
>
> We break even at $100 MRR — that's just 6 Starter subscribers.
> Launch ETA: ~3 days based on current build progress.

## Extended View (if founder asks "full breakdown" or "details")

Include:
- Revenue per plan tier (Free/Starter/Pro/Enterprise)
- Month-over-month growth rate
- Projected MRR if current growth continues
- LLM cost per customer (efficiency metric)
