# SpecKit Configuration

SpecKit is the spec-first development methodology used by the NEXUS CTO agent.

## Setup

```bash
pip install specify-cli
specify init --ai claude
```

## Workflow

```bash
# Step 1: Create spec from description
specify.specify "Add voice preview feature to library"

# Step 2: Generate implementation plan
specify.plan

# Step 3: Break into tasks
specify.tasks

# Step 4: Implement
specify.implement
```

All specs are stored in the relevant product directory as `SPEC.md`.
