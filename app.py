
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

# Require Google sign-in before showing the app
if not st.user.is_logged_in:
    st.title("📚 HSPT Study Lab")
    st.write("Sign in with Google to access your study tools.")
    st.button("🔐 Sign in with Google", on_click=st.login)
    st.stop()

# Signed-in user's account controls
with st.sidebar:
    st.write(f"Signed in as: {st.user.get('email', 'Google user')}")
    if st.button("Sign out"):
        st.logout()

# Find the website files
site_folder = Path(__file__).parent
html_file = site_folder / "index.html"

if not html_file.exists():
    st.error("index.html must be in the same folder as app.py.")
    st.stop()

# Create the website component
hspt_study_lab = components.declare_component(
    "hspt_study_lab",
    path=str(site_folder),
)


def get_gemini_reply(question):
    api_key = st.secrets.get("GEMINI_API_KEY", "")

    if not api_key:
        return "AI tutor setup is incomplete. Check Streamlit Secrets."

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return f"Could not initialize Gemini: {type(e).__name__}: {e}"

    # Try models in order until one works
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

    return (
        "I couldn't get an answer from the available models.\n\n"
        + "\n".join(errors)
    )


# Keep tutor responses between reruns
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

# Handle AI tutor requests
if isinstance(result, dict) and result.get("type") == "ai_request":
    request_id = result.get("id") or str(uuid.uuid4())
    question = str(result.get("text", "")).strip()

    if question and request_id != st.session_state.last_request_id:
        st.session_state.last_request_id = request_id

        with st.spinner("AI tutor is thinking..."):
            answer = get_gemini_reply(question)

        st.session_state.last_ai_reply = answer
        st.session_state.last_ai_reply_id = request_id
        st.rerun()
