---
name: Build Command
triggers:
  - "build "
  - "create "
  - "make "
  - "develop "
  - "add feature"
  - "i want"
---

When founder says "build [something]" or "create [something]" or describes a feature:

1. Extract the feature/product description from the message

2. Search Cognee for similar prior specs or implementations
   - If found: mention it and ask if to build fresh or extend existing

3. Run SpecKit to create spec:
   ```
   specify.specify "[description]"
   ```
   This produces a structured SPEC.md with:
   - What it does
   - Tech stack
   - Acceptance criteria
   - Edge cases

4. Create Beads tasks from the spec:
   - Break into 3-8 tasks with clear titles
   - Set dependencies between tasks
   - Assign priority (HIGH for MVP, MEDIUM for enhancements)
   - Assign to CTO agent

5. Notify CTO via Agent Mail with:
   - Link to spec
   - Priority level
   - Any context founder provided
   - Deadline if mentioned

6. Respond to founder (under 100 words):
   - Confirm what you're building
   - Mention the number of tasks created
   - Give rough estimate (if obvious from complexity)
   - Tell them you'll update at midday or when started

## Example

Founder: "Build a voice preview feature so users can hear samples before selecting"

Response:
> Got it! Creating spec for voice preview feature. I'm breaking it into 3 tasks:
> 1. Add preview buttons to voice library (front end)
> 2. Add /v1/voices/{id}/preview endpoint (backend)
> 3. Cache preview files in S3 (so they don't regenerate)
>
> CTO will pick this up after the current landing page task.
> ETA: ~2 days. I'll update you at noon. 🔨

## Clarification Flow

If description is vague (< 10 words with no clear technical direction):
Ask ONE clarifying question before creating the spec:
> "Got it! Quick question before I spec this out: [specific question]. Then I'll have CTO on it right away."

Don't ask multiple questions at once.
