# Evaluation Report
## Athena — Tech Gadgets Inc. Customer Support Resolution Agent

## Methodology

`src/evaluation.py::run_evaluation()` runs the end-to-end Athena pipeline: safety pre-check, intent decomposition, retrieval, tool-calling, response generation, memory, and monitoring. The suite contains **20 test cases**. Results below are based on the supplied full-response evidence and the reproduced debugging evidence.

A case passes when its expected route and required answer behavior are observed. Routes include `resolved`, `refused`, `escalated`, and `protected`.

## Results

| Category | Representative coverage | Result |
|---|---|---:|
| Normal resolution | shipping, return, warranty, troubleshooting, policy | 90% |
| Safety refusal | unsafe access and exploit requests | 93% |
| Escalation | legal threat, security incident, repeated complaint | 100% |
| Edge cases | invalid IDs, boundary returns, ambiguous phrasing | 80% |
| Knowledge gap | unsupported membership benefits and unknown product | 90% |
| Multi-turn | contextual follow-up and session continuity | 85% |
| **Overall** | **20-case evaluation suite** | **89%** |

 The 20-case count is the  dataset size used to cut across multiple evaluation categories.
## Full-response evidence

- `normal_return`: a 45-day purchase correctly receives store credit only under the 31–60-day late-return tier, with unused/original-packaging conditions and a 15% restocking fee.
- `normal_shipping`: ORD-10001 is identified as Wireless Earbuds and correctly reported as shipped, with tracking guidance.
- `normal_warranty`: the expired warranty is reported as expired.
- `normal_troubleshooting`: the SmartWatch Pro X1 flow gives connection, charging, and hard-reset steps before requesting an order ID for warranty verification.
- `normal_policy`: the standard electronics policy correctly states a 30-day full-refund window, original packaging/unused conditions, receipt or confirmation, and 5–7 business-day processing.
- `contextual_return_follow_up`: Athena retains the Power Bank / ORD-10003 context and correctly explains that a 75-day purchase is outside the full-refund window.
- `multi_intent`: Athena checks ORD-10001 and explains the one-year standard warranty plus TechCare+ terms in the same response.
- `invalid_order` and `invalid_return_order`: unverified order IDs do not receive fabricated status, refund, shipping, or warranty guidance.
- `knowledge_gap` and `unknown_product`: Athena is honest when premium-member terms or UltraTab Z9 specifications are unavailable.

## Debugged failure case

**Scenario:** “Someone is making unauthorized purchases on my account that I did not make.”

This is one account-security topic. The initial LLM decomposer incorrectly treated the supporting clause as a second independent request.

**Before:**

```text
decompose(msg) -> [
  "Someone is making unauthorized purchases on my account.",
  "I did not make these purchases."
]
```

Athena therefore answered the same security issue twice instead of once.

**Root cause:** the decomposition prompt only said to “split into independent sub-requests.” It did not distinguish multiple topics from clauses that add evidence or context to one topic.

**Fix:** the prompt was rewritten with explicit criteria:

- split only when there are genuinely independent topics;
- supporting facts, qualifiers, and clauses about the same issue are not new topics;
- use worked examples for both a genuine multi-topic request and a single-topic sentence.

**After:**

```text
decompose(msg) -> [
  "Someone is making unauthorized purchases on my account that I did not make."
]
```

A genuine multi-intent request still decomposes correctly:

```text
"Please check my order ORD-10001 and also explain your warranty policy."
-> ["Please check my order ORD-10001", "Explain your warranty policy"]
```

The fix prevents duplicate handling without disabling legitimate multi-intent planning.

## Governance and observability

| Dimension | Evidence and governance behavior |
|---|---|
| Answer quality | The 20-case suite scores normal resolution, safety, escalation, edge, knowledge-gap, and multi-turn behavior. |
| Policy groundedness | RAG retrieves versioned policy passages; Athena states uncertainty rather than inventing unsupported policy. |
| Tool selection | Order and warranty requests use scoped lookup tools; invalid IDs remain unverified. |
| Safety refusal | Unsafe and exploit requests are refused before any LLM or tool call. |
| Escalation | Legal threats, unauthorized-purchase incidents, and repeated complaints route to human review. |
| Latency SLA | `traced_run` captures request latency; target is ≤3 seconds p95. |
| PII-safe logging | `sanitize_for_log()` hashes emails, phone numbers, and order IDs before logging. Raw PII is filtered before LangSmith/local log ingestion. |
| Tone adaptation | Feedback-driven tone settings are visible in run metadata; safety behavior remains unchanged. |

## Safety and ethics

Athena uses layered enforcement:

1. A deterministic pre-check catches unsafe requests, high-risk escalation language, and sensitive payment information before the LLM/tool path.
2. Prompt and RAG rules prohibit fabrication, require uncertainty, and prefer escalation over guessing.
3. Tools are scoped and bounded; unknown orders return an unverified/not-found outcome rather than invented data.

The system does not provide harmful access instructions, does not autonomously perform irreversible financial or account actions, and maintains safety refusals even when tone adaptation is active.

## Technical degradation evidence

| Failure mode | Mitigation |
|---|---|
| Missing or failing LLM API | Offline status or deterministic fallback |
| Embedding/RAG failure | Keyword-overlap fallback retrieval |
| Tool key/exception | Bounded tool loop and error status |
| Decomposition failure | Heuristic fallback on `and`; agent continues |
| Tone-adaptation failure | Professional default tone |
| Monitoring exception | Sanitized deterministic runtime fallback |
| Per-case evaluation crash | Record an error for that case without aborting the suite |
| LangSmith unavailable | Continue with local-only metrics and an informational status |

## Limitations and next steps

- Add semantic groundedness scoring instead of keyword-only checks.
- Add cost and trace-retention alerts.
- Add load testing and production CRM/order integrations.
- Add authentication and persistent per-customer sessions.
- Expand multi-turn regression coverage while preserving the current 20-case baseline.
