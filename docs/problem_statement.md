# Problem Statement

TechGadgets Inc. receives recurring customer-support requests about orders, shipping, returns, warranties, product issues, and account concerns. The proposed agent supports Tier-1 resolution while preserving a strict boundary: it may explain verified policy and retrieve read-only information, but it must not fabricate policy, expose customer data, or execute uncontrolled state-changing actions.

## Inputs
Customer message, optional order identifier, and bounded conversation context.

## Outputs
Grounded response, clarification request, safe refusal, or human escalation.

## Assumptions
Support policies are available as versioned documents; demonstration tools use mock records; production integrations require authentication and additional authorization.

## Success criteria
Quality, groundedness, safety, escalation correctness, latency, and PII-safe observability are evaluated with repeatable test cases.
