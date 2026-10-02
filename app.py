import streamlit as st

from answer import answer_question


st.set_page_config(
    page_title="Northstar Knowledge Assistant",
    page_icon="📚",
    layout="centered",
)

st.title("Northstar Knowledge Assistant")
st.write("Find answers in Northstar's internal support guides.")
st.caption(
    "Fictional customer demo. Answers can contain mistakes; "
    "check the cited passages before acting."
)

with st.form("question_form"):
    question = st.text_area(
        "What would you like to know?",
        placeholder="How long is a password reset link valid?",
        max_chars=2000,
    )
    submitted = st.form_submit_button("Find answer")

if submitted:
    # Clear the previous result before handling a new question.
    st.session_state.pop("result", None)

    if not question.strip():
        st.warning("Enter a question first.")
    else:
        try:
            with st.spinner("Searching the guides and preparing an answer..."):
                answer, sources = answer_question(question.strip())

            st.session_state["result"] = {
                "question": question.strip(),
                "answer": answer,
                "sources": sources,
            }

        except Exception as error:
            st.error(
                "We couldn't complete this request. "
                "Check your connection and local project setup."
            )
            st.caption(f"Error type: {type(error).__name__}")

result = st.session_state.get("result")

if result:
    st.divider()
    st.caption(f"Question: {result['question']}")
    st.subheader("Answer")
    st.markdown(result["answer"])

    st.subheader("Cited passages")

    if not result["sources"]:
        st.warning("No sources were cited. Treat this answer as unverified.")

    for source in result["sources"]:
        label = (
            f"[{source['label']}] "
            f"{source['source']} — {source['section']}"
        )
        with st.expander(label):
            st.markdown(source["text"])