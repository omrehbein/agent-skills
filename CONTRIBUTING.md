# Contributing

Thanks for helping improve these skills.

## Adding or changing a skill

1. Create `skills/<skill-name>/SKILL.md`. The folder name must equal the `name` in the frontmatter.
2. Frontmatter:
   ```yaml
   ---
   name: my-skill            # lowercase letters, digits and hyphens, max 64 chars
   description: "What the skill does and when the agent should use it." # max 1024 chars
   ---
   ```
   The description is what the agent uses to decide whether to load the skill — name concrete triggers (tools, file types, error messages, sites).
3. Keep skills agent-agnostic and compliant with the [Agent Skills specification](https://agentskills.io/specification): describe capabilities ("run JavaScript in the page", "press a key") rather than one product's tool names.
4. Keep `SKILL.md` focused (ideally under 500 lines). Move long material to `references/` and link to it.
5. Never include secrets or real identifiers: tokens, keys, passwords, account IDs, internal hostnames, customer data. Use placeholders such as `<account-id>`.
6. Test the instructions against a real target before opening a PR and describe how you tested and with which agent(s).
6. Run the checks locally:
   ```bash
   pip install pyyaml
   python scripts/validate_skills.py
   ```
7. Add or update the skill's row in the table in `README.md`.

## Commits and pull requests

- Use [Conventional Commits](https://www.conventionalcommits.org/): `feat(ace-editor): ...`, `fix(ace-editor): ...`, `docs: ...`, `ci: ...`.
- One skill per pull request when possible.
- CI (`validate`) must pass before merge.

## Reporting problems

Open an issue with the skill name, the agent and version you used, what you asked, what happened and what you expected.
