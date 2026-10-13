# claude-skills

My personal [Claude Code](https://claude.com/claude-code) skills, tracked from `~/.claude/skills`.

| Skill | Description |
|-------|-------------|
| [canvas-plan](canvas-plan/SKILL.md) | Plan a code change visually: a `.plans/` folder with PLAN.md (alternatives, FAQ, risks), Excalidraw diagrams, and a live canvas for sticky-note comments. |
| [excalidraw-skill](excalidraw-skill/SKILL.md) | Create, edit, and refine diagrams on a live Excalidraw canvas (via [mcp-excalidraw-server](https://www.npmjs.com/package/mcp-excalidraw-server)). |

## Install

```bash
git clone git@github.com:EhlOps/claude-skills.git ~/.claude/skills
```

Anthropic-managed skills synced from claude.ai (`synced/`) are excluded.

## Canvas and MCP connection

Both skills draw on the hosted canvas at **https://draw.ehlops.com**. The CLI reaches it with `--url https://draw.ehlops.com`, so it needs no setup beyond Node/npx.

To use the Excalidraw **MCP tools** as well, connect the MCP server to that canvas. Without `EXPRESS_SERVER_URL`, it silently uses a private local canvas.

**Claude Code**
```bash
claude mcp add excalidraw -s user \
  -e EXPRESS_SERVER_URL=https://draw.ehlops.com -e ENABLE_CANVAS_SYNC=true \
  -- npx -y mcp-excalidraw-server
```

**Claude Desktop**: add to `claude_desktop_config.json` and restart the app:
```json
{
  "mcpServers": {
    "excalidraw": {
      "command": "npx",
      "args": ["-y", "mcp-excalidraw-server"],
      "env": { "EXPRESS_SERVER_URL": "https://draw.ehlops.com", "ENABLE_CANVAS_SYNC": "true" }
    }
  }
}
```

The skills check the MCP connection with a marker element before trusting it, and fall back to the CLI if the MCP tools reach a different canvas. The canvas has no authentication, so keep secrets off it.
