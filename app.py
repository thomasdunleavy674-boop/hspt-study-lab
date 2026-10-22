
import streamlit as st
import random

st.set_page_config(
    page_title="HSPT Study Lab",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020, #172647);
    color: white;
}
h1, h2, h3, p, label {
    color: #f0f4ff;
}
div.stButton > button {
    border-radius: 12px;
    font-weight: bold;
    min-height: 42px;
}
</style>
""", unsafe_allow_html=True)

QUESTIONS = {
    "Verbal Skills": [
        {
            "q": "Which word means almost the same as RELUCTANT?",
            "choices": ["Eager", "Unwilling", "Careless", "Certain"],
            "answer": "Unwilling",
            "why": "Reluctant means hesitant or unwilling to do something."
        },
        {
            "q": "BRIEF is to LENGTHY as ANCIENT is to...",
            "choices": ["Old", "Historic", "Modern", "Fragile"],
            "answer": "Modern",
            "why": "Brief and lengthy are opposites, as are ancient and modern."
        },
        {
            "q": "Which word is the opposite of SCARCE?",
            "choices": ["Rare", "Limited", "Abundant", "Unusual"],
            "answer": "Abundant",
            "why": "Scarce means in short supply. Abundant means plentiful."
        }
    ],
    "Quantitative Skills": [
        {
            "q": "What number comes next? 2, 6, 12, 20, 30, ...",
            "choices": ["36", "40", "42", "44"],
            "answer": "42",
            "why": "The differences are +4, +6, +8, +10, then +12."
        },
        {
            "q": "What is the average of 6, 8, and 13?",
            "choices": ["8", "9", "10", "11"],
            "answer": "9",
            "why": "6 + 8 + 13 = 27. Then 27 divided by 3 equals 9."
        },
        {
            "q": "If all Zips are Zaps, and all Zaps are Zops, which must be true?",
            "choices": [
                "All Zops are Zips",
                "All Zips are Zops",
                "No Zips are Zops",
                "All Zaps are Zips"
            ],
            "answer": "All Zips are Zops",
            "why": "If Zips belong to the Zaps group and Zaps belong to the Zops group, every Zip is a Zop."
        }
    ],
    "Reading": [
        {
            "q": "A student checks the clock repeatedly while waiting outside an office. What can you reasonably infer?",
            "choices": [
                "The student is waiting for something",
                "The student lost a book",
                "The office is closed forever",
                "The student dislikes clocks"
            ],
            "answer": "The student is waiting for something",
            "why": "Repeatedly checking the clock suggests the student is anticipating an event."
        },
        {
            "q": "What is the main idea of a passage explaining how bees pollinate crops?",
            "choices": [
                "Bees are always dangerous",
                "Bees help plants reproduce and crops grow",
                "All insects make honey",
                "Flowers only grow in summer"
            ],
            "answer": "Bees help plants reproduce and crops grow",
            "why": "The main idea summarizes the central point of the passage."
        },
        {
            "q": "In the sentence 'The arid desert received little rain,' arid means...",
            "choices": ["Cold", "Dry", "Crowded", "Windy"],
            "answer": "Dry",
            "why": "Arid means very dry."
        }
    ],
    "Mathematics": [
        {
            "q": "Solve: 3x + 7 = 25",
            "choices": ["4", "6", "8", "10"],
            "answer": "6",
            "why": "Subtract 7 to get 3x = 18. Divide by 3 to get x = 6."
        },
        {
            "q": "What is 35% of 80?",
            "choices": ["18", "24", "28", "32"],
            "answer": "28",
            "why": "35% is 0.35. Multiply 0.35 by 80 to get 28."
        },
        {
            "q": "A rectangle is 9 cm long and 4 cm wide. What is its perimeter?",
            "choices": ["13 cm", "26 cm", "36 cm", "72 cm"],
            "answer": "26 cm",
            "why": "Perimeter = 2 × (length + width) = 2 × 13 = 26 cm."
        }
    ],
    "Language": [
        {
            "q": "Choose the sentence with correct subject-verb agreement.",
            "choices": [
                "The list of names are here.",
                "The list of names is here.",
                "The list of names be here.",
                "The list of names were here."
            ],
            "answer": "The list of names is here.",
            "why": "The subject is 'list,' which is singular, so use 'is.'"
        },
        {
            "q": "Which sentence is punctuated correctly?",
            "choices": [
                "After lunch we, went home.",
                "After lunch, we went home.",
                "After, lunch we went home.",
                "After lunch we went, home."
            ],
            "answer": "After lunch, we went home.",
            "why": "An introductory phrase is usually followed by a comma."
        },
        {
            "q": "Yesterday, Maya _____ her homework.",
            "choices": ["finish", "finishes", "finished", "finishing"],
            "answer": "finished",
            "why": "'Yesterday' indicates the past, so 'finished' is correct."
        }
    ]
}

if "scores" not in st.session_state:
    st.session_state.scores = {s: [0, 0] for s in QUESTIONS}

if "question" not in st.session_state:
    st.session_state.question = None

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "asked" not in st.session_state:
    st.session_state.asked = set()

st.title("📚 HSPT Study Lab")
st.write("### Practice smarter. Build confidence.")
st.caption("Free HSPT-style practice • Five subject areas • Instant explanations")

st.divider()

section = st.selectbox(
    "Choose a subject",
    list(QUESTIONS.keys())
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Questions answered", sum(v[1] for v in st.session_state.scores.values()))

with col2:
    total_correct = sum(v[0] for v in st.session_state.scores.values())
    total_answered = sum(v[1] for v in st.session_state.scores.values())
    accuracy = round(total_correct / total_answered * 100) if total_answered else 0
    st.metric("Accuracy", f"{accuracy}%")

with col3:
    st.metric("Subjects", len(QUESTIONS))

st.divider()
st.header(section)

if st.button("🎲 Get a question", type="primary"):
    available = [
        q for q in QUESTIONS[section]
        if q["q"] not in st.session_state.asked
    ]
    if not available:
        st.session_state.asked = {
            item for item in st.session_state.asked
            if item not in [q["q"] for q in QUESTIONS[section]]
        }
        available = QUESTIONS[section]

    st.session_state.question = random.choice(available)
    st.session_state.asked.add(st.session_state.question["q"])
    st.session_state.feedback = None

q = st.session_state.question

if q:
    st.subheader(q["q"])

    choice = st.radio(
        "Choose your answer:",
        q["choices"],
        key=f"answer_{q['q']}"
    )

    if st.button("Check answer"):
        if st.session_state.feedback is None:
            correct = choice == q["answer"]
            st.session_state.scores[section][1] += 1
            if correct:
                st.session_state.scores[section][0] += 1

            st.session_state.feedback = {
                "correct": correct,
                "why": q["why"],
                "answer": q["answer"]
            }

    if st.session_state.feedback:
        result = st.session_state.feedback
        if result["correct"]:
            st.success("Correct! Great work.")
        else:
            st.error(f"Not quite. The answer is: {result['answer']}")

        st.info(result["why"])

st.divider()
st.header("🤖 Study Helper")

st.write(
    "Ask for study advice or an explanation. "
    "This starter helper uses built-in responses, not a live AI model."
)

question = st.text_input(
    "What would you like help with?",
    placeholder="Example: How do I solve equations?"
)

if st.button("Ask the study helper"):
    if question.strip():
        text = question.lower()

        if "fraction" in text:
            answer = (
                "For adding or subtracting fractions, find a common "
                "denominator first. For multiplication, multiply the "
                "numerators and denominators. For division, multiply "
                "by the reciprocal."
            )
        elif "percent" in text:
            answer = (
                "To find a percent of a number, change the percent "
                "to a decimal and multiply. Example: 25% of 60 is "
                "0.25 × 60 = 15."
            )
        elif "equation" in text or "solve" in text or "algebra" in text:
            answer = (
                "To solve an equation, use inverse operations to get "
                "the variable alone. Whatever you do to one side, "
                "do to the other side."
            )
        elif "vocab" in text or "word" in text or "verbal" in text:
            answer = (
                "For vocabulary, learn each word's meaning, a synonym, "
                "an antonym, and a sentence using it. For analogies, "
                "identify the relationship between the first pair."
            )
        elif "reading" in text:
            answer = (
                "For reading comprehension, find the main idea, use "
                "text clues for inferences, and look at the surrounding "
                "sentence to work out unfamiliar words."
            )
        elif "grammar" in text or "language" in text:
            answer = (
                "For language questions, check subject-verb agreement, "
                "verb tense, pronouns, commas, apostrophes, and spelling."
            )
        else:
            answer = (
                "Try asking about fractions, percentages, equations, "
                "vocabulary, reading comprehension, or grammar. "
                "I can give basic study tips for these topics."
            )

        st.info(answer)

st.divider()
st.header("📊 Your scores")

for name, values in st.session_state.scores.items():
    correct, answered = values
    percent = round(correct / answered * 100) if answered else 0
    st.write(f"**{name}:** {correct}/{answered} correct")
    st.progress(percent / 100)

st.caption(
    "Independent study project. These are original practice examples, "
    "not official HSPT questions or an official score estimate."
)
