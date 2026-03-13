---
name: Market Research
triggers:
  - "research "
  - "scout "
  - "look into"
  - "investigate"
  - "what do you know about"
  - "market for"
  - "is there demand for"
---

When founder asks to research a topic:

1. Extract the research topic from the message

2. Check Cognee for existing research on this topic:
   - If found and < 7 days old: share summary, ask if they want fresh research
   - If found and > 7 days old: mention it's outdated, do fresh research

3. Trigger Market Scout agent via Agent Mail:
   - Include the exact topic
   - Set priority: URGENT (founder is actively waiting)
   - Request full opportunity scoring (1-10)
   - Set deadline: within 30 minutes

4. Respond to founder immediately (don't wait for results):
   > 🔍 Market Scout is researching [topic]. I'll send findings in about 20 minutes.
   > Scout will check Product Hunt, Hacker News, Reddit, competitor sites.

5. When Scout returns results:
   - Format as conversational summary
   - Lead with the opportunity score and recommendation
   - Key data points (market size, competitors, customer evidence)
   - Your recommendation (build / investigate / pass)

## Example Flow

Founder: "Research AI dubbing for YouTube videos"

Immediate response:
> 🔍 On it! Market Scout is diving into AI video dubbing. Checking Product Hunt, YouTube creator forums, and competitor pricing. Back in ~20 min.

20 minutes later:
> Found some interesting stuff on AI dubbing! 🎬
>
> **Score: 7.5/10** — Good opportunity, but competitive.
>
> Market: ~$200M today, growing fast with the YouTuber economy.
> Competitors: HeyGen ($29-99/mo), Dubverse ($19+/mo), Rask.ai.
> Key insight: Most tools are expensive and don't support Hindi/multilingual well.
>
> **Our angle:** Kokoro already supports 32 languages. We could add video dubbing to Voice Lab for $19/mo — cheaper than any competitor.
>
> **My take:** Worth investigating. Not urgent vs. current focus. Add to backlog?

## Deep Research Mode

If founder says "deep research on [topic]" or "full report":
- Market Scout gets 2 hours instead of 30 minutes
- Use Gemini CLI (1M context) for comprehensive analysis
- Include: full competitor matrix, pricing analysis, customer quotes, build estimate
- Send as a detailed report (can be longer)
