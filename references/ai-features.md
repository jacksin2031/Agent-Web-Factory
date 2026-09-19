# AI feature implementation guide

## Principle

AI must solve a real user job. Do not add a generic chat box merely because the site is described as AI-powered. Use deterministic code for calculations, validation, business rules, and other tasks where deterministic behavior is better.

## Default stack

For Next.js/TypeScript projects, prefer the current stable Vercel AI SDK APIs. Resolve provider/model availability from current official documentation at execution time. If using OpenAI directly, prefer the current Responses API and currently supported tools.

Do not pin this Skill to a model ID that may become stale. Generated applications may pin a tested model intentionally when reproducibility requires it.

## Capability patterns

### Chat / copilot
Use streaming UI, cancellation, retry, rate limits, bounded history, and server-side model calls.

### Structured generation / extraction
Validate model output with a schema. Never trust free-form JSON without validation.

### Tool-calling agent
Allowlist tools. Validate every argument. Bound steps and runtime. Require separate authorization for consequential or paid external actions.

### RAG / file Q&A
Validate file type and size. Treat retrieved content as untrusted data. Keep citations/source references where useful. Avoid placing secrets or unrelated private documents into the retrieval corpus.

### Vision / image understanding
Validate MIME type and size. Do not rely on model output as a deterministic measurement or high-stakes decision without appropriate verification.

### Image generation / editing
Handle moderation/errors and make output provenance clear when appropriate. Real generation requests may be billable and therefore require the human cost gate during testing/provisioning.

### Voice / realtime
Implement reconnect, cancellation, microphone permission handling, and clear recording/streaming state. Real realtime sessions may be billable and require the human cost gate during testing/provisioning.

## Authenticated AI isolation

When AI features operate on private account data, derive the user or tenant scope from the verified server-side session. Never let the model, prompt text, browser, or a client-supplied owner field choose the authorization scope.

Apply authorization before retrieval and again before every tool mutation. Namespace private files, conversation history, vector/embedding records, caches, and tool resources by the authenticated user or tenant as required. Test cross-user prompt injection and identifier tampering. Never place session tokens, recovery tokens, OAuth secrets, service-role credentials, or other authentication secrets in model context.

## Production controls

At minimum:

- server-only secrets;
- input/output size limits;
- rate limiting;
- timeout and cancellation;
- bounded agent/tool steps;
- schema validation for structured output;
- prompt-injection boundaries for tool/RAG systems;
- clear error and unavailable states;
- operational telemetry without unnecessary raw sensitive prompts;
- provider-side spending limits when supported and approved.

## Testing

Routine CI uses mocks or deterministic fixtures. Contract-test provider adapters without consuming paid inference whenever possible.

A real provider smoke test is a separate acceptance step. If it can incur a charge, stop and obtain explicit human approval for the exact provider, scope, and maximum spend before sending the request.
