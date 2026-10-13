#!/usr/bin/env python3
"""Find the user's comments on a canvas-plan diagram.

Compares the scene the agent last saved (baseline) against the live canvas
export (current) and reports:
  - new elements the user added (sticky notes, text, arrows), with their text,
    the frame they sit in, and the agent elements they point at or sit next to
  - agent elements the user edited, moved, or deleted

Usage: find_comments.py <baseline.excalidraw> <current.excalidraw> [--json]
"""
import json
import math
import sys


def load(path):
    with open(path) as f:
        return {e["id"]: e for e in json.load(f).get("elements", []) if not e.get("isDeleted")}


def center(e):
    return (e.get("x", 0) + e.get("width", 0) / 2, e.get("y", 0) + e.get("height", 0) / 2)


def contains(outer, inner):
    cx, cy = center(inner)
    return (outer["x"] <= cx <= outer["x"] + outer.get("width", 0)
            and outer["y"] <= cy <= outer["y"] + outer.get("height", 0))


def label_of(e, elements):
    """Text of an element: its own text, or its bound label's text."""
    if e.get("text"):
        return e["text"]
    for b in e.get("boundElements") or []:
        t = elements.get(b.get("id"))
        if t and t.get("type") == "text" and t.get("text"):
            return t["text"]
    if e.get("type") == "frame":
        return e.get("name") or ""
    return ""


def binding_target(binding):
    if not binding:
        return None
    return binding.get("elementId") or binding.get("id")


def describe_agent(eid, elements):
    e = elements.get(eid)
    if not e:
        return eid
    label = label_of(e, elements)
    return f'{eid} ("{label}")' if label else eid


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    base, cur = load(args[0]), load(args[1])

    frames = [e for e in cur.values() if e.get("type") == "frame" and e["id"] in base]
    targets = [e for e in base.values()
               if e["id"] in cur and e.get("type") not in ("frame", "arrow", "line")
               and not e.get("containerId")]

    new_ids = [i for i in cur if i not in base]
    # Bound labels belong to their container; report them through it.
    new_ids = [i for i in new_ids if not (cur[i].get("containerId") in new_ids)]

    comments = []
    for i in new_ids:
        e = cur[i]
        if e.get("containerId") in base:
            # User typed a label onto an existing agent shape.
            comments.append({"id": i, "kind": "label-on-agent-shape", "text": e.get("text", ""),
                             "points_at": [describe_agent(e["containerId"], cur)], "frame": None})
            continue
        frame = next((f.get("name") or f["id"] for f in frames if contains(f, e)), None)
        points_at = []
        if e.get("type") == "arrow":
            for key in ("startBinding", "endBinding"):
                t = binding_target(e.get(key))
                if t and t in base:
                    points_at.append(describe_agent(t, cur))
        if not points_at and targets:
            cx, cy = center(e)
            nearest = min(targets, key=lambda t: math.dist((cx, cy), center(t)))
            points_at.append("near " + describe_agent(nearest["id"], cur))
        comments.append({"id": i, "kind": e.get("type"), "text": label_of(e, cur),
                         "frame": frame, "points_at": points_at})

    edits = []
    for i, b in base.items():
        if b.get("containerId") and b["containerId"] in base:
            continue  # reported via its container
        if i not in cur:
            edits.append({"id": i, "change": "deleted", "was": label_of(b, base)})
            continue
        c = cur[i]
        changes = []
        if label_of(b, base) != label_of(c, cur):
            changes.append(f'text "{label_of(b, base)}" -> "{label_of(c, cur)}"')
        if math.dist(center(b), center(c)) > 20 and b.get("type") != "arrow":
            changes.append("moved")
        if (b.get("width"), b.get("height")) != (c.get("width"), c.get("height")) and b.get("type") != "arrow":
            changes.append("resized")
        for k in ("strokeColor", "backgroundColor"):
            if b.get(k) != c.get(k):
                changes.append(f"{k} {b.get(k)} -> {c.get(k)}")
        if changes:
            edits.append({"id": i, "change": ", ".join(changes), "was": label_of(b, base)})

    if "--json" in sys.argv:
        print(json.dumps({"comments": comments, "edits": edits}, indent=2))
        return
    if not comments and not edits:
        print("No new comments or edits since the baseline.")
        return
    print(f"## {len(comments)} new comment(s)")
    for c in comments:
        where = f' in frame "{c["frame"]}"' if c.get("frame") else ""
        text = c["text"].replace("\n", " ") or "(no text)"
        print(f'- [{c["id"]}] {c["kind"]}{where}: "{text}" -> {", ".join(c["points_at"]) or "?"}')
    print(f"\n## {len(edits)} edit(s) to agent elements")
    for e in edits:
        print(f'- [{e["id"]}] ("{e["was"]}"): {e["change"]}')


if __name__ == "__main__":
    main()
