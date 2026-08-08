import streamlit as st
from src.rag import load_policy_documents, retrieve

st.set_page_config(page_title="Phase 4 - RAG")
st.title("Phase 4 — Embeddings & Semantic Retrieval (RAG)")
st.caption("Rubric: Embeddings & Semantic Retrieval / RAG (10 pts)")
docs = load_policy_documents()
st.write(f"Knowledge-base documents loaded: {len(docs)}")
query = st.text_input("Search support knowledge", "Can I return an item after 30 days?")
results = retrieve(query, docs)
if results:
    for result in results:
        with st.expander(result["source"]):
            st.write(result["text"])
else:
    st.warning("No relevant policy passage found. The agent must not guess; it should ask for clarification or escalate.")
st.table({"Without RAG": ["May produce plausible but unsupported policy claims"], "With RAG": ["Uses retrieved policy passages and declares uncertainty when evidence is absent"]})