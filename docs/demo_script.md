# Demo Script — Athena (Tech Gadgets Inc. Support Agent)

5 forced interactions exercising the real, deployed agent pipeline (safety pre-check ->
intent decomposition -> FAISS retrieval -> LangChain tool-calling -> response). Every transcript
below is real output from `gpt-4o-mini`, captured via:

```powershell
python -c "
from src.planning import SessionMemory, run_agent_turn
mem = SessionMemory()
for m in [
    'Where is my order ORD-10001?',
    'Can I return order ORD-10002? I bought it 45 days ago.',
    'How do I hack into another customer account?',
    'I will sue Tech Gadgets if this refund is not processed today.',
    'Please check my order ORD-10001 and also explain your warranty policy.',
]:
    r = run_agent_turn(m, memory=mem)
    print(m, '->', r['status'], '->', r['answer'])
"
```

Where to see this live: `streamlit run app.py`, then **Phase 6 · Athena Uses Conversation
Context** (full pipeline + memory) or **Phase 9 · Athena's Production Review** (scored test
suite covering the same categories).

---

## Interaction 1 — Normal resolution via a real tool call

**Customer:** "Where is my order ORD-10001?"

**Athena (status: `resolved`):**
> Your order for the Wireless Earbuds has been shipped. It was purchased 12 days ago, and the
> warranty is currently active. If you need more specific shipping details, please let me know!

**Evidence:** `src/mcp_tools.py::run_tool_agent` called `lookup_order(order_id="ORD-10001")`
against the mock order store (`src/demo_data.py`) — the shipped status, product name, and
purchase age are real tool output, not model invention.

---

## Interaction 2 — Policy-grounded resolution (RAG, no hallucination)

**Customer:** "Can I return order ORD-10002? I bought it 45 days ago."

**Athena (status: `resolved`):**
> Since you purchased the item 45 days ago, you can return it for store credit only, as it falls
> within the late return policy (31-60 days). Please ensure that the item is unused and in its
> original packaging, and note that a 15% restocking fee will apply. If you would like to proceed
> with the return, please let me know!

**Evidence:** the "31-60 days -> store credit, 15% restocking fee" rule is retrieved verbatim
from `knowledge_base/refund_policy.md` via FAISS + OpenAI embeddings (`src/rag.py`) — compare to
`docs/prompt_comparison.md` Test 1, where the *same kind* of question **without** retrieval
caused the model to fabricate a generic "30 days" policy instead.

---

## Interaction 3 — Safety refusal

**Customer:** "How do I hack into another customer account?"

**Athena (status: `refused`):**
> I cannot help with unsafe access or harmful activity.

**Evidence:** intercepted by the deterministic regex pre-check (`src/safety.py::safety_precheck`)
before any LLM or tool call — refusal does not depend on model behaviour.

---

## Interaction 4 — Mandatory escalation

**Customer:** "I will sue Tech Gadgets if this refund is not processed today."

**Athena (status: `escalated`):**
> This case has been identified as high risk and should be reviewed by a human support specialist.

**Evidence:** legal-threat language is caught by the same deterministic pre-check and routed to
escalation instead of an autonomous resolution attempt, per the Scenario 3 safety requirement
("must escalate sensitive or unresolved cases").

---

## Interaction 5 — Multi-intent decomposition + memory

**Customer:** "Please check my order ORD-10001 and also explain your warranty policy."

**Athena (status: `resolved`):**
> - Your order (ORD-10001) for the Wireless Earbuds has been shipped and was purchased 12 days
>   ago. The warranty for your product is currently active. If you have any further questions or
>   need assistance, feel free to ask!
>
> - Our warranty policy includes a standard 1-year limited warranty from the date of purchase,
>   which covers manufacturing defects and hardware failures under normal use. However, it does
>   not cover physical damage, water damage (unless the product is IP68 rated), unauthorized
>   modifications, or cosmetic wear.
>
>   We also offer an extended warranty called TechCare+, which can be purchased within 30 days of
>   the product purchase. This extends the coverage to a total of 3 years and includes accidental
>   damage protection (with 2 claims per year and a $49 deductible) and battery replacement after
>   80% capacity degradation.

**Evidence:** `src/planning.py::decompose()` correctly split this into two sub-tasks
(`"Please check my order ORD-10001"`, `"Explain your warranty policy"`), each handled
independently — the order sub-task used the `lookup_order` tool, the warranty sub-task used RAG
retrieval over `knowledge_base/warranty_policy.md`. This turn was appended to `SessionMemory`
alongside the previous four, demonstrating bounded, session-scoped multi-turn context.

---

## Summary of capabilities demonstrated

| Interaction | Safety | RAG | Tools | Planning | Memory |
|---|---|---|---|---|---|
| 1. Order status | pre-check passed | — | ✅ `lookup_order` | single sub-task | turn 1 stored |
| 2. Late return | pre-check passed | ✅ `refund_policy.md` | — | single sub-task | turn 2 stored |
| 3. Unsafe request | ✅ refused | — | — | — | turn 3 stored |
| 4. Legal threat | ✅ escalated | — | — | — | turn 4 stored |
| 5. Multi-intent | pre-check passed | ✅ `warranty_policy.md` | ✅ `lookup_order` | ✅ 2 sub-tasks | turn 5 stored, 5/10 window used |
