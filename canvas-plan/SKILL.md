---
name: canvas-plan
description: Plan a code change visually. Produces a plan folder (.plans/DATE-SLUG/ at the repo root) holding a PLAN.md (design, reasoning, alternatives considered, FAQ, risks, steps) with embedded screenshots of every canvas frame, required Excalidraw diagrams (C4 context/container/component, a sequence diagram, a flowchart), example files, and any other media, plus a link to the live canvas at https://draw.ehlops.com where the user leaves sticky-note comments that the agent reads back and answers. Use this whenever the user wants a plan, design doc, RFC, proposal, architecture sketch or "show me how you'd approach this" before code is written, wants to see what the agent is thinking, asks to map or diagram how parts of a codebase relate, or says "canvas plan", even when they don't mention Excalidraw or diagrams. Also use it when the user says they've left comments on the canvas or plan.
---

# Canvas Plan

A canvas plan makes your thinking inspectable before any code changes. The user should be able to open one folder and understand what you found, what you propose, what else you considered, and why, mostly by *looking*, then push back by dropping sticky notes on the live canvas.

**Diagrams show, the document argues.** Excalidraw carries *what*: structure, ownership, interactions, ordering, before/after. When you're about to write a paragraph describing any of those, draw it instead and write one sentence pointing at it. PLAN.md carries *why*: the reasoning, the tradeoffs, the alternatives and why they lost, the FAQ. That reasoning never goes on the canvas. Canvas text is limited to names, short labels and short facts (`hot path, ~2k rps`), because reasoning in a screenshot can't be reviewed line by line and goes stale without anyone noticing. `scripts/check_plan.py` enforces this.

**Every plan has these, no exceptions:**
- **Screenshots** of every frame plus the whole canvas, embedded in PLAN.md
- **C4 diagrams**: System Context (L1), Container (L2), and Component (L3) for both current and proposed
- **A sequence diagram** of the key interaction
- **A flowchart** of the control or decision logic
- **Alternatives considered** in PLAN.md, each with its reasoning

If a required view seems trivial for this change, draw it anyway, keep it small, and say in one line of PLAN.md why it's simple. A two-box Context diagram still orients the reader.

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
│   ├── 00-overview.png     # the whole canvas in one image (every frame, plus any user notes)
│   ├── 01-c4-context.png   # one PNG per frame, named after the frame id, in reading order
│   ├── 02-c4-container.png
│   ├── 03-current.png      # C4 component, today
│   ├── 04-proposed.png     # C4 component, after
│   ├── 05-sequence.png
│   ├── 06-flow.png
│   ├── 07-alt-<name>.png   # optional
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

Put every view on **one canvas**, each in its own Excalidraw `frame` with a clear name. Lay frames out left to right in reading order with about 200px gaps so the user can pan through them like slides. Frame names are titles the reader sees (`C4 L2: Containers`), and frame ids follow the scheme below.

Frame ids are `f-NN-<kind>`, and the PNG for each is `diagrams/NN-<kind>.png`. The checker finds frames by kind, so keep the kind names exact.

**Required frames**, in this reading order:

| Frame id | What it shows |
|----------|---------------|
| `f-01-c4-context` | **C4 System Context (L1).** The system being changed as one box, the people who use it, and the external systems it talks to. Mark the part this change touches. |
| `f-02-c4-container` | **C4 Container (L2).** The deployable or runnable units inside the system (apps, services, databases, queues, workers) and how they communicate. Highlight the container(s) the change lives in. |
| `f-03-current` | **C4 Component (L3), today.** The components inside the affected container as they are wired now: modules, classes and files as boxes, labeled with real names (`auth/session.ts`, `TokenStore`); calls, imports and data flow as arrows. |
| `f-04-proposed` | **C4 Component (L3), after the change.** The same view at the same zoom. Color what's new (green), changed (yellow) and removed (red, dashed), and add a small legend. |
| `f-05-sequence` | **Sequence diagram** of the key interaction after the change. Participants as boxes along the top, dashed vertical lifelines, numbered horizontal message arrows in time order, dashed return arrows, and failure or retry paths as labeled alternate blocks. If the interaction itself changes, add `f-05-sequence-current` before it. |
| `f-06-flow` | **Flowchart** of the control or decision logic: ellipse for start and end, rectangles for steps, diamonds for decisions with every branch labeled (`yes`/`no`, `token expired?`), arrows for flow. This covers the logic the change introduces or alters, for example request handling, a migration, or a retry policy. |

**C4 notation.** In each C4 box, put the name, a type tag (`[Person]`, `[Software System]`, `[Container: Node/Express]`, `[Component: TS class]`) and a description of *what it is*, at most about ten words. Label each relationship arrow with a verb and, where relevant, the protocol (`reads tokens from [SQL]`). Use a consistent style: people as rounded shapes, external systems in grey, the system in scope in blue. Each C4 frame gets a one-line title naming its level and scope.

**Optional frames**, added after the required ones:

| Frame id | What it shows |
|----------|---------------|
| `f-NN-alt-<name>` | One per serious alternative (usually 1–3), at the same zoom as Proposed so they compare side by side. The frame shows only the **shape** of the alternative. Its pros and cons, the reason it lost, and the comparison table all go in PLAN.md. |
| `f-NN-steps` | For multi-step changes, the implementation order as a chain of boxes matching the steps in PLAN.md. |
| `f-NN-<kind>` | Anything else that earns its place: data model, state machine, dependency graph, failure modes. |

Draw sequence diagrams and flowcharts directly with elements rather than through `mermaid`. Mermaid conversion needs an open browser tab and doesn't place its output inside a frame. Give elements inside a frame id prefixes that match it (`ctx-`, `ctr-`, `cur-`, `new-`, `seq-`, `flow-`, `alt-<name>-`) so ids stay unique and readable. Keep agent ids lowercase and dashed; the checker uses that to tell your text apart from the user's notes.

Follow the excalidraw-skill quality loop on **every** frame: draw, screenshot that frame (`screenshot --frame <id>`), check for truncation, overlap and arrow crossings, fix, re-check. Messy diagrams undermine trust in the plan.

Small annotations on the canvas help: a free-standing fact beside a box ("hot path, ~2k rps") or a "?" marking an open question. **No reasoning on the canvas.** Keep out "because", pros and cons, "why not", tradeoffs, and any text over about 15 words. If a label needs a justification, the justification belongs in PLAN.md under that frame's screenshot.

### 3. Save the artifacts

After the canvas looks right:

```bash
P=<repo>/.plans/<date>-<slug>
X="npx -y mcp-excalidraw-server --url https://draw.ehlops.com"
$X export --out $P/diagrams/scene.excalidraw          # also the comment baseline
$X screenshot --scale 1 --out $P/diagrams/00-overview.png   # whole canvas, every frame
for f in $(python3 -c "import json,sys; print(*[e['id'] for e in json.load(open(sys.argv[1]))['elements'] if e['type']=='frame' and not e.get('isDeleted')])" $P/diagrams/scene.excalidraw); do
  $X screenshot --frame $f --scale 2 --out $P/diagrams/${f#f-}.png   # f-01-c4-context -> 01-c4-context.png
done
$X snapshot save canvas-plan-<slug>
```

**Screenshots are part of the plan, not an optional extra.** Every frame gets a PNG, and the whole canvas gets `00-overview.png`, so the plan reads fully without opening the canvas. Look at each PNG (Read it) before embedding it. The headless renderer is what the reader sees, so fix anything it shows as clipped or as tofu boxes. Excalifont lacks some glyphs, like `→` and `✗`; use ASCII (`->`, `X`) in canvas text. Use `--scale 1` for the overview, since it's wide, and `--scale 2` for frames.

Put real code in `examples/` when it sharpens the plan: the current function you're changing, a sketch of the new interface, a sample config or payload. Name files descriptively (`examples/current-refresh-logic.ts`, `examples/proposed-TokenStore-interface.ts`) and keep excerpts focused. In excerpts, put the source path and line range as a comment at the top.

### 4. Write PLAN.md

Use `references/plan-template.md`. What matters:

- **Visual first.** Put the overview screenshot (`![Canvas overview](diagrams/00-overview.png)`) right under the header, then open every major section with its frame's screenshot (`![Proposed](diagrams/04-proposed.png)`), followed by the explanation and reasoning. If a section has no picture, ask whether it needs one.
- **Every screenshot is embedded**, each under the section it supports: the C4 Context and Container frames under "System context", Current and Proposed under their sections, Sequence and Flow under "Proposed design".
- **The reasoning lives here.** Under each screenshot, explain what the picture means and why the design is shaped that way. The canvas only labels; this is where you argue.
- **Alternatives considered** are first-class, and their reasoning is written here, not on the canvas. For each one give its screenshot (if it has a frame), what it is in a sentence, pros, cons, and a `**Why not:**` line with the specific reason it lost. Include "do nothing" when that's a real option. Show the comparison as a table across the criteria that actually decided it.
- **FAQ.** Anticipate what a skeptical reviewer would ask: "why not X?", "what happens when Y fails?", "does this break Z?", "how do we roll back?", "how big is this?". Write 5–10 real questions with direct answers, not filler.
- **Ground claims in code.** Cite `path/to/file.ts:42` when you say something about current behavior.
- **Open questions** you need the user to decide go in their own section. Mark them on the canvas too.
- Link the live canvas near the top (see below).

### 5. Run the checker

```bash
python3 <this-skill>/scripts/check_plan.py $P
```

It fails when a required frame (C4 context, C4 container, current, proposed, sequence, flow) is missing, when a frame has no PNG, when a PNG isn't embedded or an embed points nowhere, when an alternative has no `**Why not:**` in PLAN.md, or when your canvas text reads like reasoning. Fix every FAIL, re-export and re-screenshot, and run it again. Don't hand over a plan that fails. Run it again after each round of comments.

### 6. Hand it over

End your turn with a short message containing:

- The folder path, plus PLAN.md as a clickable path.
- The **live canvas link**: https://draw.ehlops.com
- How to comment: *"Drop a sticky note (a rectangle with text, any color) or a text box on the canvas next to what you're asking about. Draw an arrow to it if you like. Then tell me 'check my comments'."* They can also move, recolor or retype your boxes; you'll see those edits too.
- The 1–3 decisions you most need from them.
- Optionally a read-only share link from `share`. Note that edits there don't sync back.

Don't start implementing. The plan exists so the user can redirect you cheaply.

### Publishing the plan as an issue, PR or doc

When the user asks for the plan as a GitHub issue, a PR description or anything else outside the repo, **keep the screenshots in it**. Never drop the image lines because the relative `diagrams/…` paths won't resolve there. Host the PNGs and rewrite the links:

1. Push the PNGs to an asset branch (default `canvas-plans`, one folder per plan slug). This publishes them, so get the user's OK the first time for that repo. Say plainly when the repo is public, because anyone will be able to see the images. Use a temporary worktree so the user's checkout and branch are left alone:
   ```bash
   R=$(git rev-parse --show-toplevel); S=$(basename $P); WT=$(mktemp -d)
   if git fetch -q origin canvas-plans 2>/dev/null; then git worktree add -q --detach $WT origin/canvas-plans
   else git worktree add -q --detach $WT && git -C $WT checkout -q --orphan canvas-plans-tmp && git -C $WT rm -rqf .; fi
   mkdir -p $WT/$S && cp $P/diagrams/*.png $WT/$S/
   git -C $WT add $S && git -C $WT commit -qm "canvas-plan images: $S"; git -C $WT push -q origin HEAD:refs/heads/canvas-plans
   git worktree remove --force $WT
   ```
2. Rewrite the image links into the body. For a public repo use `https://raw.githubusercontent.com/<owner>/<repo>/canvas-plans/<slug>/<file>.png`. For a private repo use `https://github.com/<owner>/<repo>/blob/canvas-plans/<slug>/<file>.png?raw=true`, which renders for anyone with access:
   ```bash
   sed "s#](diagrams/\([^)]*\.png\))#]($BASE/\1)#g" $P/PLAN.md > /tmp/issue-body.md
   ```
   Then link the live canvas at the top of the body, drop the local-only sections (Artifacts, the empty Feedback log), and create the issue with `gh issue create --body-file`.
3. Images link to the branch, not to a commit, so re-pushing after a round of feedback updates the issue's pictures in place. Say so in the hand-over.

If pushing isn't allowed or wanted, create the issue without images and tell the user exactly which screenshots are missing. Don't quietly ship a picture-less plan.

## Reading and answering comments

When the user says they've commented (or asks you to check the canvas):

1. Export the live scene and diff it against the baseline:
   ```bash
   $X export --out /tmp/canvas-current.excalidraw
   python3 <this-skill>/scripts/find_comments.py $P/diagrams/scene.excalidraw /tmp/canvas-current.excalidraw
   ```
   The script lists new elements (with their text, frame, and what they point at or sit nearest) and any of your elements the user edited, moved or deleted. Screenshot the affected frames as well, because placement sometimes carries meaning the script can't capture.
2. Answer each comment **on the canvas**: a text element right beside it, in blue (`#1971c2`), starting with `Re:`. Don't use `↳`; the headless renderer draws it as a tofu box in the PNGs. Keep it to one or two lines and point to PLAN.md for anything longer. Don't delete or move the user's notes.
3. Re-take `00-overview.png` and the screenshots of every frame you or the user touched, so the PNGs in the plan show their notes and your replies. If the plan was published as an issue or PR, re-push the PNGs to the asset branch as well. If a comment changes the plan, update the diagrams, re-export the PNGs, and update PLAN.md. Record it in PLAN.md's **Feedback log**: the comment, your response, and what changed.
4. Re-export `scene.excalidraw` so the new baseline includes their notes and your replies, and the next diff only shows fresh comments.
5. Run `scripts/check_plan.py $P` again.
6. Summarize in chat what you changed and what still needs their decision.

Treat edits to your elements as feedback too. A box the user dragged into another zone, or a label they retyped, is a statement about the design. Acknowledge it, and either adopt it or explain why not.

## Revising an existing plan

If `.plans/<…>-<slug>/` already exists, `import diagrams/scene.excalidraw --replace` to restore the canvas first. Snapshot it before big changes. Keep earlier alternatives in the doc unless the user dismisses them, since the history of what was considered is part of the value.
