import streamlit as st
from src.runtime import answer

st.title("Feedback-Adapted Support")
if "feedback" not in st.session_state: st.session_state.feedback = []
rating = st.slider("Rate the previous response", 1, 5, 3)
if st.button("Save feedback"):
    st.session_state.feedback.append(rating)
avg = sum(st.session_state.feedback[-10:]) / len(st.session_state.feedback[-10:]) if st.session_state.feedback else 3
tone = "empathetic" if avg < 3 else "professional"
st.write({"ratings": st.session_state.feedback, "rolling_average": round(avg, 2), "current_tone": tone})
message = st.text_input("Repeat a support question", "My package is delayed")
if st.button("Generate adapted response"):
    st.json(answer(message, feedback={"tone": tone}))