
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

# Use the existing website as a connected Streamlit component.
site_folder = Path(__file__).parent

if not (site_folder / "index.html").exists():
    st.error("index.html must be in the same repository as app.py.")
    st.stop()

website = components.declare_component(
    "hspt_study_lab",
    path=str(site_folder),
)

if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = []

if "last_request_id" not in st.session_state:
    st.session_state.last_request_id = None

if "ai_reply" not in st.session_state:
    st.session_state.ai_reply = ""

if "ai_reply_id" not in st.session_state:
    st.session_state.ai_reply_id = ""

# Send replies back to the tutor box inside index.html.
request = website(
    ai_reply=st.session_state.ai_reply,
    ai_reply_id=st.session_state.ai_reply_id,
    key="hspt_site",
)

# Handle messages sent from the website's tutor box.
if (
    isinstance(request, dict)
    and request.get("type") == "ai_request"
    and request.get("id") != st.session_state.last_request_id
):
    request_id = request.get("id")
    prompt = str(request.get("text", "")).strip()

    if request_id and prompt:
        st.session_state.last_request_id = request_id
        st.session_state.ai_messages.append(
            {"role": "user", "content": prompt}
        )

        try:
            client = genai.Client(
                api_key=st.secrets["GEMINI_API_KEY"]
            )

            recent = st.session_state.ai_messages[-12:]
            conversation = "\n".join(
                f'{m["role"].upper()}: {m["content"]}'
                for m in recent
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    "You are a friendly, age-appropriate HSPT study tutor. "
                    "Help the student learn vocabulary, verbal skills, "
                    "quantitative reasoning, reading, math, and grammar. "
                    "Explain clearly with examples and step-by-step guidance. "
                    "Be concise. Do not claim practice questions are official.\n\n"
                    + conversation
                ),
            )

            answer = response.text or (
                "I couldn't generate a reply. Please try again."
            )

        except Exception as e:
    answer = f"Gemini connection error: {type(e).__name__}: {e}"
            )

        st.session_state.ai_messages.append(
            {"role": "assistant", "content": answer}
        )

        st.session_state.ai_reply = answer
        st.session_state.ai_reply_id = str(request_id)
        st.rerun()

