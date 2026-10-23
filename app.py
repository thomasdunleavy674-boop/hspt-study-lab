import json
import re
import uuid
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from google import genai

st.set_page_config(page_title="HSPT Study Lab", page_icon="📚", layout="wide")

# Google sign-in. Requires Authlib in requirements.txt and [auth] in Streamlit Secrets.
if not st.user.is_logged_in:
    st.title("📚 HSPT Study Lab")
    st.write("Sign in with Google to access your study tools.")
    st.button("🔐 Sign in with Google", on_click=st.login)
    st.stop()

with st.sidebar:
    st.write(f"Signed in as: {st.user.get('email', 'Google user')}")
    if st.button("Sign out"):
        st.logout()

site_folder = Path(__file__).parent
if not (site_folder / "index.html").exists():
    st.error("index.html must be in the same folder as app.py.")
    st.stop()

hspt_study_lab = components.declare_component("hspt_study_lab", path=str(site_folder))

MODELS = ["gemini-3.8-flash", "gemini-2.5-flash"]

def gemini_text(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from Streamlit Secrets.")
    client = genai.Client(api_key=api_key)
    errors = []
    for model in MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            if response.text:
                return response.text
            errors.append(f"{model}: empty response")
        except Exception as exc:
            errors.append(f"{model}: {type(exc).__name__}: {exc}")
    raise RuntimeError("Gemini model request failed. " + " | ".join(errors))

def make_questions(section, count, avoid):
    subjects = {
        "verbal": "Verbal Skills: synonyms, antonyms, analogies, word relationships, vocabulary",
        "quant": "Quantitative Skills: number patterns, logic, arithmetic reasoning, quantitative comparisons",
        "reading": "Reading: short original passages, main idea, inference, details, tone, context clues",
        "math": "Mathematics: arithmetic, fractions, percentages, equations, geometry, word problems",
        "language": "Language: grammar, punctuation, sentence structure, usage, spelling",
    }
    if section == "mixed":
        topic = "Create a balanced mix across these five HSPT-style areas: " + "; ".join(subjects.values())
    else:
        topic = subjects.get(section, subjects["math"])
    avoid_text = "\n".join(f"- {x}" for x in avoid if isinstance(x, str)) or "(none supplied)"
    prompt = f'''Create exactly {count} ORIGINAL HSPT-style practice questions. These are unofficial practice items, not copied from an actual exam.
Topic: {topic}
Difficulty: realistic middle-school/high-school-placement-test level, with varied skills and question structures.
Avoid repeating or closely paraphrasing these previously used question stems:
{avoid_text}
Return ONLY a valid JSON array. Every item must have exactly these keys:
{{"section":"one of verbal, quant, reading, math, language","question":"self-contained question; include any needed passage","choices":["choice 1","choice 2","choice 3","choice 4"],"answer":0,"explanation":"brief explanation"}}
The answer is a zero-based integer 0, 1, 2, or 3 matching exactly one correct choice. Make all distractors plausible but clearly wrong. Check arithmetic and the answer key before responding. Do not use Markdown fences, introductions, or extra text. Ensure questions are distinct from one another and from the avoided stems.'''
    raw = gemini_text(prompt).strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I)
    data = json.loads(raw)
    if not isinstance(data, list) or not data:
        raise ValueError("Gemini did not return a question list.")
    clean = []
    allowed = {"verbal", "quant", "reading", "math", "language"}
    for item in data[:count]:
        choices = item.get("choices")
        answer = item.get("answer")
        sec = item.get("section", section if section != "mixed" else "math")
        if sec not in allowed or not isinstance(item.get("question"), str) or not isinstance(choices, list) or len(choices) != 4 or not isinstance(answer, int) or answer not in range(4):
            continue
        clean.append({"section": sec, "question": item["question"], "choices": [str(c) for c in choices], "answer": answer, "explanation": str(item.get("explanation", "Review the relationship or calculation in the question."))})
    if not clean:
        raise ValueError("Gemini returned questions in an unexpected format. Try again.")
    return clean

if "last_ai_reply" not in st.session_state: st.session_state.last_ai_reply = ""
if "last_ai_reply_id" not in st.session_state: st.session_state.last_ai_reply_id = ""
if "last_request_id" not in st.session_state: st.session_state.last_request_id = None
if "generated_questions" not in st.session_state: st.session_state.generated_questions = "[]"
if "generated_questions_id" not in st.session_state: st.session_state.generated_questions_id = ""

result = hspt_study_lab(
    ai_reply=st.session_state.last_ai_reply,
    ai_reply_id=st.session_state.last_ai_reply_id,
    generated_questions=st.session_state.generated_questions,
    generated_questions_id=st.session_state.generated_questions_id,
    default=None,
    key="hspt_study_lab_component",
)

if isinstance(result, dict):
    request_id = str(result.get("id") or uuid.uuid4())
    if result.get("type") == "generate_questions" and request_id != st.session_state.last_request_id:
        st.session_state.last_request_id = request_id
        try:
            with st.spinner("Creating original HSPT questions..."):
                questions = make_questions(str(result.get("section", "mixed")), int(result.get("count", 10)), result.get("avoid", []))
            st.session_state.generated_questions = json.dumps(questions)
            st.session_state.generated_questions_id = request_id
        except Exception as exc:
            st.session_state.last_ai_reply = f"Question generation failed: {exc}"
            st.session_state.last_ai_reply_id = request_id
            st.session_state.generated_questions = "[]"
            st.session_state.generated_questions_id = request_id
        st.rerun()
    elif result.get("type") == "ai_request" and request_id != st.session_state.last_request_id:
        st.session_state.last_request_id = request_id
        question = str(result.get("text", "")).strip()
        if question:
            try:
                with st.spinner("AI tutor is thinking..."):
                    answer = gemini_text("You are a friendly HSPT study tutor. Explain clearly at a student-friendly level. Do not claim these are official HSPT questions. Student asks: " + question)
            except Exception as exc:
                answer = f"AI tutor error: {exc}"
            st.session_state.last_ai_reply = answer
            st.session_state.last_ai_reply_id = request_id
            st.rerun()
