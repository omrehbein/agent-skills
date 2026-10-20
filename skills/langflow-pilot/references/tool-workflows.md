# LFX MCP tool workflows

This reference groups the official LFX MCP tools by intent. Tool availability can vary by installed lfx version, so discover the connected server's catalog and follow its schemas when they differ.

## Authentication and setup

- Prerequisites: a running Langflow instance, a stdio-capable MCP client, uv or an installed lfx package, a Langflow API key, and any provider API key already available in Langflow (typically as a global variable).
- Start with uvx --from lfx lfx-mcp.
- Set LANGFLOW_SERVER_URL and, preferably, LANGFLOW_API_KEY in protected client environment configuration.
- Without an API key, login accepts a username, password, and optional server URL, but those credentials travel as MCP arguments and may be retained by clients. Use login only when the client guarantees protected argument handling; otherwise require protected API-key configuration.
- Verify connectivity with a read-only call such as list_flows or search_component_types.

LFX MCP differs from Langflow as an MCP server, which exposes selected flows as tools, and Langflow as an MCP client, which lets canvas components call external MCP servers.

## Discover components

1. search_component_types — search by purpose, category, or output type. A no-argument call can enumerate types.
2. describe_component_type — read exact inputs, outputs, fields, advanced fields, constraints, defaults, beta/legacy status, and component_as_tool support.
3. components — use only if exposed and useful for the connected version; prefer the explicit search/describe pair for portable behavior.

Connections are type-safe: source output types must overlap target input types. Connecting component_as_tool enables tool mode when the component supports it.

## Read flows before mutation

- list_flows(query?) — returns IDs, names, descriptions, graph diagrams, summaries, and counts.
- get_flow_info(flow_id) — detailed graph, components, connections, and spec summary.
- list_components(flow_id) — inventory within one flow.
- get_component_info(flow_id, component_id) — current component parameters and ports.
- export_flow(flow_id) — full redacted JSON for inspection, versioning, or sanitized sharing. Because secrets are removed, it is not a complete rollback backup; duplicate_flow is safer for rollback. Review before distribution.

If names collide, require or resolve the UUID. Never infer a target solely from ordering.

## Create flows

Use create_flow_from_spec(spec, validate=true) after discovering every component and port. Validation is enabled by default, so do not immediately repeat validate_flow unless later changes occurred or independent revalidation is required. On failure it attempts to remove the partial flow, but still reconcile with list_flows before retrying.

For stepwise construction use create_flow, add_component, configure_component, connect_components, layout_flow, validate_flow, run_flow, then notify_done.

Use list_starter_projects and use_starter_project when a published starter closely matches the request; inspect and rename the resulting copy.

## Edit flows

- configure_component — targeted parameter changes. Inspect allowed fields first. Supplied values are literals and can disable variable-loading mode for that field. LFX MCP has no global-variable management tool: provision provider secrets in Langflow beforehand, and do not configure secret fields through MCP unless the connected version exposes a verified safe binding mechanism.
- add_component / remove_component — change nodes; removal also removes its connections.
- connect_components / disconnect_components — change edges. Provide exact port names when parallel edges exist.
- layout_flow — clean canvas layout after structural changes.
- rename_flow — change name and/or description.
- update_flow_from_spec — replace all nodes and edges while preserving the flow ID. It attempts to restore the original graph data if rebuilding fails, but the restore is best-effort. It does not perform final validation; duplicate first when independent rollback matters, call it, then validate_flow.
- duplicate_flow — create a safe working copy before broad experiments.
- freeze_component / unfreeze_component — reuse cached upstream output while iterating downstream; unfreeze before final end-to-end evidence when fresh execution matters.
- notify_done — signal that a stepwise modification series is settled so the UI refreshes promptly. Full-spec create/update operations already emit settlement events.

## Validate, execute, and debug

1. validate_flow(flow_id) — server-side graph validation. Stop on invalid results.
2. build_flow(flow_id) — trigger a build and obtain a job ID. LFX MCP exposes no generic job-wait tool.
3. get_build_results(flow_id) — inspect latest recorded validity, outputs, and errors only after independently confirming completion or when diagnosing an already completed build; an immediate read can be stale.
4. get_component_output(flow_id, component_id) — isolate a specific intermediate output.
5. run_flow(flow_id, input_value, input_type, output_type, tweaks?) — execute with optional temporary overrides. Treat output as evidence, not just a successful transport call.

Prefer non-sensitive, representative input. If execution has external effects, cost, or messaging consequences, obtain authorization or use an isolated copy or mocked dependency.

## Agent-assisted editing

run_assistant asks Langflow's server-side assistant to build, edit, or explain a flow. It can persist canvas changes. Afterwards inspect the returned flow, read get_flow_info, call validate_flow, run only when authorized, and call notify_done if needed.

## Batch operations

batch runs supported actions sequentially and supports $N.field references to earlier results. It is efficient for a known, recoverable sequence. It is not atomic: if an action fails, earlier mutations can remain. The batch registry is a subset of direct MCP tools (for example, run_assistant and batch itself are not batch actions), so use the error's available-tool list or the connected server schema rather than assuming every exposed tool is batchable. Reconcile the flow before retrying and never blindly replay an uncertain batch.

## Destructive operations

- delete_flow(flow_id) — after fresh explicit confirmation naming flow and UUID.
- remove_component — after showing the component and dependent connections.
- disconnect_components — after identifying the exact edges.
- update_flow_from_spec — only after the user intends complete replacement; duplicate first when independent rollback matters.

## Completion evidence

For any mutation, report the flow name and UUID, operations completed, validation result and exact remaining errors, observable output when run, backup identity for broad changes, and notify_done result. Do not report persisted changes from runtime-only tweaks, and do not report UI refresh as proof of graph correctness.

## Official sources

- [Build flows with the LFX MCP server](https://docs.langflow.org/lfx-mcp)
- [LFX MCP implementation for Langflow 1.12.5](https://github.com/langflow-ai/langflow/tree/v1.12.5/src/lfx/src/lfx/mcp)
- [Current LFX MCP development source](https://github.com/langflow-ai/langflow/tree/main/src/lfx/src/lfx/mcp)
