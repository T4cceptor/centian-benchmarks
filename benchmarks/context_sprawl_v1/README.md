# context_sprawl_v1

`context_sprawl_v1` is the first context-sprawl benchmark suite. It currently contains only **V1** of the bug-fix task.

## What is implemented

- Python fixture code for the buggy payload builder and its existing regression coverage
- A runnable V1 case under `cases/bug_fix_v1`
- A local MCP docs server exposing:
  - tool: `get_docs`
  - description: `Retrieve documentation for the MyOrgAPI.`
  - current profile: signal-only baseline docs, with no injected noise
- Suite and Centian config wiring for the local benchmark

The signal content is the fictional MyOrgAPI documentation described in [docs/task_design.md](./docs/task_design.md).

## Design intent

This benchmark is meant to test **reasoning over documentation**, not simple rule lookup.

The agent is given a realistic bug report, existing code, and access to the API docs. The prompt intentionally does **not** name the offending field or tell the agent which documented rule is relevant. A successful run therefore requires the agent to:

1. understand the reported symptom
2. read the documentation
3. infer which documented rule could explain the failure
4. connect that rule back to the implementation
5. express the inference as a failing regression test and minimal fix

The baseline task should remain solvable on its own from the available evidence; it is not intended to be ambiguous or trick-based. The experiment is that, once irrelevant context is added around the same signal, performance may degrade because the agent has to preserve the right reasoning chain through a noisier context window — not because the answer was handed to it and became harder to search for.

## Language and tooling

The benchmark fixture is written in Python and uses only the standard library:

- tests: `python3 -m unittest`
- validation: `python3 -m py_compile`

The docs MCP server is a tiny dependency-free Node.js stdio server at [server/get_docs_server.mjs](./server/get_docs_server.mjs). It is intentionally separate from the benchmark fixture language because Node is already required by this repository's existing Centian setup.

## Current benchmark shape

The V1 fixture starts with:

- `user_payload.py`
- `test_user_payload.py`

During the task, the agent is expected to:

1. call `get_docs`
2. create a new failing regression test for the observed bug in `test_regression.py`
3. establish the failing baseline
4. make the minimal production fix in `user_payload.py`

This uses a new regression file because the repository's current `guided_tdd_workflow` template is shaped around creating a new test artifact during scaffolding. The original task design proposes appending the test into the existing `test_user_payload.py`; that exact flow is not represented by the current template yet.

## Docs profiles

`CONTEXT_SPRAW_PROFILE` currently supports only:

- `baseline`
- `1:0`

Both return the same signal-only HTML. Noise profiles such as `1:1`, `1:3`, and `1:10` are intentionally **not implemented yet** because the noise corpus still needs to be designed.

## Run V1 locally

```bash
./run-centian-demo-v1-benchmarks.sh \
  --suite context_sprawl_v1 \
  --scenario codex-gpt-5.4 \
  --repeat 1
```

The runner materializes the docs-server script path at launch time so the MCP process still starts correctly from Centian's copied benchmark workspace.

## Known gaps intentionally left open

These are called out rather than silently approximated:

1. **Mandatory `get_docs` gating is not implemented yet.** The task design says Centian should require at least one `get_docs` call before the workflow can advance from planning to execution. The current benchmark/template assets in this repo do not show an existing mechanism for that rule, so this setup exposes the tool and instructs the agent to use it, but does not enforce the call.
2. **The exact "append a test to an existing file" workflow is not modeled yet.** The current guided TDD template expects a new test file artifact during scaffolding. V1 uses a fresh regression file to stay compatible with the existing workflow.
3. **Noise profiles are not ready.** The server has the switch point for profiles, but only signal-only output exists for now.
4. **V2 and V3 are intentionally omitted.** This setup is V1-only, as requested.

## Local server smoke test

The docs server speaks JSON-RPC over stdio. A quick manual probe:

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0.1.0"}}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_docs","arguments":{}}}' \
  | node benchmarks/context_sprawl_v1/server/get_docs_server.mjs
```
