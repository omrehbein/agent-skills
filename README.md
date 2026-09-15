# Agent Skills

[![validate](https://github.com/omrehbein/agent-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/omrehbein/agent-skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/format-Agent%20Skills-8A2BE2)](https://agentskills.io/specification)

Reusable skills for **any AI agent** that supports the open [Agent Skills](https://agentskills.io) format — Claude Code, ChatGPT & Codex, GitHub Copilot / VS Code, Cursor, Gemini CLI, OpenCode, Goose, Amp, Kiro, Junie, Roo Code and [many more](https://agentskills.io/clients).

Each skill is a folder with a `SKILL.md`: a short frontmatter (`name`, `description`) that the agent reads at startup to know **when** to use it, plus instructions it loads only when a task matches. No agent-specific code, no lock-in.

## Skills

| Skill | What it does |
| --- | --- |
| [`ace-editor`](skills/ace-editor/SKILL.md) | Read, replace and fix text in Ace code editors during browser automation (AWS console policy editors, Cloudscape, react-ace) without the corruption caused by typing — via the editor API, with paste/clipboard fallbacks and verification steps. |

## Install

### With the `skills` CLI (any agent)

```bash
npx skills add omrehbein/agent-skills --skill ace-editor
```

The CLI asks which agents to install to. Use `-a <agent>` to target one directly, `-g` for a user-level (global) install, and omit `--skill` to pick skills interactively.

### Manually

Copy the skill folder into your agent's skills directory — each client documents its location in the [Agent Skills client list](https://agentskills.io/clients). For example, Claude Code reads `~/.claude/skills/` (user) and `<project>/.claude/skills/` (project).

```bash
git clone https://github.com/omrehbein/agent-skills.git
cp -r agent-skills/skills/ace-editor <your-agent-skills-dir>/
```

## Usage

Nothing to wire up: the agent loads a skill on its own when your request matches the skill's description. Agents that expose skills as commands also let you call one explicitly (e.g. `/ace-editor`).

## Compatibility

Skills follow the [Agent Skills specification](https://agentskills.io/specification) and are written against generic capabilities — "run JavaScript in the page", "press a key", "read a file" — instead of a specific product's tool names, so they work the same with Playwright, Puppeteer, browser MCP servers or an agent's built-in browser tools.

## Repository layout

```text
skills/
  <skill-name>/
    SKILL.md          # required: frontmatter (name, description) + instructions
    references/       # optional: extra docs loaded on demand
    scripts/          # optional: helper scripts the skill calls
scripts/
  validate_skills.py  # CI check for frontmatter and leaked secrets
```

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) © Osmar Maciel Rehbein
