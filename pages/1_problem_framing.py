import streamlit as st
from pathlib import Path

from src.athena import ATHENA_NAME, COMPANY_NAME
from src.ui import phase_carousel

st.set_page_config(page_title="Phase 1 - Problem Statement", page_icon="🧭", layout="wide")
phase_carousel(1)
st.title(f"Phase 1 — Understanding {COMPANY_NAME}'s Support Problem")
st.caption(f"Before {ATHENA_NAME} was built, the business problem, the customer, and the success bar had to be defined.")

st.markdown("### Business context")
st.write(
    f"{COMPANY_NAME} is a consumer electronics e-commerce company selling wearables, audio devices, "
    "and personal electronics. Customer Support today is a human-only, email- and chat-first operation "
    "with a small Tier-1 team and a Tier-2 specialist pool."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Daily ticket volume", "500+", "+15% QoQ")
col2.metric("First response time", "8 hrs", "email channel")
col3.metric("Multi-touch tickets", "40%", "need 2+ contacts")
col4.metric("Tier-1 time spent", "60%", "on repetitive queries")

st.markdown("### Primary customer persona")
pc1, pc2 = st.columns([1, 2])
with pc1:
    st.markdown("**Sarah Chen** (composite persona)")
    st.write("Age 25–45 · tech-savvy but not a support-systems expert · expects a quick, accurate resolution.")
with pc2:
    st.write("**Frustration triggers:** repeating information across contacts, generic answers that ignore her specific situation, 24+ hour email waits, being transferred multiple times for a simple issue.")

st.markdown("### The customer-support case lifecycle (domain workflow)")
st.caption("This is how a support case moves through the business today — independent of who or what performs the resolution step.")
st.code(
    """1. Trigger Event (delivery delay, defective product, billing question, account concern)
        |
        v
2. Channel Entry (chat, email, self-service help center)
        |
        v
3. Identity & Order Verification
        |
        v
4. Issue Triage & Categorization (Order Status | Returns/Refunds | Warranty | Billing | Account Security)
        |
        v
5. Tier-1 Resolution Attempt
        |
   +----+----+
   v         v
Resolved   Needs Escalation
   |         |
   |         v
   |   6a. Tier-2 / Specialist Queue (disputes, legal threats, security, policy exceptions)
   |         |
   |         v
   |   6b. Specialist Resolution & Authorization
   |         |
   +----+----+
        v
7. Resolution Confirmation to Customer
        |
        v
8. Post-Interaction Survey (CSAT / NPS)
        |
        v
9. Quality Assurance Sampling (QA audit + coaching loop)""",
    language="text",
)
st.info(
    f"Phase 2 onward changes who or what performs Step 5 — starting with a simple rule-based attempt by {ATHENA_NAME} "
    "and evolving toward a grounded, tool-using, monitored system. The rest of this lifecycle stays constant."
)

st.markdown("### Example customer questions")
for q in [
    "Where is my order ORD-10567? It was supposed to arrive yesterday.",
    "My SmartWatch Pro X1 won't charge. I've had it for 3 months.",
    "I want a full refund — the product doesn't match the website description.",
    "Can you transfer my warranty to someone else? I'm selling the device.",
    "Someone is making purchases on my account that I didn't authorize!",
]:
    st.markdown(f"- \"{q}\"")

st.markdown("### Success criteria — Customer Service SLA metrics")
st.table(
    {
        "Metric": ["CSAT", "First Contact Resolution", "Containment Rate", "SLA Compliance (first response)", "Average Handle Time", "CS Quality Score (QA)", "Escalation Rate", "NPS", "Backlog / Ticket Aging", "Policy Accuracy"],
        "Target": ["≥ 4.2 / 5.0", "≥ 70%", "≥ 65%", "≥ 95%", "≤ 3 min", "≥ 90%", "≤ 20%", "≥ 40", "0 aged cases", "≥ 90%"],
    }
)

st.markdown("### Known failure cases and edge scenarios")
st.table(
    {
        "Scenario": [
            "Product not in knowledge base",
            "Non-existent order ID",
            "Multi-intent request",
            "Sarcastic / ambiguous phrasing",
            "Rapid repeated contact",
            "Full card number or SSN shared",
            "Policy boundary case (30 vs 31 days)",
            "Peak-season surge",
            "Legal threat / security incident",
        ],
        "Required mitigation": [
            "State uncertainty; escalate if needed",
            "Verify before responding",
            "Decompose and address each intent",
            "Clarify before acting",
            "Bounded retries; escalate on repeat contact",
            "Detect and redact before logging or responding",
            "Explicit boundary rules in knowledge base",
            "Containment targets tested under load",
            "Immediate mandatory escalation",
        ],
    }
)

st.markdown("### Why an AI agent? — Solution justification")
st.write(
    "Alternatives considered: (1) Hire more Tier-1 agents — does not scale with 15% QoQ growth and adds linear cost. "
    "(2) Expand FAQ / self-service — helps with simple lookups but cannot handle contextual reasoning, multi-intent requests, or order-specific verification. "
    "(3) Decision-tree chatbot — rigid, requires constant manual updates, and fails on edge cases. "
    f"An AI agent ({ATHENA_NAME}) is chosen because it combines real-time reasoning, policy grounding via RAG, tool-calling for verified data, "
    "and graceful escalation — delivering instant, consistent Tier-1 resolution while preserving human specialists for complex cases."
)

st.markdown("### Stakeholder map")
st.table({
    "Stakeholder": ["Customer (Sarah Chen)", "Tier-1 Support Agent", "CS Operations Manager", "Product / Engineering", "Compliance & Legal"],
    "Role": [
        "End user receiving support",
        "Handles overflow and escalations",
        "Owns SLA targets and staffing",
        "Builds and maintains the AI system",
        "Ensures policy accuracy and data safety",
    ],
    "Key concern": [
        "Speed, accuracy, no repetition",
        "Reduced repetitive load, clear escalation triggers",
        "Containment rate, CSAT, cost per contact",
        "Observability, graceful degradation, maintainability",
        "No PII leaks, no fabricated policy, audit trail",
    ],
})

st.markdown("### Evaluation planning")
st.write(
    "Success criteria will be validated through a **fixed test suite** (Phase 9) covering:"
)
st.markdown(
    "- **Quality**: Does the response correctly address the customer's intent using verified information?\n"
    "- **Safety**: Are unsafe/out-of-scope requests refused? Is PII detected and redacted?\n"
    "- **Policy compliance**: Do answers match the documented knowledge base without fabrication?\n"
    "- **Graceful failure**: Does the system degrade to deterministic logic (not errors) when the LLM is unavailable?\n"
    "- **Latency**: Is p95 response time within the 3-second SLA target?"
)
st.info(
    "The test dataset (`evaluation/dataset.json`) contains representative cases for each failure mode above. "
    "Phase 9 runs every test case through the full agent pipeline and produces a quantitative scorecard."
)

st.markdown("### Capability-to-phase mapping")
st.table({
    "Success Metric": ["CSAT ≥ 4.2", "FCR ≥ 70%", "Containment ≥ 65%", "SLA Compliance ≥ 95%", "AHT ≤ 3 min", "QA Score ≥ 90%", "Escalation ≤ 20%", "Policy Accuracy ≥ 90%"],
    "Delivered by Phase": ["P3 (natural tone) + P7 (adaptation)", "P4 (RAG) + P5 (tools)", "P5 (tools) + P6 (planning)", "P3 (instant LLM) + P8 (monitoring)", "P3 (LLM) + P5 (tools)", "P9 (evaluation suite)", "P2 (safety) + P5 (escalate tool)", "P4 (RAG grounding)"],
})

st.markdown("---")
doc_path = Path("docs/phase1_problem_statement.md")
if doc_path.exists():
    st.download_button("Download full Phase 1 problem statement", doc_path.read_text(encoding="utf-8"), file_name="phase1_problem_statement.md")
