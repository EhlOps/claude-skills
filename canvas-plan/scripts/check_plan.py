#!/usr/bin/env python3
"""Check a canvas-plan folder before hand-over.

Fails (exit 1) when:
  - a required frame is missing from diagrams/scene.excalidraw
    (C4 context, C4 container, current, proposed, sequence, flow)
  - a frame has no PNG, or 00-overview.png is missing
  - a PNG in diagrams/ is not embedded in PLAN.md, or PLAN.md embeds a PNG
    that doesn't exist
  - an alternative frame has no "Why not" in PLAN.md, or the Alternatives
    considered section is missing
  - agent text on the canvas reads like reasoning (too long, or uses
    rationale words). Reasoning belongs in PLAN.md, not the diagram.

Usage: check_plan.py <plan-folder>
"""
import json
import os
import re
import sys

REQUIRED = {
    "c4-context": "C4 System Context (level 1)",
    "c4-container": "C4 Container (level 2)",
    "current": "Current, C4 Component (level 3) as it is today",
    "proposed": "Proposed, C4 Component (level 3) after the change",
    "sequence": "Sequence diagram",
    "flow": "Flowchart",
}
FRAME_ID = re.compile(r"^f-(\d{2})-([a-z0-9-]+)$")
# Ids the agent assigns: lowercase words joined by dashes. Excalidraw's own ids
# (what the user's notes get) are mixed-case nanoids, so they never match.
AGENT_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)+$")
MAX_WORDS = 15
REASONING = re.compile(
    r"\b(because|since we|pros?|cons?|why not|trade-?offs?|rationale|rejected|"
    r"we chose|chosen over|better than|worse than|downside|upside)\b",
    re.IGNORECASE,
)


def main(folder):
    errors = []
    scene_path = os.path.join(folder, "diagrams", "scene.excalidraw")
    plan_path = os.path.join(folder, "PLAN.md")
    for p in (scene_path, plan_path):
        if not os.path.isfile(p):
            print(f"FAIL missing {os.path.relpath(p, folder)}")
            return 1

    with open(scene_path) as f:
        elements = [e for e in json.load(f).get("elements", []) if not e.get("isDeleted")]
    by_id = {e["id"]: e for e in elements}
    with open(plan_path) as f:
        plan = f.read()

    # Frames: required kinds present, each with a PNG.
    frames = [e for e in elements if e.get("type") == "frame"]
    kinds = {}
    for fr in frames:
        m = FRAME_ID.match(fr["id"])
        if not m:
            errors.append(f"frame id '{fr['id']}' doesn't follow f-NN-<kind>")
            continue
        kinds.setdefault(m.group(2), []).append(fr["id"])
        png = os.path.join(folder, "diagrams", fr["id"][2:] + ".png")
        if not os.path.isfile(png):
            errors.append(f"frame {fr['id']} has no screenshot diagrams/{fr['id'][2:]}.png")
    for kind, label in REQUIRED.items():
        if not any(k == kind or k.startswith(kind + "-") for k in kinds):
            errors.append(f"missing required frame: {label} (id f-NN-{kind})")
    if not os.path.isfile(os.path.join(folder, "diagrams", "00-overview.png")):
        errors.append("missing diagrams/00-overview.png (whole-canvas screenshot)")

    # Screenshots: every PNG embedded, every embed exists.
    pngs = sorted(f for f in os.listdir(os.path.join(folder, "diagrams")) if f.endswith(".png"))
    for png in pngs:
        if f"](diagrams/{png})" not in plan:
            errors.append(f"screenshot not embedded in PLAN.md: diagrams/{png}")
    for ref in re.findall(r"\]\((diagrams/[^)]+\.png)\)", plan):
        if not os.path.isfile(os.path.join(folder, ref)):
            errors.append(f"PLAN.md embeds a missing file: {ref}")

    # Alternatives: the reasoning lives in the doc.
    if not re.search(r"^## Alternatives considered", plan, re.MULTILINE):
        errors.append("PLAN.md has no '## Alternatives considered' section")
    alts = [k for k in kinds if k.startswith("alt-")]
    why_nots = len(re.findall(r"\*\*Why not:?\*\*", plan))
    if why_nots < len(alts):
        errors.append(f"{len(alts)} alternative frame(s) but only {why_nots} '**Why not:**' entries in PLAN.md")

    # Canvas text: labels and short facts only, no reasoning.
    for e in elements:
        if e.get("type") != "text" or not e.get("text"):
            continue
        owner = e.get("containerId") or e["id"]
        if not (AGENT_ID.match(e["id"]) or (owner in by_id and AGENT_ID.match(owner))):
            continue  # the user's note
        text = " ".join(e["text"].split())
        if text.startswith("Re:"):
            continue  # reply to a comment; already kept short
        words = len(text.split())
        if words > MAX_WORDS:
            errors.append(f"canvas text '{e['id']}' is {words} words; move the explanation to PLAN.md: \"{text[:60]}...\"")
        elif REASONING.search(text):
            errors.append(f"canvas text '{e['id']}' reads like reasoning; move it to PLAN.md: \"{text}\"")

    for err in errors:
        print("FAIL", err)
    if not errors:
        print(f"OK {len(frames)} frames, {len(pngs)} screenshots embedded, no reasoning on the canvas")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
