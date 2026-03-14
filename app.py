# ======================================================
# SMART STUDY FLASHCARDS & MCQ GENERATOR
# FINAL LOCAL STREAMLIT APPLICATION
# ======================================================

import streamlit as st
import fitz  # PyMuPDF
import re
import hashlib

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Study Flashcards", layout="centered")

st.title("📚 Smart Study Flashcards & MCQ Generator")
st.write("Upload a PDF file to generate flashcards and exam-style MCQs automatically.")

# ---------------- SESSION STATE INIT ----------------
if "score" not in st.session_state:
    st.session_state.score = 0

if "answered" not in st.session_state:
    st.session_state.answered = set()

# ---------------- TEXT PROCESSING ----------------
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x20-\x7E]', ' ', text)
    return text.strip()

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    filtered = []

    for s in sentences:
        if len(s.split()) < 6:
            continue
        if any(word in s.lower() for word in [
            "faculty", "university", "chapter", "page",
            "copyright", "session", "unit"
        ]):
            continue
        filtered.append(s.strip())

    return filtered

# ---------------- FLASHCARD GENERATION ----------------
def generate_flashcards(sentences, limit=20):
    flashcards = []

    for s in sentences[:limit]:
        question = "Explain the following concept:"
        if " is " in s.lower():
            question = f"What is {s.split(' is ')[0].strip()}?"

        flashcards.append({
            "question": question,
            "answer": s
        })

    return flashcards

# ---------------- MCQ GENERATION (RULE-BASED) ----------------
def generate_mcqs(sentences):
    mcqs = []
    generated = set()

    for s in sentences:
        s_lower = s.lower()

        # Turing Test
        if "turing" in s_lower and "turing" not in generated:
            mcqs.append({
                "question": "What does the Turing Test evaluate?",
                "options": [
                    "Machine's ability to mimic human intelligence",
                    "Speed of a computer processor",
                    "Accuracy of numerical computation",
                    "Memory capacity of a system"
                ],
                "answer": "Machine's ability to mimic human intelligence"
            })
            generated.add("turing")

        # Intelligent Agent
        elif "agent" in s_lower and "percept" in s_lower and "agent" not in generated:
            mcqs.append({
                "question": "What is an intelligent agent in AI?",
                "options": [
                    "An entity that perceives and acts in an environment",
                    "A system that only stores data",
                    "A hardware device used for sensing",
                    "A fixed rule-based program"
                ],
                "answer": "An entity that perceives and acts in an environment"
            })
            generated.add("agent")

        # Reinforcement Learning
        elif ("reward" in s_lower or "penalty" in s_lower or "pain" in s_lower) and "rl" not in generated:
            mcqs.append({
                "question": "Which learning method is based on rewards and penalties?",
                "options": [
                    "Reinforcement learning",
                    "Supervised learning",
                    "Unsupervised learning",
                    "Rule-based learning"
                ],
                "answer": "Reinforcement learning"
            })
            generated.add("rl")

        if len(mcqs) >= 5:
            break

    return mcqs

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📤 Upload PDF", type=["pdf"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    file_hash = hashlib.md5(file_bytes).hexdigest()

    # Regenerate only if a NEW PDF is uploaded
    if st.session_state.get("pdf_hash") != file_hash:
        st.session_state.pdf_hash = file_hash
        st.session_state.score = 0
        st.session_state.answered = set()

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        raw_text = ""

        for page in doc:
            raw_text += page.get_text() + " "

        cleaned_text = clean_text(raw_text)
        sentences = split_into_sentences(cleaned_text)

        st.session_state.flashcards = generate_flashcards(sentences)
        st.session_state.mcqs = generate_mcqs(sentences)

    flashcards = st.session_state.flashcards
    mcqs = st.session_state.mcqs

    # ---------------- DISPLAY INFO ----------------
    st.success("✅ PDF processed successfully")
    st.write(f"📄 Pages: {doc.page_count}")
    st.write(f"🧠 Flashcards: {len(flashcards)}")
    st.write(f"📝 MCQs: {len(mcqs)}")
    st.subheader(f"🏆 Score: {st.session_state.score}")

    # ---------------- FLASHCARDS ----------------
    st.divider()
    st.subheader("📌 Flashcards")

    for card in flashcards[:5]:
        with st.expander(card["question"]):
            st.write(card["answer"])

    # ---------------- MCQs ----------------
    st.divider()
    st.subheader("📝 MCQs")

    for idx, mcq in enumerate(mcqs, start=1):
        st.markdown(f"**Q{idx}. {mcq['question']}**")

        selected = st.radio(
            "Choose an option:",
            mcq["options"],
            index=None,
            key=f"mcq_{idx}"
        )

        if st.button("Check Answer", key=f"check_{idx}"):
            if idx in st.session_state.answered:
                st.info("ℹ️ You already answered this question.")
            elif selected == mcq["answer"]:
                st.session_state.score += 1
                st.session_state.answered.add(idx)
                st.success("✅ Correct!")
            else:
                st.session_state.answered.add(idx)
                st.error(f"❌ Correct answer:\n{mcq['answer']}")

        st.divider()
