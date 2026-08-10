# Engineering & Product Justification

## Athena — Tech Gadgets Inc. Customer Support Resolution Agent

---

### 1. Architecture Overview

```
                    Customer Input
                          |
                          v
   Safety Pre-Check (deterministic regex, src/safety.py)
   - PII detection (payment-card pattern)
   - Unsafe-request keywords (hack, exploit, bypass security...)
   - Legal / high-risk keywords (sue, lawyer, legal action)
   - Returns immediately if triggered — no LLM/tool call is made
                          |
                          v (passes check)
   Intent Decomposition (src/planning.py::decompose)
   - real ChatOpenAI call, splits genuinely multi-topic requests
   - single-topic / multi-sentence requests are kept as one sub-task
                          |
                          v (for each sub-task)
   RAG Retrieval (src/rag.py) — real OpenAI embeddings (text-embedding-3-small)
   in a FAISS vector store over chunked knowledge_base/*.md
                          |
                          v
   LangChain Tool-Calling Agent (src/mcp_tools.py) — ChatOpenAI (gpt-4o-mini)
   bound to lookup_order / check_warranty / escalate_to_human, grounded in the
   retrieved policy context, bounded to settings.max_tool_iterations
                          |
                          v
   Adaptive tone (src/adaptation.py) — feedback-derived tone/verbosity applied
                          |
                          v
   Observability wrapper (src/observability.py::traced_run) — latency capture,
   PII-safe log line, LangSmith tracing, graceful fallback to deterministic
   src/runtime.py logic if the live call fails
                          |
                          v
              Structured response returned to the customer
```

Each Streamlit page under `pages/` isolates one layer of this pipeline for evaluator clarity
(`pages/3_llm_integration.py` = plain LLM + prompt variants, `pages/4_rag.py` = retrieval only,
`pages/5_mcp_tools.py` = tool-calling only, `pages/6_planning_memory.py` = the full composed
pipeline with memory). `src/planning.py::run_agent_turn` is the single function that wires safety
+ decomposition + retrieval + tools + memory + feedback together and is reused by Phases 6-9.

---

### 2. Design Decisions & Tradeoffs

#### Decision 1: LangChain (Track A) over CrewAI or a framework-free build

**Choice:** LangChain, single agent with bound tools (`ChatOpenAI.bind_tools`).

**Why:**
- Customer support here is a single-agent workflow — one entity triages, retrieves, and resolves.
- LangChain's `ChatOpenAI` + `bind_tools` + `FAISS`/`OpenAIEmbeddings` integrations gave a real,
  working RAG + tool-calling agent without hand-rolling function-calling JSON schemas.
- LangSmith tracing is available out of the box via `LANGCHAIN_TRACING_V2=true`.

**Tradeoff accepted:** LangChain adds a dependency surface (and a Windows-specific FAISS/OpenMP
issue, see §4) versus a minimal framework-free client. Justified by faster, more reliable
tool-calling and retrieval code.

#### Decision 2: FAISS (in-memory) over Chroma/Pinecone

**Choice:** `langchain_community.vectorstores.FAISS`, rebuilt in-process from `knowledge_base/*.md`.

**Why:** the knowledge base is 5 small markdown files — an in-memory index is fast, has no
external service dependency, and is trivial to reproduce with `streamlit run app.py`.

**Tradeoff accepted:** the index is rebuilt on first use per process (cached after that) and is
not persisted to disk; not suitable for a large, frequently-changing knowledge base. At that
scale we would persist the index and add incremental updates.

#### Decision 3: `gpt-4o-mini`, temperature 0.3 (0 for tool-calling)

**Why:** consistent, low-cost, low-latency responses are more important than maximum reasoning
depth for Tier-1 support; temperature 0 for the tool-calling agent makes tool selection
deterministic and testable.

**Tradeoff accepted:** lower reasoning ceiling for very ambiguous cases — mitigated by the
mandatory escalation path for legal/security/unresolved cases.

#### Decision 4: Two-layer safety, deterministic layer first

**Choice:** a regex-based `safety_precheck()` (`src/safety.py`) runs before any LLM or tool call;
prompt-level rules (`src/llm_agent.py`, `src/mcp_tools.py`) are a second layer.

**Why:** refusal/escalation of known-unsafe or high-risk requests must not depend on
non-deterministic LLM behaviour. This was verified directly in `docs/prompt_comparison.md` (Test
2): all three prompt variants produced an identical refusal because the regex layer intercepted
the request before the model ever saw it.

**Tradeoff accepted:** regex patterns can miss creative/obfuscated unsafe phrasing — the prompt
layer and RAG grounding are the second line of defense for those cases.

#### Decision 5: LLM-based multi-intent decomposition, with a documented failure and fix

**Choice:** `src/planning.py::decompose()` uses a real LLM call (not a keyword split) to decide
whether a message contains multiple distinct topics.

**Why:** a purely heuristic split (on "and"/commas) either over-splits ordinary sentences or
misses topic changes phrased without a conjunction.

**Real failure found and fixed during development** (see `docs/evaluation_report.md` §3 for full
detail): the first version of the decomposition prompt over-split single-topic, multi-sentence
messages (e.g. *"Someone is making unauthorized purchases on my account that I did not make."*)
into two bogus sub-tasks. Fixed by rewriting the prompt with an explicit rule plus three
input/output worked examples. Re-verified against `evaluation/dataset.json`: 100% pass after the
fix, with genuine multi-intent requests still splitting correctly.

**Tradeoff accepted:** decomposition costs one extra LLM call per turn versus a free heuristic
split; acceptable given the correctness gain and `gpt-4o-mini`'s low latency/cost.

#### Decision 6: Session-scoped rolling memory (10 turns) over full history

**Choice:** `SessionMemory` (`src/planning.py`) keeps the last 10 user/assistant turns in
`st.session_state`, with an explicit `reset()`.

**Why:** typical support sessions are 3-8 turns; a bounded window avoids unbounded token growth
and stale context, while an explicit reset gives a clean boundary between customer sessions.

**Tradeoff accepted:** a customer referencing something from more than 10 turns ago will not be
recalled; acceptable for a single-session support interaction, and memory is per Streamlit
session (not shared across concurrent users), so a real deployment would add per-customer,
persistent session storage.

---

### 3. Safety Approach

**Philosophy:** safety is a feature, enforced deterministically wherever possible, with the LLM
as a second and third layer rather than the only line of defense.

| Layer | Mechanism | File |
|---|---|---|
| 1. Pre-check | Regex: unsafe keywords, card-number pattern, legal/high-risk keywords | `src/safety.py` |
| 2. Prompt rules | "Never fabricate", "escalate instead of guessing", intent/evidence/answer/next-step structure | `src/llm_agent.py`, `src/mcp_tools.py` |
| 3. Tool guardrails | Read-only tools only; unverifiable order IDs return `not_found` (never guessed); bounded tool-call loop | `src/mcp_tools.py`, `src/config.py` (`max_tool_iterations`) |

**Escalation triggers (automatic, deterministic):** legal-action language ("sue", "lawyer",
"legal action", "complaint"), which the pre-check catches before any model call.

**PII-safe logging:** `sanitize_for_log()` hashes emails, phone numbers, and order IDs
(SHA-256, truncated) before anything reaches `logs/`; full conversation content and raw
identifiers are never written to disk.

---

### 4. Deployment Assumptions & Limitations

**Assumptions:**
- OpenAI API key and quota are available (configured via `.env` locally, Streamlit Cloud
  **Secrets** in production — never committed to the repository).
- The knowledge base (`knowledge_base/*.md`) is maintained by the support-ops team and re-indexed
  automatically the first time it is used in a running process.
- A human escalation queue exists for the cases the agent explicitly routes to escalation.

**Current limitations:**
- No real order/CRM database — `src/demo_data.py` provides mock orders for demonstration.
- No authentication/authorization layer; a production deployment would add per-customer session
  identity instead of a single Streamlit session.
- LangSmith trace ingestion to the configured regional endpoint
  (`https://apac.smith.langchain.com`) currently returns **HTTP 405** — likely an account/plan
  limitation on that endpoint, not a code defect. `LANGCHAIN_TRACING_V2` remains enabled per the
  assignment's monitoring requirement; local latency/error capture in
  `src/observability.py::traced_run` is the primary observability evidence until this is resolved.
- On Windows, `faiss-cpu` and `numpy` can link two OpenMP runtimes and crash on import; this is
  worked around with `os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")` in `src/config.py`
  (documented here so it is not accidentally removed).
- No rate limiting beyond the tool-call iteration cap.
- English-only support; feedback adaptation is per-session, not a persisted model update.

**Production readiness checklist:**
- [x] Real LLM/RAG/tool integration (LangChain + OpenAI + FAISS), not a simulation
- [x] Two-layer deterministic + prompt-level safety, with a bounded tool-call loop
- [x] PII-safe logging
- [x] Configurable via environment variables / Streamlit secrets
- [x] Reproducible (`requirements.txt`, this document, clear run instructions in `README.md`)
- [x] Latency/error capture and graceful degradation to deterministic fallback logic
- [ ] Authentication (would add for production)
- [ ] Per-customer persistent session storage (would add for production)
- [ ] Full LangSmith trace visibility (blocked on the 405 above)
- [ ] Load testing

---

### 5. Evolution Summary

| Phase | What changed | Why |
|---|---|---|
| 2 -> 3 | Keyword/template rules -> real `ChatOpenAI` call behind 3 versioned prompts | Handle natural language, nuance, and uncertainty instead of rigid keyword matching |
| 3 -> 4 | Ungrounded LLM answers -> real OpenAI-embeddings + FAISS retrieval | Eliminate hallucination on policy questions (see the real fabrication example in `docs/prompt_comparison.md` Test 1) |
| 4 -> 5 | Passive answers -> LangChain tool-calling agent (`bind_tools`) | Actually resolve issues via read-only order/warranty lookups and escalation, with loop guards |
| 5 -> 6 | Single-shot -> LLM-based decomposition + bounded session memory | Handle multi-intent requests and multi-turn conversations; a real over-splitting bug was found and fixed here |
| 6 -> 7 | Static tone -> feedback-derived tone/verbosity adjustment | Adapt to customer sentiment without retraining the model |
| 7 -> 8 | Direct calls -> `traced_run` wrapper with latency capture and fallback | Deployment-safe: never surface a raw error to a customer |
| 8 -> 9 | Manual spot checks -> `run_evaluation` test harness over `evaluation/dataset.json` | Repeatable, real (not simulated) quality/safety measurement with a documented root-cause fix |
