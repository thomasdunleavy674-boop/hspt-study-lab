
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import json
import uuid

st.set_page_config(
    page_title="HSPT Study Lab",
    page_icon="📚",
    layout="wide",
)

# Load the website files
site_folder = Path(__file__).parent
html_file = site_folder / "index.html"

if not html_file.exists():
    st.error("Couldn't find index.html. Make sure it is in the same GitHub folder as app.py.")
    st.stop()

# Create the website component
hspt_study_lab = components.declare_component(
    "hspt_study_lab",
    path=str(site_folder),
)

# Gemini AI tutor
def get_gemini_reply(question):
    try:
        from google import genai

        api_key = st.secrets.get("GEMINI_API_KEY", "")

        if not api_key:
            return (
                "The AI tutor is not configured yet. "
                "Add GEMINI_API_KEY in your Streamlit app's Secrets settings."
            )

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=question,
        )

        if response.text:
            return response.text

        return "Gemini returned an empty answer. Please try again."

    except Exception as e:
        # Show the actual error so we can diagnose it.
        return f"Gemini connection error: {type(e).__name__}: {e}"


# Receive requests from the website
if "ai_replies" not in st.session_state:
    st.session_state.ai_replies = {}

if "last_request_id" not in st.session_state:
    st.session_state.last_request_id = None

# Render the HTML website
result = hspt_study_lab(
    ai_reply=st.session_state.get("last_ai_reply", ""),
    ai_reply_id=st.session_state.get("last_ai_reply_id", ""),
    default=None,
    key="hspt_study_lab_component",
)

# Process AI tutor messages from the component
if isinstance(result, dict) and result.get("type") == "ai_request":
    request_id = result.get("id", str(uuid.uuid4()))
    question = str(result.get("text", "")).strip()

    if question and request_id != st.session_state.last_request_id:
        st.session_state.last_request_id = request_id

        with st.spinner("AI tutor is thinking..."):
            answer = get_gemini_reply(question)

        st.session_state.last_ai_reply = answer
        st.session_state.last_ai_reply_id = request_id
        st.rerun()
