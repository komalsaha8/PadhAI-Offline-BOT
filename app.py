"""
PadhAI BOT - Offline Board-to-Notes AI (Working Prototype)
-----------------------------------------------------------
This is a functional CPU-based prototype built to demonstrate the
Board -> Text -> Notes pipeline proposed for the Snapdragon AI Lab
Build & Present Challenge.

IMPORTANT (Current Status):
This prototype currently uses Tesseract OCR (CPU) and a rule-based
notes/MCQ generator so it can run and be demoed on any machine,
including Streamlit Community Cloud, without requiring Snapdragon
hardware or paid APIs.

The FINAL proposed version (see README.md) will replace these
placeholder components with:
  - YOLOv8-OCR (INT8), Qualcomm AI Hub  -> runs on Hexagon NPU
  - Phi-3.5 Mini Instruct (INT4), Qualcomm AI Hub -> runs on Hexagon NPU
  - ONNX Runtime with QNN Execution Provider for on-device inference
    on a Snapdragon-powered HP PC.

This app proves the end-to-end UX and pipeline logic work; the AI
model layer is designed to be swapped for the Qualcomm AI Hub models
once run on Snapdragon-powered HP hardware.
"""

import re
import io
import string
import random

import streamlit as st
from PIL import Image, ImageOps, ImageFilter
import pytesseract

# ----------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------
st.set_page_config(page_title="PadhAI BOT - Board to Notes", page_icon="📝", layout="centered")

st.title("📝 PadhAI BOT")
st.caption("Offline Board-to-Notes AI — working prototype (CPU demo build)")

with st.expander("ℹ️ About this prototype (read before judging)", expanded=True):
    st.markdown(
        """
This is a **working CPU prototype** built to demonstrate the pipeline proposed
for the **Snapdragon® AI Lab Build & Present Challenge**.

| Stage | This Demo (CPU) | Final Proposed Build (Snapdragon-powered HP PC) |
|---|---|---|
| OCR | Tesseract OCR | YOLOv8-OCR (INT8) — Qualcomm AI Hub, on Hexagon NPU |
| Notes/MCQ | Rule-based generator | Phi-3.5 Mini Instruct (INT4) — Qualcomm AI Hub, on Hexagon NPU |
| Runtime | Python / CPU | ONNX Runtime + QNN Execution Provider |

The goal of this demo is to prove the **pipeline and UX work end-to-end**.
The AI model layer is designed to be swapped for Qualcomm AI Hub models
once tested on Snapdragon-powered HP hardware.
        """
    )

# ----------------------------------------------------------------------
# Step 1: Photo -> Text
# ----------------------------------------------------------------------
st.header("Step 1: Photo → Text")
uploaded_file = st.file_uploader(
    "Upload a photo of a blackboard / whiteboard / notes page",
    type=["png", "jpg", "jpeg"],
)


def preprocess_image(image: Image.Image) -> Image.Image:
    """Basic cleanup to help OCR handle low-light / low-contrast board photos."""
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray)
    gray = gray.filter(ImageFilter.SHARPEN)
    return gray


def extract_text(image: Image.Image) -> str:
    processed = preprocess_image(image)
    text = pytesseract.image_to_string(processed)
    return text.strip()


extracted_text = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded board photo", use_container_width=True)

    with st.spinner("Extracting text from image..."):
        extracted_text = extract_text(image)

    st.subheader("Extracted Text")
    if extracted_text:
        st.text_area("OCR Output", extracted_text, height=180)
    else:
        st.warning(
            "No text could be detected. Try a clearer, well-lit photo, "
            "or type text manually below to test Steps 2 & 3."
        )

st.markdown("**Or paste/type board text manually** (useful for testing Steps 2 & 3 directly):")
manual_text = st.text_area("Manual text input", value="", height=120, key="manual_text")

final_text = manual_text.strip() if manual_text.strip() else extracted_text

# ----------------------------------------------------------------------
# Step 2: Text -> Smart Notes
# ----------------------------------------------------------------------
st.header("Step 2: Text → Smart Notes")


def split_sentences(text: str):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 0]


def generate_summary(sentences, max_sentences=3):
    if not sentences:
        return "Not enough text to summarize."
    return " ".join(sentences[:max_sentences])


def generate_notes(sentences):
    notes = []
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean.split()) >= 3:
            notes.append(f"- {s_clean}")
    return notes[:8] if notes else ["- (Add clearer board text to generate notes)"]


def generate_mcqs(sentences, num_questions=3):
    """
    Simple rule-based fill-in-the-blank MCQ generator.
    Placeholder for Phi-3.5 Mini Instruct in the final build.
    """
    candidates = [s for s in sentences if len(s.split()) >= 5]
    random.shuffle(candidates)
    mcqs = []

    for s in candidates[:num_questions]:
        words = [w.strip(string.punctuation) for w in s.split()]
        long_words = [w for w in words if len(w) > 4]
        if not long_words:
            continue
        answer = random.choice(long_words)
        question_text = s.replace(answer, "ـ" * len(answer), 1)

        distractors = set()
        while len(distractors) < 3:
            fake = random.choice(long_words + ["Concept", "Process", "Value", "Factor"])
            if fake.lower() != answer.lower():
                distractors.add(fake)

        options = list(distractors) + [answer]
        random.shuffle(options)

        mcqs.append(
            {
                "question": f"Fill in the blank: {question_text}",
                "options": options,
                "answer": answer,
            }
        )

    return mcqs


sentences = split_sentences(final_text)

if final_text:
    summary = generate_summary(sentences)
    notes = generate_notes(sentences)
    mcqs = generate_mcqs(sentences)

    st.subheader("Quick Summary")
    st.info(summary)

    st.subheader("Notes")
    st.markdown("\n".join(notes))

    st.subheader("Practice MCQs")
    if mcqs:
        for i, q in enumerate(mcqs, 1):
            st.markdown(f"**Q{i}. {q['question']}**")
            st.radio(
                f"Select an answer for Q{i}",
                q["options"],
                key=f"mcq_{i}",
                label_visibility="collapsed",
            )
            with st.expander("Show answer"):
                st.write(f"✅ {q['answer']}")
    else:
        st.write("Add more board text to generate practice questions.")
else:
    st.write("Upload a board photo or type text above to generate notes.")

# ----------------------------------------------------------------------
# Step 3: BOT Chat - Offline Doubt Solving (rule-based placeholder)
# ----------------------------------------------------------------------
st.header("Step 3: BOT Chat — Offline Doubt Solving (Demo)")

st.caption(
    "In this CPU demo, chat responses are template-based so the interface "
    "can be shown without an internet connection or paid API. "
    "The final build will use Phi-3.5 Mini Instruct running fully on-device "
    "on the Hexagon NPU for real offline doubt-solving, translation, and quizzing."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_query = st.text_input("Ask a doubt about the notes above (e.g. 'Summarize this', 'Test me')")

if st.button("Ask BOT") and user_query.strip():
    query_lower = user_query.lower()

    if not final_text:
        response = "Please upload a board photo or add text first, then ask your question."
    elif "hindi" in query_lower or "explain" in query_lower:
        response = (
            "(Demo response) In the final on-device build, Phi-3.5 Mini Instruct "
            "will generate a real explanation in Hindi based on your notes above."
        )
    elif "test" in query_lower or "quiz" in query_lower:
        response = "Scroll up to 'Practice MCQs' — that's your quiz for this content!"
    elif "summary" in query_lower or "summarize" in query_lower:
        response = f"Here's your summary: {generate_summary(sentences)}"
    else:
        response = (
            "(Demo response) This is a placeholder BOT reply. The final version "
            "will use an on-device LLM (Phi-3.5 Mini Instruct via Qualcomm AI Hub) "
            "to answer any doubt about your notes, fully offline."
        )

    st.session_state.chat_history.append((user_query, response))

for q, r in reversed(st.session_state.chat_history):
    st.markdown(f"**You:** {q}")
    st.markdown(f"**PadhAI BOT:** {r}")
    st.markdown("---")

st.caption(
    "PadhAI BOT — proposed for the Snapdragon® AI Lab Build & Present Challenge. "
    "This prototype demonstrates the pipeline; final version targets Snapdragon-powered HP PCs."
)
