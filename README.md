# Athena — Tech Gadgets Inc. Smart Customer Service Agent

Athena is a smart, helpful, kind, and just personified AI chatbot working as a customer-service agent for Tech Gadgets Inc.

This repository demonstrates Athena’s evolution from a basic rule-based chatbot into a production-oriented customer-support architecture. Each phase adds a capability because Athena’s previous architecture exposed a specific failure.

## Athena’s evolution

1. Athena understands the customer-support problem.
2. Athena provides basic rule/template support.
3. Athena gains LLM reasoning and prompt design.
4. Athena uses Tech Gadgets Inc. policies and knowledge through retrieval.
5. Athena uses controlled support tools.
6. Athena gains planning, memory, and conversation context.
7. Athena adapts from customer feedback.
8. Athena runs as a monitored service.
9. Athena is evaluated for quality, safety, governance, and production readiness.

Run locally with `streamlit run app.py`. Configure local credentials using `.env.example`; never commit the real `.env` file.

Athena can explain verified Tech Gadgets Inc. support information and recommend safe next steps. She does not fabricate policies or customer data, expose sensitive information, or execute uncontrolled state-changing actions.
