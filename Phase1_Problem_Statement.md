# Phase 1 — Design Document
## Tech Gadgets Inc. · Customer Support Modernization Initiative

---

## 1. Business Context & Problem Statement

Tech Gadgets Inc. is a consumer electronics e-commerce company selling wearables, audio devices, and personal electronics through its own storefront. Customer Support currently operates as a **human-only, email- and chat-first operation** with a small Tier-1 team and a Tier-2 specialist pool for complex or sensitive cases.

**Current state pain points:**

| Area | Current Performance | Business Impact |
|---|---|---|
| Ticket volume | 500+ tickets/day, growing 15% quarter-over-quarter | Team is understaffed relative to demand |
| First response time | 8-hour average (email channel) | Customers churn before first contact |
| Multi-touch resolution | 40% of tickets require 2+ agent interactions | Higher cost-per-contact, agent fatigue |
| Repetitive Tier-1 load | 60% of agent time spent on shipping status, return policy, and basic troubleshooting | Tier-2 specialists get pulled into Tier-1 work during peaks |
| CSAT trend | Declining quarter-over-quarter | Brand and retention risk |
| Peak-season backlog | Ticket aging spikes 3x during post-holiday return windows | SLA breaches, escalated complaints |
| Consistency | No single source of truth; answers vary by agent | Compliance and trust risk |

**Problem statement:** Tech Gadgets Inc. needs a support operating model that resolves high-volume, repetitive Tier-1 requests instantly and consistently, reserves human specialist time for complex or sensitive cases, and does so without sacrificing accuracy, safety, or customer trust.

**Goal:** Modernize the support workflow so that Tier-1 resolution is instant and policy-consistent, human specialists are engaged only where judgment or authority is required, and every interaction is measurable against a defined service-quality bar.

---

## 2. Primary User Persona & Daily Workflow

### Persona: The Requesting Customer

| Attribute | Detail |
|---|---|
| Name (composite) | Sarah Chen |
| Role | Existing Tech Gadgets Inc. customer |
| Demographics | Age 25–45, comfortable with technology, not a support-systems expert |
| Expectation | Instant, accurate resolution without repeating herself |
| Frustration triggers | Long hold times, generic answers, being transferred repeatedly |

### Customer-Support Domain Workflow (channel- and technology-agnostic)

This is the **operational workflow of a support case**, independent of who or what executes each step:

```
1. Trigger Event
   (delayed delivery, defective product, billing question, account concern)
            │
            ▼
2. Channel Entry
   (chat, email, self-service help center)
            │
            ▼
3. Identity & Order Verification
   (confirm customer identity, locate order/account context)
            │
            ▼
4. Issue Triage & Categorization
   (Order Status | Returns/Refunds | Warranty | Billing | Account Security)
            │
            ▼
5. Tier-1 Resolution Attempt
   (apply policy knowledge to resolve without specialist involvement)
            │
       ┌────┴────┐
       ▼         ▼
   Resolved   Needs Escalation
       │         │
       │         ▼
       │   6a. Tier-2 / Specialist Queue
       │       (billing disputes, legal threats, security incidents,
       │        policy exceptions)
       │         │
       │         ▼
       │   6b. Specialist Resolution & Authorization
       │         │
       └────┬────┘
            ▼
7. Resolution Confirmation to Customer
            │
            ▼
8. Post-Interaction Survey
   (CSAT / NPS capture)
            │
            ▼
9. Quality Assurance Sampling
   (QA audit score, coaching feedback loop)
```

This is a standard contact-center case lifecycle. Phase 2 onward in this project changes **who or what performs Step 5** — starting with a simple rule-based attempt and evolving toward a grounded, tool-using, monitored system — but the surrounding operational workflow (verification → triage → resolution attempt → escalation branch → confirmation → survey → QA) stays constant throughout.

---

## 3. Inputs, Outputs, Constraints & Assumptions

**Inputs:** Natural-language customer message; optional order ID; conversation context within a session; post-interaction satisfaction rating (1–5).

**Outputs:** A policy-grounded response; a tool-verified data lookup (order status, warranty state); an escalation record for Tier-2; a safe refusal for out-of-scope or unsafe requests; latency and outcome metrics for monitoring.

**Constraints:**
- Must not fabricate policy, pricing, or product information.
- Must not store full payment-card numbers, SSNs, or other raw PII in logs.
- Must not execute an irreversible account or financial action without a controlled, auditable step.
- Must respond within 3 seconds (p95) for Tier-1 categories.
- Must escalate legal threats, security incidents, and unresolved repeat contacts.

**Assumptions:** Customers interact through text-based channels only (chat/email) at this stage. Order data is available through a read-only lookup. A human specialist queue is staffed during business hours for escalations. Support policy documents are maintained and versioned by the CS Operations team.

---

## 4. Example Customer Questions

1. "Where is my order ORD-10567? It was supposed to arrive yesterday."
2. "My SmartWatch Pro X1 won't charge. I've had it for 3 months."
3. "I want a full refund — the product doesn't match the website description."
4. "Can you transfer my warranty to someone else? I'm selling the device."
5. "Someone is making purchases on my account that I didn't authorize!"

---

## 5. Success Criteria — Customer Service SLA Metrics

Success is measured using standard contact-center service metrics, not implementation-specific metrics:

| Metric | Definition | Target | Measurement Method |
|---|---|---|---|
| CSAT (Customer Satisfaction) | Post-interaction rating average | ≥ 4.2 / 5.0 | Post-chat survey |
| First Contact Resolution (FCR) | % resolved without follow-up contact | ≥ 70% | Case tracking |
| Containment Rate | % of Tier-1 cases resolved without a human specialist | ≥ 65% | Case routing logs |
| SLA Compliance (First Response) | % of contacts receiving first response within target window | ≥ 95% | Timestamp logging |
| Average Handle Time (AHT) | Average time to resolve a Tier-1 case | ≤ 3 minutes | Session duration logging |
| CS Quality Score (QA Audit) | Score from quality-assurance review of sampled interactions | ≥ 90% | QA sampling rubric |
| Escalation Rate | % of cases requiring Tier-2 specialist involvement | ≤ 20% | Case routing logs |
| Net Promoter Score (NPS) | Likelihood-to-recommend metric | ≥ 40 | Post-interaction survey |
| Backlog / Ticket Aging | Cases open beyond 24 hours | 0 aged cases | Queue monitoring |
| Policy Accuracy | % of responses matching current documented policy | ≥ 90% | Manual QA sample review |

---

## 6. Known Failure Cases & Edge Scenarios

| # | Scenario | Expected Failure Mode | Required Mitigation |
|---|---|---|---|
| 1 | Product not in knowledge base | Agent invents specs or policy | State uncertainty; escalate if needed |
| 2 | Non-existent or mistyped order ID | Agent fabricates order status | Verify before responding; ask customer to confirm |
| 3 | Multi-intent request (refund + shipping + complaint) | Only first intent addressed | Decompose and address each intent |
| 4 | Sarcastic or ambiguous phrasing | Intent misclassified | Clarify before acting |
| 5 | Rapid repeated contact (abuse or distress signal) | Endless loop or resource exhaustion | Bounded retries; escalate on repeat contact |
| 6 | Customer shares full card number or SSN | Sensitive data logged or repeated back | Detect and redact before logging or responding |
| 7 | Policy boundary case (exactly 30 days vs. 31 days) | Wrong policy tier applied | Explicit boundary rules in the knowledge base |
| 8 | Peak-season surge (post-holiday returns) | SLA breach due to volume spike | Escalation and containment targets tested under load |
| 9 | Legal threat or security incident | Treated as a normal request | Immediate mandatory escalation, no autonomous resolution |

---

## 7. Scope Boundary for Phase 1

This document defines the **problem, the customer, the operational workflow, and the success bar**. It intentionally does not describe how the resolution step will be technically implemented — that evolution is demonstrated phase by phase, starting with a basic rule-based attempt in Phase 2.
