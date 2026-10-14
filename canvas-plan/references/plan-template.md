# PLAN.md template

Adapt the headings to the change and drop optional sections that don't apply. Keep these: System context, How it works today, Proposed design (with Sequence and Flow), and Alternatives considered, along with every screenshot. Keep the order as well: it moves from orientation, to the proposal, to the alternatives, to execution, to reviewer questions.

```markdown
# <Title: the change in plain words>

> **Status:** Draft · awaiting review   **Date:** YYYY-MM-DD
> **Live canvas:** https://draw.ehlops.com. Leave sticky notes next to anything you want to discuss.
> **Scene file:** [diagrams/scene.excalidraw](diagrams/scene.excalidraw)

![Canvas overview](diagrams/00-overview.png)

## TL;DR
Three to five bullets: the problem, the proposal, the main tradeoff, and what you need from the reviewer.

## Decisions needed
1. <The question>. Options: A / B. My recommendation: A, because …

## System context
![C4 System Context](diagrams/01-c4-context.png)
Who uses the system, what it talks to, and where this change sits.

![C4 Container](diagrams/02-c4-container.png)
The containers involved and which one(s) the change lives in.

## How it works today
![Current (C4 Component)](diagrams/03-current.png)
A few sentences on what matters in this picture, with file:line references for the claims.

## Proposed design
![Proposed (C4 Component)](diagrams/04-proposed.png)
What changes and **why**. The reasoning goes here, not on the canvas. Mention the color legend (green new, yellow changed, red removed).
Link the relevant examples: [proposed interface](examples/proposed-….ts).

### Sequence
![Sequence](diagrams/05-sequence.png)
Walk through the numbered messages that matter, especially failure and retry paths.

### Flow
![Flowchart](diagrams/06-flow.png)
The decision logic, and why each branch behaves the way it does.

## Alternatives considered
All the reasoning for alternatives is written here. Their canvas frames show only the shape.

### Alternative A: <name>
![Alternative A](diagrams/07-alt-a.png)
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
![Steps](diagrams/08-steps.png)   <!-- optional -->
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
- `diagrams/` holds the canvas scene, `00-overview.png` (the whole canvas) and one PNG per frame, each embedded above (`scripts/check_plan.py` passes)
- `examples/` holds code excerpts and sample data (list each with a one-line description)
- `media/` holds renders and recordings (only when present)

## Feedback log
| # | Comment (where) | Response | Changed |
|---|-----------------|----------|---------|
```
