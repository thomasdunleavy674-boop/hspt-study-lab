
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from google import genai

st.set_page_config(
    page_title="HSPT Study Lab",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Display your original website
html_path = Path(__file__).parent / "index.html"

if html_path.exists():
    html = html_path.read_text(encoding="utf-8")
    components.html(html, height=1600, scrolling=True)
else:
    st.error("Missing index.html. Add it to your GitHub repository.")

st.divider()

# Real AI tutor
st.title("✦ AI Study Tutor")
st.caption("Ask questions about HSPT math, vocabulary, reading, or grammar.")

if "tutor_messages" not in st.session_state:
    st.session_state.tutor_messages = []

for message in st.session_state.tutor_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask your AI tutor a question...")

if prompt:
    st.session_state.tutor_messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)

        # Include recent conversation so the tutor remembers context.
        recent = st.session_state.tutor_messages[-12:]
        conversation = "\n".join(
            f'{m["role"].upper()}: {m["content"]}'
            for m in recent
        )

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=(
                        "You are a friendly, age-appropriate HSPT study tutor. "
                        "Explain concepts clearly, use examples, and help the "
                        "student learn step by step. Be concise. These are "
                        "practice questions, not official HSPT questions.\n\n"
                        + conversation
                    ),
                )
                answer = response.text or "I couldn't generate a reply. Try again."
                st.markdown(answer)

        st.session_state.tutor_messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as error:
        st.error(
            "The AI tutor couldn't connect. Check that GEMINI_API_KEY "
            "is saved in Streamlit Settings → Secrets and that your "
            "Gemini API key has available access."
        )
        st.caption(f"Error details: {error}")

if st.button("Clear AI chat"):
    st.session_state.tutor_messages = []
    st.rerun()

st.caption(
    "Independent study project. Not affiliated with the HSPT or its publisher."
)
