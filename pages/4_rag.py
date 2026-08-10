import streamlit as st
from src.llm_agent import llm_response
from src.rag import load_policy_documents, retrieve

st.title("Phase 4 — Athena Uses Company Knowledge")
docs = load_policy_documents()
st.write(f"Knowledge-base documents loaded: {len(docs)} (chunked and embedded with OpenAI `text-embedding-3-small`, indexed in FAISS).")

query = st.text_input("Search the support knowledge base", "Can I return an item after 30 days?")
if st.button("Retrieve policy passages"):
    matches = retrieve(query, top_k=3)
    st.session_state["retrieved"] = matches
    if matches:
        for match in matches:
            with st.expander(f"{match['source']} (distance {match.get('distance', '—')})"):
                st.write(match["text"])
    else:
        st.warning("No relevant policy passage found. Athena must not guess; she should ask for clarification or escalate.")

st.subheader("Compare: answer without retrieval vs. with retrieval")
message = st.text_input("Ask a grounded customer question", "Can I return order ORD-10001 after purchase?")
col1, col2 = st.columns(2)
with col1:
    if st.button("Answer WITHOUT retrieval"):
        st.json(llm_response(message, context=""))
with col2:
    if st.button("Answer WITH retrieval"):
        context = "\n\n".join(f"[{m['source']}] {m['text']}" for m in st.session_state.get("retrieved", []) or retrieve(message, top_k=3))
        st.json(llm_response(message, context=context))
st.warning("Without retrieval the model can only rely on general knowledge and may hedge or guess. With retrieval it must ground the answer in the actual TechGadgets policy text.")