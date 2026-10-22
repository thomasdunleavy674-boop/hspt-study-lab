
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from google import genai
import uuid

st.set_page_config(
    page_title="HSPT Study Lab",
    page_icon="📚",
    layout="wide",
)

# Find the website
site_folder = Path(__file__).parent
html_file = site_folder / "index.html"

if not html_file.exists():
    st.error(
        "Couldn't find index.html. "
        "Make sure it is in the same folder as app.py."
    )
    st.stop()

# Create the website component
hspt_study_lab = components.declare_component(
    "hspt_study_lab",
    path=str(site_folder),
)


def get_gemini_reply(question):
    """Try each model in order until one successfully answers."""

    api_key = st.secrets.get("GEMINI_API_KEY", "")

    if not api_key:
        return (
            "AI tutor setup is incomplete. "
            "Add GEMINI_API_KEY in Streamlit app Secrets."
        )

    client = genai.Client(api_key=api_key)

    models = [
        "gemini-3.8-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash-lite",
    ]

    errors = []

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=question,
            )

            if response.text:
                return response.text

            errors.append(f"{model}: empty response")

        except Exception as e:
            errors.append(
                f"{model}: {type(e).__name__}: {e}"
            )

    # Only show this if every model failed.
    return (
        "I couldn't get an answer from any available AI model.\n\n"
        "Models tried:\n"
        + "\n".join(errors)
    )


# Keep AI tutor responses between Streamlit reruns
if "last_ai_reply" not in st.session_state:
    st.session_state.last_ai_reply = ""

if "last_ai_reply_id" not in st.session_state:
    st.session_state.last_ai_reply_id = ""

if "last_request_id" not in st.session_state:
    st.session_state.last_request_id = None


# Display the website
result = hspt_study_lab(
    ai_reply=st.session_state.last_ai_reply,
    ai_reply_id=st.session_state.last_ai_reply_id,
    default=None,
    key="hspt_study_lab_component",
)

# Handle AI tutor requests from the website
if isinstance(result, dict) and result.get("type") == "ai_request":
    request_id = result.get("id") or str(uuid.uuid4())
    question = str(result.get("text", "")).strip()

    if question and request_id != st.session_state.last_request_id:
        st.session_state.last_request_id = request_id

        with st.spinner("AI tutor is trying available models..."):
            answer = get_gemini_reply(question)

        st.session_state.last_ai_reply = answer
        st.session_state.last_ai_reply_id = request_id
        st.rerun()

