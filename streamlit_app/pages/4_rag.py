import streamlit as st
from streamlit_app.components import phase_header, evidence_note
from src.rag import load_policy_documents, retrieve
phase_header(4, "Embeddings & Semantic Retrieval (RAG)", 10)
evidence_note("Demonstrate retrieval quality, grounding improvement, and honest handling of missing knowledge.")
docs = load_policy_documents()
st.write(f"Knowledge-base documents loaded: {len(docs)}")
query = st.text_input("Search support knowledge", "Can I return an item after 30 days?")
results = retrieve(query, docs)
if results:
    for result in results:
        with st.expander(result["source"]): st.write(result["text"])
else:
    st.warning("No relevant policy passage found. The agent must not guess; it should ask for clarification or escalate.")
st.subheader("Required comparison")
st.table({"Without RAG": ["May produce plausible but unsupported policy claims"], "With RAG": ["Uses retrieved policy passages and declares uncertainty when evidence is absent"]})
