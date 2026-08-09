# Engineering & Product Justification

## Customer Support AI Resolution Agent

---

### 1. Architecture Overview

┌─────────────────────────────────────────────────────────────────┐
│                    Customer Input                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              Safety Pre-Check (Regex + Pattern)                   │
│  • PII detection (credit cards, SSN, phones)                     │
│  • Unsafe request patterns (hack, exploit, etc.)                 │
│  • Returns immediately if triggered (< 50ms)                     │
└─────────────────────┬───────────────────────────────────────────┘
                      │ (passes check)
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              RAG / Knowledge Retrieval (FAISS)                    │
│  • Embeds query → similarity search                              │
│  • Returns top-3 relevant policy/product chunks                  │
│  • Provides grounding context for LLM                            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              LangChain Agent (GPT-4o-mini)                        │
│  • System prompt (v3_safety_first)                               │
│  • Conversation memory (last 10 turns)                           │
│  • Session context (sentiment, issues discussed)                 │
│  • Behaviour instructions (from feedback adaptation)             │
│  • Available tools: order_lookup, warranty_check,                │
│    escalate_to_human, create_return_request                      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              Post-Processing & Response                           │
│  • Sanitize logs (hash PII)                                      │
│  • Record metrics (latency, status)                              │
│  • Update conversation memory                                    │
│  • Return structured response + metadata                         │
└─────────────────────────────────────────────────────────────────┘

```

---

### 2. Design Decisions & Tradeoffs

#### Decision 1: LangChain over CrewAI or Flowise

**Choice:** LangChain (single-agent with tools)

**Why:**

- Customer support is inherently a single-agent workflow — one entity handles the conversation
- CrewAI's multi-agent orchestration adds complexity without benefit here (no need for "researcher" + "writer" + "reviewer" agents)
- LangChain's tool-calling abstraction directly maps to support actions (lookup, escalate, create ticket)
- Mature ecosystem with FAISS integration, memory modules, and OpenAI tools support

**Tradeoff accepted:** Less modular than CrewAI for hypothetical future multi-agent needs. Mitigated by clean separation of concerns in code.

#### Decision 2: FAISS over Chroma for vector store

**Choice:** FAISS (in-memory, local)

**Why:**

- Knowledge base is small (< 100 documents) — FAISS is faster for small datasets
- No external service dependency — simpler deployment
- CPU-based FAISS is sufficient for our scale
- Reproducible without Docker/server setup

**Tradeoff accepted:** Not suitable for very large knowledge bases (10K+ docs). For production scale, would migrate to Chroma or Pinecone.

#### Decision 3: GPT-4o-mini over GPT-4o

**Choice:** gpt-4o-mini (temperature 0.3)

**Why:**

- Customer support responses should be consistent (low temperature)
- gpt-4o-mini is 10x cheaper and 2x faster than gpt-4o
- For policy-grounded responses with explicit context, mini performs comparably
- Latency is critical for customer support (< 3s target)

**Tradeoff accepted:** Slightly lower reasoning capability for extremely complex edge cases. Mitigated by escalation to human for complex issues.

#### Decision 4: Pre-check safety filter BEFORE LLM

**Choice:** Regex-based safety pre-check runs before sending to LLM

**Why:**

- Deterministic safety (100% consistent, no LLM randomness)
- ~50ms vs 2000ms+ for LLM evaluation
- Catches PII exposure before it reaches the API (data never sent to OpenAI)
- Defense-in-depth: LLM prompt also has safety rules as second layer

**Tradeoff accepted:** Regex patterns are rigid — may miss creative/obfuscated unsafe requests. The LLM's safety rules act as second layer for these cases.

#### Decision 5: Session-scoped rolling memory (10 turns) over full history

**Choice:** A custom rolling buffer of the latest 10 complete user/assistant turns.

**Why:**

- Customer support sessions are typically 3-8 turns
- Window prevents context explosion for rare long sessions
- Reduces token cost per query
- Avoids carrying stale context from much earlier in conversation
- The buffer stores LangChain `HumanMessage` and `AIMessage` objects and passes
  them to the agent as `chat_history` for follow-up queries
- `/reset` explicitly clears the buffer before a new customer session

**Tradeoff accepted:** If a customer references something from more than 10
turns ago, the agent may not recall it. The current local API has one in-memory
agent instance, so it is appropriate for a single-user demonstration only. A
production deployment would use a session ID plus isolated, persistent or
checkpointed storage per customer.

---

### 3. Safety Approach

**Philosophy:** Safety is treated as a feature, not a constraint. The agent is designed to fail-safe.

**Three-Layer Safety Model:**

| Layer | Mechanism | Coverage | Speed |
| ------- | ----------- | ---------- | ------- |
| 1. Pre-check | Regex patterns | PII, known unsafe terms | < 50ms |
| 2. Prompt rules | LLM system prompt | Policy compliance, fabrication prevention | At inference time |
| 3. Tool guardrails | Tool-level validation | Order eligibility, action limits | At tool execution |

**Escalation Triggers (automatic):**

- Customer mentions legal action (lawyer, attorney, sue)
- Account security concerns (hacked, unauthorized access)
- Repeated failures (same issue unresolved after 2 attempts)
- Agent confidence below threshold
- Customer explicitly requests human agent

**PII-Safe Logging:**

- All logs run through `sanitize_for_log()` before writing
- Emails, phone numbers, order IDs are hashed (SHA-256, first 8 chars)
- Full credit card numbers are never stored or processed
- Conversation content is NOT logged — only metadata (intent, status, timing)

---

### 4. Deployment Assumptions & Limitations

**Assumptions:**

- OpenAI API is available and within rate limits
- Knowledge base is updated regularly by support ops team
- Human escalation team available during business hours
- Customers interact via text (not voice, image, or video)
- Single concurrent session per customer

**Current Limitations:**

- No real database integration (uses mock data for demonstration)
- No authentication/authorization layer (production would need OAuth)
- No rate limiting beyond tool iteration caps
- English-only support
- No real-time learning (feedback adaptation is batch, not per-query)
- No A/B testing infrastructure built-in
- Memory is process-local and is not isolated between concurrent API clients;
  production would require session IDs and a per-customer store

**Production Readiness Checklist:**

- [x] Error handling with graceful fallbacks
- [x] PII-safe logging
- [x] Configurable via environment variables
- [x] Reproducible (requirements.txt, clear run instructions)
- [x] Metrics collection
- [ ] Authentication (would add for production)
- [ ] Rate limiting (would add for production)
- [ ] Monitoring/alerting dashboard (would add for production)
- [ ] Load testing (would add for production)

---

### 5. Evolution Summary

| Phase | What Changed | Why |
| ------- | ------------- | ----- |
| 2 → 3 | Keyword matching → LLM | Handle natural language, context, nuance |
| 3 → 4 | Generic LLM → RAG-grounded | Eliminate hallucination, ensure policy accuracy |
| 4 → 5 | Passive answers → Tool actions | Actually resolve issues (lookups, returns, escalations) |
| 5 → 6 | Stateless → Memory + Planning | Handle multi-turn, avoid repetition, decompose complex queries |
| 6 → 7 | Fixed behaviour → Adaptive | Respond to feedback, improve tone and detail |
| 7 → 8 | Dev mode → Deployment-ready | Logging, error handling, configuration, metrics |
| 8 → 9 | Untested → Evaluated | Systematic testing, failure analysis, quality metrics |

Each phase was additive, building on the previous. The baseline's limitations (documented in Phase 2) motivated each subsequent improvement.
