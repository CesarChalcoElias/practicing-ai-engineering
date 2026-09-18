# Week 1 Exercises: Reliable LLM Interfaces

This week's objective is to move from “calling an LLM API” to “engineering an LLM component with an explicit software contract, observable failure modes, and reproducible experiments.” The exercises build on one another: first establish an application-owned provider boundary, then make its outcomes explicit, and finally use that contract to run a reproducible evaluation baseline.

## Learning Outcomes

By completing the exercises, I should be able to:

- Design a provider-independent model interface.
- Use typed requests and typed results.
- Distinguish transport success from application success.
- Represent different LLM failure modes explicitly.
- Separate schema validation from semantic validation.
- Capture experimental metadata for reproducibility.
- Build the first small evaluation dataset for an LLM application.

## Exercise 1: Build a Minimal Model Provider Adapter

### Objective

Introduce a boundary between application code and the LLM provider. The application should not directly depend on provider-specific API response objects.

The conceptual boundary is:

```text
Application
Model Adapter
LLM Provider
```

### Task

Design and implement a minimal provider adapter that:

- Accepts a typed request.
- Calls one LLM provider.
- Returns a typed result.
- Prevents provider-specific response objects from leaking into application code.
- Records the exact model identifier used.
- Can eventually support another provider without changing calling code.

Use Python type models such as Pydantic models or dataclasses. Choose the class names and precise field types yourself; do not expand this into a larger framework.

The request should contain at minimum:

- Input text.
- Request identifier.

The result should eventually contain information such as:

- Request identifier.
- Status.
- Generated result when available.
- Model identifier.
- Token usage when available.
- Latency.

### Engineering Constraints

- Business logic must not call the provider SDK directly.
- Provider-specific parsing belongs inside the adapter.
- API credentials must come from environment variables.
- The model identifier should be configurable.
- Do not introduce LangChain, LangGraph, Google ADK, or another agent framework.
- Do not implement an agent.
- Keep the implementation intentionally small.

### Questions I Should Answer Before Coding

- What information should belong to the request contract?
- What information should belong to the response contract?
- Which provider-specific details should remain hidden?
- What would need to change if the provider were replaced tomorrow?
- Which fields are required for debugging and reproducibility?

### Acceptance Criteria

The exercise is complete when:

- A typed request can be passed to the adapter.
- A typed result is always returned for a normal successful request.
- Application code does not depend on the provider SDK's response type.
- The exact model identifier is observable.
- A second hypothetical provider could implement the same application-facing contract.

### Follow-up: Verify the Contract with a Second Provider

After the single-provider adapter works, implement a second provider adapter as a contract exercise. You may use another provider you have access to, or a deterministic fake provider if you want to avoid another live API call.

The second adapter must:

- Implement the same application-facing operation as the first adapter.
- Accept the same typed request.
- Return the same typed result.
- Keep its provider SDK calls and response parsing inside its own adapter.
- Use its own configured API credential and model identifier.
- Leave application calling code unchanged when the selected provider changes.

Do not add fallback logic, provider competition, routing heuristics, or a provider abstraction framework. The purpose is to test whether your contract is genuinely provider-independent.

#### Follow-up Questions

- What code remained unchanged when you switched providers?
- Which fields required provider-specific translation?
- Did either provider omit token usage or return it in a different shape?
- Which assumptions in the first adapter were accidentally provider-specific?
- Where should provider selection occur, and where should it not occur?

#### Follow-up Acceptance Criteria

The follow-up is complete when:

- Two adapters satisfy the same application-facing contract.
- The same request model can be sent through either adapter.
- The same result model is returned by either adapter.
- Application code does not import either provider SDK.
- Provider selection can change through configuration or adapter construction rather than application logic changes.
- At least one provider-specific difference is documented and contained inside its adapter.

### Reflection

Write 3 to 5 sentences answering:

> What responsibility belongs to the model adapter, and what responsibility should remain outside it?

## Exercise 2: Model Failure Modes Explicitly

### Objective

An LLM request cannot be modeled simply as success or failure. The application needs different observable outcomes because each may require different handling, retry policies, metrics, and user behavior.

### Required Outcome Types

Represent at least these outcomes:

- **Success:** The provider completed the request and the returned result passed the required validation.
- **Refusal:** The model intentionally declined to complete the requested task. A refusal is not equivalent to infrastructure failure.
- **Invalid output:** The provider responded, but the returned content does not satisfy the application's contract. Distinguish schema validation from semantic validation. For example, a JSON field can be structurally valid while its percentage is outside the allowed business range.
- **Timeout:** The request exceeded the application's allowed deadline. Represent timeout explicitly rather than converting it into `None`, empty text, or a generic failure.
- **Truncation:** The model produced only part of the expected output because generation ended before the task was completed. Partial text must not automatically be interpreted as success.

### Task

Extend Exercise 1 so that every model interaction produces one explicit outcome. Deliberately create or simulate examples of each outcome. Deterministic simulation or mocks are acceptable for failure modes that are difficult to force through a live model API.

### Failure Injection

Include at least one test case or fixture for each:

- Normal successful response.
- Simulated refusal.
- Malformed or semantically invalid result.
- Timeout.
- Truncated result.

Focus on the application's behavior, not on convincing the provider to naturally produce each failure.

### Questions I Should Answer

- Which outcomes are safe to retry?
- Which outcomes should not automatically be retried?
- Can an HTTP 200 response still represent application failure?
- Why is valid JSON insufficient to establish correctness?
- Why is partial output dangerous?
- Where should semantic validation live?

Do not answer these questions in the exercise guide. Work out and document your answers as part of the exercise.

### Acceptance Criteria

The exercise is complete when:

- All five outcomes are represented explicitly.
- None of them silently becomes success.
- Schema-invalid output is detectable.
- At least one schema-valid but semantically invalid example is detectable.
- Timeout is distinguishable from refusal.
- Truncation is distinguishable from success.
- Tests or fixtures demonstrate every outcome.

### Reflection

Write a short answer to:

> Why should an LLM be treated as an unreliable semantic dependency even when the provider infrastructure is healthy?

## Exercise 3: Build a 20-Case Evaluation Baseline

### Objective

Create the first small evaluation dataset and experimental baseline. The objective is to make behavior measurable and reproducible, not yet to optimize the model.

### Task

Create 20 synthetic requests. Do not make them all easy happy-path examples. Include a mixture such as:

- Straightforward requests.
- Ambiguous requests.
- Missing information.
- Unexpected formatting.
- Contradictory information.
- Unusually long inputs.
- Boundary values.
- Cases likely to produce invalid output.

Choose a simple, synthetic task domain. Possible examples include purchase request extraction, support request classification, or structured information extraction. Do not use production or confidential data.

### Required Metadata

For every execution, record:

- Case identifier.
- Request identifier.
- Model identifier.
- Prompt version.
- Timestamp.
- Input token usage when available.
- Output token usage when available.
- Latency.
- Final outcome.
- Optional error category.
- Optional short observation.

Record both model version and prompt version so a result can be tied to the exact model and instructions used. An explicit prompt version is required even when there is only one prompt initially, for example `v1`. Do not build a prompt registry for this exercise.

### Experiment Output

Generate a machine-readable artifact that supports later inspection of individual cases. Choose a format such as JSON Lines, JSON, CSV, or SQLite. JSON Lines or SQLite is recommended for this exercise, but the choice is yours.

### Baseline Summary

Produce a small summary containing at minimum:

- Total cases.
- Success count.
- Refusal count.
- Invalid-output count.
- Timeout count.
- Truncation count.
- Average latency.
- Total input tokens.
- Total output tokens.

If the selected provider does not expose a metric, record it as unavailable rather than inventing a value.

### Important Constraint

Do not optimize prompts during the first run. This run becomes the baseline. Changing the prompt while constructing the baseline would contaminate the comparison.

### Questions I Should Answer

- Which cases failed most often?
- Were failures caused by the model, validation, or infrastructure?
- Which cases exposed weaknesses in the request or result contract?
- What information would I need to compare prompt v1 with prompt v2?
- Which metadata would I regret not collecting after 100 experiments?
- Why is average latency alone insufficient for a production system?

Do not answer these questions in the exercise guide. Use the experiment results to develop and record your answers.

### Acceptance Criteria

The exercise is complete when:

- Exactly 20 or more synthetic cases exist.
- Every case has a stable case ID.
- Every execution records its model and prompt versions.
- Every execution receives one explicit outcome.
- Token usage is recorded when available.
- Latency is measured.
- Results are persisted in a machine-readable artifact.
- A baseline summary can be generated.
- The original baseline remains unchanged after it is produced.

### Reflection

Write approximately one paragraph answering:

> What did I learn from the 20 executions that I could not have learned from manually testing three or four prompts?

# Week 1 Completion Checklist

- [ ] Provider-independent model adapter exists.
- [ ] Typed request contract exists.
- [ ] Typed result contract exists.
- [ ] Success is explicit.
- [ ] Refusal is explicit.
- [ ] Invalid output is explicit.
- [ ] Timeout is explicit.
- [ ] Truncation is explicit.
- [ ] Schema validation exists.
- [ ] Semantic validation exists.
- [ ] At least one failure example exists for every outcome.
- [ ] 20 or more synthetic evaluation cases exist.
- [ ] Model identifier is recorded.
- [ ] Prompt version is recorded.
- [ ] Token usage is recorded when available.
- [ ] Latency is recorded.
- [ ] Results are persisted.
- [ ] Baseline summary exists.
- [ ] Original baseline is preserved.
- [ ] Week 1 reflections are written.

# What Not to Build Yet

Do not add:

- RAG.
- Embeddings.
- Vector databases.
- Memory.
- Tools.
- Agent loops.
- LangChain.
- LangGraph.
- Google ADK.
- MCP.
- Multi-agent systems.
- Production UI.
- Elaborate observability platforms.

These are intentionally deferred because Week 1 is about understanding the reliability contract of a single model interaction.

# Definition of Done

Week 1 is complete when I can explain and demonstrate:

1. Why an LLM provider should sit behind an application-owned interface.
2. Why provider success does not imply task success.
3. Why schema correctness does not imply semantic correctness.
4. Why refusal, timeout, truncation, and invalid output are different engineering states.
5. How to reproduce a specific experiment using its case ID, model version, and prompt version.
6. How the 20-case baseline becomes the foundation for later evaluation work.

Do not include solutions to these questions in the exercise guide.
