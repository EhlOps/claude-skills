---
name: canvas-plan
description: Plan a code change visually. Produces a plan folder (.plans/DATE-SLUG/ at the repo root) holding a PLAN.md (design, alternatives considered, FAQ, risks, steps), Excalidraw diagrams of how the code relates, screenshots, example files, and any other media, plus a link to the live canvas at https://draw.ehlops.com where the user leaves sticky-note comments that the agent reads back and answers. Use this whenever the user wants a plan, design doc, RFC, proposal, architecture sketch or "show me how you'd approach this" before code is written, wants to see what the agent is thinking, asks to map or diagram how parts of a codebase relate, or says "canvas plan", even when they don't mention Excalidraw or diagrams. Also use it when the user says they've left comments on the canvas or plan.
---

# Canvas Plan

A canvas plan makes your thinking inspectable before any code changes. The user should be able to open one folder and understand what you found, what you propose, what else you considered, and why, mostly by *looking*, then push back by dropping sticky notes on the live canvas.

**Lean hard on Excalidraw.** The diagrams carry the explanation and the markdown supports them. Prose is for reasoning a picture can't hold: tradeoffs, the "why", the FAQ. When you're about to write a paragraph describing structure, flow, ownership, ordering or before/after, draw it instead and write one sentence pointing at it.

This skill builds on the **excalidraw-skill** for all canvas work (CLI `npx -y mcp-excalidraw-server <cmd>` or the `excalidraw` MCP tools). Read it first if you haven't this session, because its layout rules and quality checklist apply to every diagram here.

## The canvas: https://draw.ehlops.com

The user's canvas is hosted at **https://draw.ehlops.com**. Draw there and give the user that link, so they look at and comment on the same canvas you're drawing on. Never hand them `localhost`/`127.0.0.1` links or SSH tunnel instructions.

Point the CLI at it explicitly with `--url` (or `EXPRESS_SERVER_URL`). Otherwise the CLI auto-starts a private local server that the user can't see:

```bash
X="npx -y mcp-excalidraw-server --url https://draw.ehlops.com"
$X status    # should report "running": true
```

If `status` fails, tell the user the canvas looks down rather than falling back to a local canvas.

**MCP tools.** If `excalidraw` MCP tools are in your tool list, use them only after confirming they reach draw.ehlops.com. Run the marker check in the excalidraw-skill's "MCP Connection" section: create an element via MCP, then `$X get` it. An MCP server set up without `EXPRESS_SERVER_URL=https://draw.ehlops.com` silently draws on a local canvas the user never sees, so their comments would never reach you. If the check fails, or there are no MCP tools, use the CLI with `--url`. It works everywhere. If the user wants the MCP tools, show them the setup command from that section, adjusted for their client.

Two things follow from it being one shared, public canvas:

- **It has no authentication.** Anyone with the URL can see it. Keep secrets, credentials, customer data and internal hostnames off the canvas; refer to them generically.
- **Other plans may already be on it.** Before drawing a new plan, if `describe` shows existing content, `snapshot save before-<slug>` and then `clear --yes`. Each plan's own `scene.excalidraw` lets you restore it later.

## The output folder

```
<repo>/.plans/<YYYY-MM-DD>-<slug>/
├── PLAN.md                 # the document; template in references/plan-template.md
├── diagrams/
│   ├── scene.excalidraw    # full canvas: the baseline used to detect user comments
│   ├── 01-current.png      # one PNG per frame, numbered in reading order
│   ├── 02-proposed.png
│   ├── 03-alt-<name>.png
│   └── ...
├── examples/               # real code excerpts, sample inputs/outputs, before/after snippets, API shapes
└── media/                  # only when something warrants it: renders, recordings, profiler output, UI captures
```

- `<repo>` is the git root of the code being planned (`git rev-parse --show-toplevel`). If you're not in a repo, ask where to put it.
- The slug is short and descriptive (`auth-token-refresh`, not `plan`). If the folder already exists, you're revising that plan, so update it in place.
- Don't create empty `examples/` or `media/` folders just to fill out the layout. Add a file only when it helps someone understand the plan. A video or render belongs there when the change is something you'd naturally show that way, like a UI flow, an animation, or rendered output.
- Don't commit `.plans/` or add it to `.gitignore` yourself; that's the user's call. Mention it once.

## Workflow

### 1. Investigate before drawing

Read the code the change touches: entry points, the modules involved, how data moves, and what calls what. Each node you draw should correspond to something real, so note file paths as you go. Diagrams of imagined architecture are worse than none, because they look authoritative.

If the request is too vague to plan (you can't tell what's in scope), ask one or two sharp questions before drawing.

### 2. Draw the canvas, one frame per view

Put every view on **one canvas**, each in its own Excalidraw `frame` with a clear name. Lay frames out left to right in reading order with about 200px gaps so the user can pan through them like slides. Use frame ids `f-01-current`, `f-02-proposed`, … and give elements inside a frame matching prefixes (`cur-`, `new-`, `altA-`) so ids stay unique and readable.

Pick the views that fit the change. Usually:

| Frame | What it shows |
|-------|---------------|
| **Current** | How the relevant code is wired today: modules/files as boxes, calls/imports/data flow as arrows. Label boxes with real names (`auth/session.ts`, `TokenStore`). |
| **Proposed** | The same view after the change. Color what's new (green), changed (yellow) and removed (red, dashed) so the delta is visible at a glance. Add a small legend. |
| **Alternative(s)** | One frame per serious alternative, drawn at the same zoom as Proposed so they compare side by side. Usually 1–3 alternatives. |
| **Flow / sequence** | When ordering matters (request lifecycle, migration steps, retries), a numbered left-to-right or top-down flow. |
| **Rollout / steps** | For multi-step changes, the implementation order as a chain of boxes that matches the steps in PLAN.md. |

Add others when they earn their place: data model, state machine, dependency graph, failure modes. Skip a view rather than draw a trivial one.

Follow the excalidraw-skill quality loop on **every** frame: draw, screenshot that frame (`screenshot --frame <id>`), check for truncation, overlap and arrow crossings, fix, re-check. Messy diagrams undermine trust in the plan.

Small annotations on the canvas help: a free-standing text note beside a box ("hot path, ~2k rps") or a "?" note marking an open question. Keep them short, since the reasoning itself goes in PLAN.md.

### 3. Save the artifacts

After the canvas looks right:

```bash
P=<repo>/.plans/<date>-<slug>
X="npx -y mcp-excalidraw-server --url https://draw.ehlops.com"
$X export --out $P/diagrams/scene.excalidraw          # also the comment baseline
$X screenshot --frame f-01-current  --scale 2 --out $P/diagrams/01-current.png
$X screenshot --frame f-02-proposed --scale 2 --out $P/diagrams/02-proposed.png
# ...one per frame
$X snapshot save canvas-plan-<slug>
```

Put real code in `examples/` when it sharpens the plan: the current function you're changing, a sketch of the new interface, a sample config or payload. Name files descriptively (`examples/current-refresh-logic.ts`, `examples/proposed-TokenStore-interface.ts`) and keep excerpts focused. In excerpts, put the source path and line range as a comment at the top.

### 4. Write PLAN.md

Use `references/plan-template.md`. What matters:

- **Visual first.** Every major section opens with its diagram (`![Proposed](diagrams/02-proposed.png)`) and then a few lines of commentary. If a section has no picture, ask whether it needs one.
- **Alternatives considered** are first-class. For each one give its diagram, what it is in a sentence, pros, cons, and the specific reason it lost. Include "do nothing" when that's a real option. Show the comparison as a table across the criteria that actually decided it.
- **FAQ.** Anticipate what a skeptical reviewer would ask: "why not X?", "what happens when Y fails?", "does this break Z?", "how do we roll back?", "how big is this?". Write 5–10 real questions with direct answers, not filler.
- **Ground claims in code.** Cite `path/to/file.ts:42` when you say something about current behavior.
- **Open questions** you need the user to decide go in their own section. Mark them on the canvas too.
- Link the live canvas near the top (see below).

### 5. Hand it over

End your turn with a short message containing:

- The folder path, plus PLAN.md as a clickable path.
- The **live canvas link**: https://draw.ehlops.com
- How to comment: *"Drop a sticky note (a rectangle with text, any color) or a text box on the canvas next to what you're asking about. Draw an arrow to it if you like. Then tell me 'check my comments'."* They can also move, recolor or retype your boxes; you'll see those edits too.
- The 1–3 decisions you most need from them.
- Optionally a read-only share link from `share`. Note that edits there don't sync back.

Don't start implementing. The plan exists so the user can redirect you cheaply.

## Reading and answering comments

When the user says they've commented (or asks you to check the canvas):

1. Export the live scene and diff it against the baseline:
   ```bash
   $X export --out /tmp/canvas-current.excalidraw
   python3 <this-skill>/scripts/find_comments.py $P/diagrams/scene.excalidraw /tmp/canvas-current.excalidraw
   ```
   The script lists new elements (with their text, frame, and what they point at or sit nearest) and any of your elements the user edited, moved or deleted. Screenshot the affected frames as well, because placement sometimes carries meaning the script can't capture.
2. Answer each comment **on the canvas**: a text element right beside it, in blue (`#1971c2`), starting with `↳`. Keep it to one or two lines and point to PLAN.md for anything longer. Don't delete or move the user's notes.
3. If a comment changes the plan, update the diagrams, re-export the PNGs, and update PLAN.md. Record it in PLAN.md's **Feedback log**: the comment, your response, and what changed.
4. Re-export `scene.excalidraw` so the new baseline includes their notes and your replies, and the next diff only shows fresh comments.
5. Summarize in chat what you changed and what still needs their decision.

Treat edits to your elements as feedback too. A box the user dragged into another zone, or a label they retyped, is a statement about the design. Acknowledge it, and either adopt it or explain why not.

## Revising an existing plan

If `.plans/<…>-<slug>/` already exists, `import diagrams/scene.excalidraw --replace` to restore the canvas first. Snapshot it before big changes. Keep earlier alternatives in the doc unless the user dismisses them, since the history of what was considered is part of the value.
