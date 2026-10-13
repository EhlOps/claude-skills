# PLAN.md template

Adapt the headings to the change, dropping sections that don't apply. Keep the order, though: it moves from orientation, to the proposal, to the alternatives, to execution, to reviewer questions.

```markdown
# <Title: the change in plain words>

> **Status:** Draft · awaiting review   **Date:** YYYY-MM-DD
> **Live canvas:** http://127.0.0.1:3000. Leave sticky notes next to anything you want to discuss.
> **Scene file:** [diagrams/scene.excalidraw](diagrams/scene.excalidraw)

## TL;DR
Three to five bullets: the problem, the proposal, the main tradeoff, and what you need from the reviewer.

## Decisions needed
1. <The question>. Options: A / B. My recommendation: A, because …

## How it works today
![Current](diagrams/01-current.png)
A few sentences on what matters in this picture, with file:line references for the claims.

## Proposed design
![Proposed](diagrams/02-proposed.png)
What changes and why. Mention the color legend (green new, yellow changed, red removed).
Link the relevant examples: [proposed interface](examples/proposed-….ts).

### Flow
![Flow](diagrams/03-flow.png)   <!-- if ordering matters -->

## Alternatives considered

### Alternative A: <name>
![Alternative A](diagrams/04-alt-a.png)
- **What:** one sentence
- **Pros:** …
- **Cons:** …
- **Why not:** the specific deciding reason

### Alternative B: <name> / Do nothing
…

### Comparison
| Criterion | Proposed | Alt A | Alt B |
|-----------|----------|-------|-------|
| <criterion that actually mattered> | ✅ | ⚠️ | ❌ |

## Implementation steps
![Steps](diagrams/05-steps.png)
1. Step: files touched, and how you'll verify it
2. …

## Risks & mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|

## FAQ
**Why not <obvious alternative>?**
Direct answer.

**What happens if <failure>?**
…

**How do we roll back?**
…

## Open questions
- …

## Artifacts
- `diagrams/` holds the canvas scene and one PNG per frame
- `examples/` holds code excerpts and sample data (list each with a one-line description)
- `media/` holds renders and recordings (only when present)

## Feedback log
| # | Comment (where) | Response | Changed |
|---|-----------------|----------|---------|
```
