# Engineering and Product Justification
## Athena — Tech Gadgets Inc. Customer Support Resolution Agent

## Architecture

```text
Customer input
    ↓
Deterministic safety pre-check
    ↓
LLM-based intent decomposition
    ↓
RAG retrieval over versioned knowledge_base/*.md
    ↓
LangChain tool-calling agent
    ↓
Adaptive tone and bounded session memory
    ↓
Observability, sanitized logging, and fallback
    ↓
Structured customer response or human escalation
```

The pre-check handles unsafe requests, high-risk escalation language, and sensitive payment information before the LLM/tool path. Passed requests are decomposed only when they contain genuinely independent topics. Each task receives relevant policy context and may use scoped read-only tools such as `lookup_order` or `check_warranty`. The full composition is reused by Phases 6–9.

## Key decisions and trade-offs

### LangChain single agent

A single customer-support workflow needs one entity to triage, retrieve, call tools, and answer. LangChain provides `ChatOpenAI`, bound tools, FAISS integration, and LangSmith compatibility without hand-building function-call schemas. The trade-off is a larger dependency surface than a framework-free client.

### FAISS over a managed vector database

The demonstration knowledge base is small Markdown content. An in-memory FAISS index avoids another service, is easy to reproduce locally, and is fast for the use case. A production system would persist and incrementally update the index as policy volume and change frequency grow.

### `gpt-4o-mini`

Tier-1 support benefits from consistent, low-latency, cost-conscious responses more than maximum reasoning depth. Temperature is kept low for predictable tool selection. Ambiguous, legal, security, and unresolved cases have an escalation path rather than relying on deeper autonomous reasoning.

### Deterministic safety before the LLM

Safety-critical refusals and escalation routes must not depend on probabilistic model behavior. Regex pre-checks run first, while prompt-level grounding and tool guardrails provide defense in depth. This design explains why all prompt variants produced the same unsafe-request refusal in the controlled comparison.

### LLM decomposition with explicit criteria

A heuristic split on “and” is cheap but can split ordinary supporting clauses or miss topic changes. LLM decomposition handles natural language better, but it introduced a real failure: unauthorized-purchase language was split into duplicate security tasks. The prompt was corrected with explicit criteria and worked examples. Genuine multi-intent requests still split; single-topic clauses remain together.

### Bounded memory

`SessionMemory` retains a bounded recent window, supporting normal 3–8-turn customer sessions without unbounded token growth. A production deployment would use authenticated, persistent per-customer storage and a clear retention policy.

## Safety, privacy, and escalation

| Layer | Mechanism | Purpose |
|---|---|---|
| Pre-check | Regex for unsafe terms, card patterns, legal/high-risk language | Refuse, protect, or escalate before LLM/tools |
| Prompt/RAG | Never fabricate; state uncertainty; escalate instead of guessing | Improve grounded behavior |
| Tool guardrails | Read-only tools, verified IDs, bounded iterations | Prevent unauthorized or invented actions |
| Monitoring boundary | Sanitization before local/LangSmith logging | Keep raw PII out of traces |

Legal threats, unauthorized-purchase incidents, and repeated unresolved complaints are escalation cases. Athena does not autonomously execute irreversible financial or account actions. Safety refusals remain active when tone adaptation is enabled.

## Reliability and graceful degradation

| Failure | Behavior |
|---|---|
| Missing LLM key/API failure | Offline status or deterministic fallback |
| Embedding failure | Keyword-overlap retrieval fallback |
| Tool failure | Error/offline status with bounded loop |
| Decomposition failure | Heuristic `and` split fallback |
| Tone adaptation failure | Professional default |
| Monitoring exception | Sanitized deterministic runtime fallback |
| Per-case evaluation crash | Record case error; continue suite |
| LangSmith unavailable | Local-only metrics and informational status |

These fallbacks ensure that an infrastructure failure does not become a raw exception shown to a customer.

## Evaluation evidence

The final evaluation suite contains **20 test cases** and reports an overall score of **89%** across the displayed categories: normal resolution 90%, safety refusal 93%, escalation 100%, edge cases 80%, knowledge gap 90%, and multi-turn 85%.

The strongest engineering evidence is the reproduced decomposition defect and fix. Before the fix, the unauthorized-purchases sentence produced two duplicate tasks. After the prompt rewrite, it produces one task, while “check my order and explain warranty policy” still produces two independent tasks. Additional evidence includes the correctly handled 45-day return tier, invalid order refusal to fabricate, contextual follow-up, safety refusal, legal/security escalation, knowledge gaps, and PII filtering before LangSmith.

## Deployment assumptions and limitations

- Demonstration order data is mocked; production needs authenticated CRM/order integrations.
- Authentication and authorization are not implemented in the Streamlit demo.
- Persistent customer sessions, rate limits, load testing, and operational dashboards remain production work.
- English is the supported language.
- LangSmith availability may vary by endpoint/account; local sanitized metrics remain the fallback.
- The knowledge base must be versioned and maintained by Customer Support Operations.

## Phase evolution

| Phase | Change | Reason |
|---|---|---|
| 2 → 3 | Rules to real LLM prompts | Handle natural language and nuance |
| 3 → 4 | Ungrounded answers to RAG | Reduce policy hallucination |
| 4 → 5 | Answers to scoped tool calls | Verify order and warranty facts |
| 5 → 6 | Single-shot to planning and memory | Handle multi-intent and follow-up context |
| 6 → 7 | Static tone to feedback adaptation | Improve customer experience without retraining |
| 7 → 8 | Direct calls to tracing and fallback | Capture latency and survive failures |
| 8 → 9 | Spot checks to a 20-case suite | Measure quality, safety, escalation, and regressions |

Athena is therefore not justified as “an LLM chatbot.” It is justified as a layered support operating capability in which deterministic controls, grounded knowledge, verified tools, bounded planning, observability, and human escalation each address a different operational risk.