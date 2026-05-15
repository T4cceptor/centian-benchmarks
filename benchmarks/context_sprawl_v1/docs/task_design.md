# Task Design: Bug-Fix TDD with Sprawl-Injectable Docs

**Status:** Draft for pilot validation
**Owner:** Ben / Centian
**Used by:** Context sprawl experiment, Centian benchmarks series Part 2

---

## Overview

A bug-fix TDD task where the agent must:

1. Read a description of a reported bug
2. Retrieve API documentation via a mock MCP server (`get_docs` tool)
3. Identify the rule that's being violated by the existing code
4. Write a failing test demonstrating the bug
5. Implement a minimal fix
6. Confirm all tests pass

Sprawl is injected into the documentation returned by `get_docs`. The agent's comprehension of the docs — under varying signal-to-noise ratios — is the variable under test.

## Task framing (prompt to agent)

> A free-plan user reported that creating additional users for their tenant in the MyOrgAPI returns a 400 error. The existing code at `user_payload.py` builds the API payload. Use `get_docs` to retrieve the API specification, then fix the bug using test-driven development (centian TDD template).

The prompt deliberately does not identify the offending field or rule. The agent must comprehend the documentation to determine which rule applies to free-plan tenants and connect it to the bug in the existing code. This mirrors a realistic bug report and ensures sprawl-induced degradation of comprehension (rather than lookup) is what's measured.

## Buggy code (`user_payload.py`)

```python
"""Builds payloads for the MyOrgAPI /users endpoint."""


def build_user_create_payload(user, tenant_id):
    """Build the JSON payload for creating a user via MyOrgAPI."""
    payload = {
        "tenant_id": tenant_id,
        "user": {
            "email": user["email"].lower(),
            "display_name": " ".join(user["display_name"].split()),
            "role": user.get("role", "member"),
        },
        "metadata": {
            "source": "api",
            "version": 1 if tenant_id.startswith("archive_") else 2,
        },
    }

    # Legacy tenants preserve email casing for backwards compatibility
    if tenant_id.startswith("legacy_"):
        payload["user"]["email"] = user["email"]

    return payload
```

## Existing tests (`test_user_payload.py`)

```python
from user_payload import build_user_create_payload


def test_basic_payload_lowercases_email():
    user = {"email": "Alice@Example.COM", "display_name": "Alice"}
    result = build_user_create_payload(user, "tenant_abc")
    assert result["user"]["email"] == "alice@example.com"


def test_display_name_whitespace_is_normalized():
    user = {"email": "bob@example.com", "display_name": "  Bob   Smith  "}
    result = build_user_create_payload(user, "tenant_abc")
    assert result["user"]["display_name"] == "Bob Smith"


def test_legacy_tenant_preserves_email_casing():
    user = {"email": "Carol@Example.COM", "display_name": "Carol"}
    result = build_user_create_payload(user, "legacy_corp_42")
    assert result["user"]["email"] == "Carol@Example.COM"


def test_archive_tenant_uses_v1_metadata():
    user = {"email": "dave@example.com", "display_name": "Dave"}
    result = build_user_create_payload(user, "archive_old_inc")
    assert result["metadata"]["version"] == 1


def test_default_metadata_version_is_2():
    user = {"email": "eve@example.com", "display_name": "Eve"}
    result = build_user_create_payload(user, "tenant_xyz")
    assert result["metadata"]["version"] == 2


def test_role_defaults_to_member_when_not_specified():
    user = {"email": "frank@example.com", "display_name": "Frank"}
    result = build_user_create_payload(user, "tenant_xyz")
    assert result["user"]["role"] == "member"


def test_explicit_role_is_preserved():
    user = {"email": "grace@example.com", "display_name": "Grace", "role": "admin"}
    result = build_user_create_payload(user, "tenant_xyz")
    assert result["user"]["role"] == "admin"
```

The existing tests cover the basic case, display-name normalization, legacy-tenant casing, archive-tenant version, default role, and explicit role. They do **not** cover any free-plan tenant case, which is where the bug lives. The test names and coverage are designed to look like reasonable existing coverage rather than a treasure map pointing at `free_` tenants.

## Documentation (returned by `get_docs`)

The mock MCP server's `get_docs` tool returns HTML documentation containing the following rules. Sprawl is injected around this content per the experiment's sprawl ratio variable.

```
MyOrgAPI — Create User Endpoint

POST /users

The endpoint accepts a JSON payload with the following structure:

{
  "tenant_id": string,
  "user": {
    "email": string,
    "display_name": string,
    "role": string (optional)
  },
  "metadata": {
    "source": "api",
    "version": integer
  }
}

Rules:

1. The `email` field must be lowercased before submission, except when the
   `tenant_id` starts with `legacy_`. Legacy tenants preserve the original
   casing for backwards compatibility.

2. The `role` field must be omitted from the payload (not set to null, not
   set to any default value) when the tenant is on the free plan. Free-plan
   tenants are identified by `tenant_id` values starting with `free_`. This
   rule applies regardless of whether the caller provides a `role` value —
   any provided role is discarded for free-plan tenants. For all other
   tenants, `role` defaults to "member" if not specified by the caller.

3. The `display_name` field must be trimmed of leading and trailing
   whitespace, with any sequence of internal whitespace collapsed to a
   single space.

4. The `metadata.version` field must be `2` by default, but `1` for any
   tenant whose ID starts with `archive_`.
```

Rule 2 is the rule the buggy code violates. The rule is written to be unambiguous about the caller-provided-role edge case.

## Expected agent behavior (under no sprawl)

1. **Planning phase:** agent declares its intent to write a test for free-plan role omission. Test name something like `test_free_plan_tenant_omits_role`. Expected failing assertion: `"role" not in result["user"]`. Expected fix location: the role-handling block in `build_user_create_payload`.

2. **Execution phase:**
   - Calls `get_docs` to retrieve documentation
   - Reads the existing code
   - Writes the failing test:
     ```python
     def test_free_plan_tenant_omits_role():
         user = {"email": "test@example.com", "display_name": "Test"}
         result = build_user_create_payload(user, "free_starter")
         assert "role" not in result["user"]
     ```
   - Confirms test fails (current code always sets `role`)
   - Implements the fix:
     ```python
     # Free-plan tenants must not have a role field
     if tenant_id.startswith("free_"):
         payload["user"].pop("role", None)
     ```
     (Or equivalent — multiple valid implementations exist)
   - Confirms all tests pass

## MCP server configuration

A single MCP server is configured with one tool:

```
Tool: get_docs
Description: "Retrieve documentation for the MyOrgAPI."
Parameters: none
Returns: HTML content containing the API specification, with sprawl
         injected per the current experiment configuration.
```

The Centian workflow is configured to require at least one call to `get_docs` before the agent can advance from planning to execution. This ensures the docs are actually retrieved and the sprawl is actually delivered to the agent's context.

## Sprawl injection

The HTML returned by `get_docs` is constructed as follows:

- **Signal:** the documentation content above, rendered as clean HTML with semantic tags (`<h1>`, `<h2>`, `<p>`, `<ol>`, `<li>`, `<code>`).
- **Noise:** added at signal-to-noise ratios of 1:0 (baseline), 1:1, 1:3, 1:10, and optionally 1:30 (pending pilot).
- **Noise content:** sampled from a fixed corpus of unrelated technical HTML (sidebar navigation, advertisement blocks, unrelated documentation excerpts, comment threads). Corpus is sampled deterministically with a fixed seed. Pre-filtered to remove imperative-mood sentences and direct instructions.

Two sprawl-content variants:
- **Variant A — unrelated noise:** content from other domains and topics. Readability is expected to filter this well.
- **Variant B — related-but-wrong noise:** documentation for other MyOrgAPI endpoints (e.g. `POST /admins`, `PATCH /users`) with similar but different rules. Readability cannot filter this structurally; only semantic understanding could.

Variant A is the main sweep. Variant B is a secondary experiment.

## Bug variants (for cross-rule generalization)

Three independent bug variants are run, each with its own buggy codebase:

| Variant | Buggy rule | Fix complexity |
|---|---|---|
| **V1: free-plan role** | Code always sets `role`; should omit for `free_` tenants | One conditional |
| **V2: legacy casing** | Code always lowercases email; should preserve for `legacy_` tenants | One conditional |
| **V3: archive version** | Code always uses `version: 2`; should use `version: 1` for `archive_` tenants | One conditional |

For V2 and V3, the buggy code is the same shape but with the legacy/archive logic removed. Existing tests are adjusted so they don't cover the buggy path. Bug report wording for V2 and V3 follows the same pattern as V1 — naming the affected customer segment (e.g. "a legacy customer reported..." or "an archived organization's user reported...") without identifying the offending field or rule.

Running three variants provides:
- Three data points per agent per sprawl ratio (3× effective sample size)
- Cross-rule generalization (is degradation consistent across rule types, or rule-specific?)
- Resilience against any single variant having unexpected properties

## Metrics

Reused from prior benchmark:
- Success rate (all tests pass at end)
- First-pass rate (no restart or recovery)
- Median wall-clock time
- Total events (Centian + MCP)
- Total errors (Centian + MCP)

Added for this study:
- Total characters delivered to agent via Centian (data volume proxy)
- Planning-phase vs execution-phase failure attribution (where in the workflow did the agent fail?)

## Pre-pilot validation checklist

Before running the main sweep, verify on baseline (1:0 sprawl, no defense):

- [ ] At least one flagship model (Opus 4.7) completes V1 successfully **with ≥90% consistency over 10 baseline runs**. If lower, the task is too hard to cleanly measure sprawl effects against a baseline (noise floor problem). Mitigation: re-add a soft hint to the prompt (e.g. "the API returned an error about a field validation") without naming the specific rule or field.
- [ ] The agent's failing test catches the bug for the right reason (test asserts `"role" not in result["user"]`, not just `result["user"] != some_other_value`)
- [ ] The agent reads `get_docs` content (workflow enforces this — confirm enforcement actually triggers if the agent tries to skip)
- [ ] No existing test inadvertently passes the buggy path or fails on correct code
- [ ] V2 and V3 buggy codebases satisfy the same properties (each tested independently against the flagship baseline)
- [ ] Prompt ambiguity check: confirm the "free-plan user creating users for their tenant" phrasing is interpreted consistently by all tested flagships at baseline. If different flagships interpret the actor/subject relationship differently, refine the prompt before main sweep.

Estimated validation effort: half a day to one day.

## Open questions

- **Language choice.** Spec written in Python for clarity. The Centian TDD template currently supports Python; if other languages are added, the task can be ported.
- **Variant B (related-but-wrong noise) corpus construction.** Needs careful design — the "wrong" endpoint docs must be plausibly relevant but distinguishable from the target endpoint to a careful reader. To be designed during pilot phase if Variant A succeeds.
- **Bug variant counts.** Three variants is the recommended scope. If compute time becomes binding, drop to V1 only and frame the result as specific to one bug type rather than generalized across rules.