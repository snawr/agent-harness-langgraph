# PLAN: Make the agent loop work end-to-end

## Objective

Make the harness execute a complete planner -> coder -> patcher -> executor -> critic loop reliably, using the current local LLM setup as the primary driver. The first milestone is a working loop, not a perfect agent.

## Current assessment

The project is in a good foundation state:

- The local LLM client is configurable and works with Ollama.
- The graph structure is present and the main entrypoint runs.
- The unit test suite is green: 14 tests pass.

The remaining blocker is end-to-end behavior. The current run fails because the model produces a patch that attempts to create a file that already exists, and the current patching flow treats that as a hard failure. As a result, the graph stops in a failed state before the loop can continue meaningfully.

## Primary goal for the next iteration

Deliver a robust, minimal loop that can:

1. Generate a patch.
2. Apply it safely.
3. Run the verification command.
4. Decide whether to stop or retry with context.

This should be implemented as a stable, extensible loop rather than a special-case workaround.

## Proposed implementation plan

### 1. Stabilize the patching contract

Focus on making patch application deterministic and predictable.

- Make patch application idempotent for the common case where a patch tries to create a file that already exists with matching content.
- Treat matching already-applied content as success, not failure.
- Handle conflicting cases explicitly with a clear error message.
- Preserve the patch and result in state so the next iteration can reason about what happened.

Why this matters:
The current failure is not a model problem alone; it is a loop robustness problem. The patcher must be able to distinguish between “already done” and “conflict”.

### 2. Make the loop resilient, not brittle

The graph should be able to recover from a failed patch without collapsing immediately.

- Keep the current graph shape, but make the critic and retry logic more explicit.
- Store useful context for retries, including the last patch, patch result, and execution output.
- Add a clear “no-op” or “already applied” path so the loop can continue when the change is effectively complete.

This keeps the system expandable for later improvements such as richer planning, better prompt tuning, or multi-step code changes.

### 3. Improve state and observability

The loop should be easier to debug when it fails.

- Add a small, structured log trail to state for the last patch, patch success/failure, and test output.
- Make the final result more informative than a bare status string.
- Keep the state schema explicit so future nodes can use it without ad-hoc assumptions.

### 4. Add regression tests around the core loop

Before broadening functionality, lock in behavior that matters.

- Add tests for patch idempotency when a new-file patch targets an existing file with matching contents.
- Add tests for the graph path when patching succeeds and when it fails.
- Keep tests focused on behavior rather than implementation details.

### 5. Verify against the real harness

Once the above is in place:

- Run the harness end-to-end with the local LLM.
- Confirm the loop reaches execution and finishes with a meaningful success or failure state.
- Only after that, consider improving the planner or coder prompts.

## Scope for this milestone

This milestone should be intentionally narrow:

- Make the loop work for a simple task.
- Support one or two iteration cycles cleanly.
- Keep the architecture simple and understandable.

## Out of scope for now

- Advanced planning or memory systems.
- Complex patch generation strategies.
- Full autonomous debugging beyond a basic retry loop.
- Broad prompt optimization.

## Definition of done

The milestone is complete when:

- The harness runs from the main entrypoint without ending in an immediate failed state for a simple task.
- A generated patch can be applied successfully or recognized as already applied.
- The executor runs and the critic produces a clear next step.
- The behavior is covered by automated tests.
