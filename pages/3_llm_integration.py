import streamlit as st
from src.llm_agent import PROMPT_VARIANTS, compare_prompts, llm_response

st.title("Phase 3 — Athena Gains LLM Reasoning")
st.write("Athena now calls a real LLM (`gpt-4o-mini` via LangChain `ChatOpenAI`) behind three versioned system prompts.")

for name, prompt in PROMPT_VARIANTS.items():
    with st.expander(name):
        st.code(prompt)

st.subheader("Try a single prompt variant")
message = st.text_area("Customer message", "My order ORD-10002 arrived damaged. Can I get a refund?")
variant = st.selectbox("Prompt variant", list(PROMPT_VARIANTS.keys()), index=2)
if st.button("Ask the assistant"):
    st.json(llm_response(message, prompt_version=variant))

st.subheader("Required prompt comparison (same test set, 3 variants)")
st.caption("Runs the identical message through v1_basic, v2_structured, and v3_safety_first for a real, side-by-side comparison.")
compare_message = st.text_input("Comparison test message", "What happens if my warranty just expired yesterday?")
if st.button("Run prompt comparison"):
    results = compare_prompts(compare_message)
    st.table({
        "Variant": [r["variant"] for r in results],
        "Status": [r["status"] for r in results],
        "Answer": [r["answer"][:220] for r in results],
    })
    st.caption("v1_basic tends to be terse and may omit uncertainty; v3_safety_first grounds itself and explicitly separates information from action — see docs/prompt_comparison.md for the full written analysis.")
