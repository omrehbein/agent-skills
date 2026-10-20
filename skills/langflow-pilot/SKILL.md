---
name: langflow-pilot
description: "Use when an AI agent must create, inspect, edit, validate, run, debug, duplicate, rename, export, or safely delete flows on a running Langflow instance through the official LFX MCP server; when configuring the lfx-mcp stdio server; or when component types, ports, fields, tool-mode connections, build failures, or flow execution need discovery and verification."
---

# Pilot Langflow with LFX MCP

Use the official LFX MCP server to manage flows through Langflow's API. This skill is independently authored from the [official documentation](https://docs.langflow.org/lfx-mcp); it is not an official Langflow skill.

## Principles

1. **Discover before composing.** Call search_component_types, then describe_component_type for every chosen type. Never guess component names, ports, fields, options, or output types.
2. **Inspect before changing.** Resolve a flow with list_flows, then read get_flow_info and component details. Preserve its ID and unrelated nodes, edges, settings, and metadata.
3. **Choose the least destructive operation.** Prefer targeted component and connection tools. update_flow_from_spec replaces all nodes and edges; use it only when full graph replacement is intended and authorized.
4. **Validate before running.** Call validate_flow after graph or configuration changes. If invalid, report and repair the exact errors before run_flow.
5. **Verify effects.** Re-read the flow after edits, run harmless representative input when execution is authorized, inspect build/component results when needed, and use notify_done after stepwise edit sequences that need immediate UI settlement.
6. **Protect credentials.** Prefer a Langflow API key supplied through protected environment configuration. Never print, store in the flow, commit, or repeat credentials. If authentication is absent, explain that login sends credentials through MCP arguments and use it only when the client guarantees protected argument handling; otherwise stop and request protected API-key configuration.
7. **Confirm destructive work.** Before delete_flow, obtain fresh explicit confirmation naming the exact flow and ID. Treat component removal and full-spec replacement as destructive when they discard behavior.

## Connect

A compatible MCP client starts the server as a local stdio process with command `uvx` and arguments `--from`, `lfx`, `lfx-mcp`. Supply `LANGFLOW_SERVER_URL` and preferably `LANGFLOW_API_KEY` through protected environment configuration.

There is no standalone `lfx-mcp` package on PyPI; the binary ships in the `lfx` package. Do not place real secrets in version-controlled configuration. Exact client configuration locations vary; use the client's documented MCP registration mechanism.

## Core workflow

### Create a flow

1. Clarify desired inputs, outputs, model/provider, tools, data sources, and success evidence.
2. Discover and describe candidate component types.
3. Prefer create_flow_from_spec for a complete new graph. Use stepwise tools when dynamic configuration, iterative inspection, or partial construction is safer.
4. Use the creation result as initial validation evidence because create_flow_from_spec validates by default. Validate again after later changes, run harmless input when authorized, and call notify_done only when additional stepwise edits need UI settlement.

### Edit an existing flow

1. Use list_flows and match by ID, not name alone when names collide.
2. Read get_flow_info; inspect affected components.
3. Duplicate first for rollback when the requested change is broad or risky. Use export only for redacted inspection, versioning, or sanitized sharing.
4. Apply only required edits with configure_component, component tools, and connection tools.
5. Use update_flow_from_spec only for deliberate full replacement. Duplicate first when rollback matters; export is redacted and is suitable only for inspection, versioning, or sanitized sharing.
6. Validate, re-read, optionally run, then notify_done with a factual summary.

### Debug and run

- Use validate_flow for graph validity.
- Prefer synchronous validate_flow. build_flow returns a job ID but LFX MCP has no generic wait tool; use get_build_results only after independently confirming build completion or to inspect an already completed build. Use get_component_output to isolate wrong intermediate data.
- Use run_flow with representative, non-sensitive input; runtime tweaks are temporary and should not be reported as persisted configuration.
- Never claim success from tool completion alone. Report the returned output or exact validation/build evidence.

## Safety boundaries

- delete_flow: irreversible; always require explicit confirmation immediately before the call.
- remove_component and disconnect_components: inspect dependencies and state what will be removed.
- update_flow_from_spec: graph replacement, not a merge. It attempts to restore original graph data if rebuilding fails, but duplicate first when independent rollback matters.
- run_assistant: may persist server-side canvas changes. Treat it as a mutating operation, inspect its result, and validate the resulting flow.
- batch: improves efficiency but is sequential, not transactional. Earlier actions can persist when a later action fails; use it only when partial completion is acceptable or recoverable.
- export_flow: the official tool redacts sensitive fields, so it is not a complete rollback backup for secret-bearing flows. Review exported data before sharing or committing it.

For exact task sequences and complete tool coverage, read [references/tool-workflows.md](references/tool-workflows.md).
