import streamlit as st
from src.policies import load_policies, search_policies
from src.runtime import answer

st.title("Policy-Grounded Support")
policies = load_policies()
query = st.text_input("Search the support policy", "What is the return period?")
if st.button("Retrieve policy"):
    matches = search_policies(query, policies)
    st.session_state["retrieved"] = matches
    st.write(f"Retrieved passages: {len(matches)}")
    for match in matches: st.write(f"**{match['source']}**\n\n{match['text']}")
message = st.text_input("Ask a grounded customer question", "Can I return order ORD-10001 after purchase?")
if st.button("Answer with retrieved policy"):
    context = "\n".join(x["text"] for x in st.session_state.get("retrieved", []))
    st.json(answer(message, context=context))
st.warning("If no policy passage is retrieved, the assistant must not guess; it should ask for clarification or escalate.")