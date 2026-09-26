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
import numpy as np
import cv2
from PIL import Image
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


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Cleanup pipeline to help Tesseract handle real board photos:
    uneven lighting, small handwriting/symbols, low resolution.
    NOTE: This only improves TEXT recognition (words, formulas, units).
    It cannot interpret diagrams, circuits, or drawings — OCR has no
    concept of visual/spatial meaning, only characters.
    """
    img_array = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # Upscale — small board text/symbols are much easier to read larger
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Denoise before thresholding
    gray = cv2.fastNlMeansDenoising(gray, h=10)

    # Adaptive threshold handles uneven board lighting / glare better
    # than a single global contrast adjustment.
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    return thresh


def extract_text(image: Image.Image) -> str:
    processed = preprocess_image(image)
    # --oem 3: default LSTM engine. --psm 6: assume a single uniform block
    # of text, which suits board/whiteboard photos better than the default.
    text = pytesseract.image_to_string(processed, config="--oem 3 --psm 6")
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


def generate_notes(sentences, max_points=10):
    """
    Breaks extracted text into short, scannable bullet points instead of
    dumping full sentences as-is. Long sentences are split on natural
    breaks (commas, semicolons, ' and ') so each point stays concise -
    closer to how a student would actually write notes.
    """
    points = []

    for s in sentences:
        s_clean = s.strip().rstrip(".")
        if len(s_clean.split()) < 3:
            continue

        # If the sentence is short enough, keep it as one point.
        if len(s_clean.split()) <= 12:
            points.append(s_clean)
            continue

        # Otherwise, split long sentences into smaller chunks on natural
        # breaks (commas, semicolons, "and") so each bullet stays a
        # complete, readable idea rather than a mid-clause fragment.
        chunks = re.split(r",\s+| and |; ", s_clean)
        for chunk in chunks:
            chunk = chunk.strip()
            # Drop a leading conjunction left over from splitting, so
            # points don't awkwardly start with "and"/"which"/"but".
            chunk = re.sub(r"^(and|which|where|but)\s+", "", chunk, flags=re.IGNORECASE)
            if len(chunk.split()) >= 3:
                points.append(chunk)

    # Capitalize first letter and dedupe while preserving order
    seen = set()
    clean_points = []
    for p in points:
        p_formatted = p[0].upper() + p[1:] if p else p
        key = p_formatted.lower()
        if key not in seen:
            seen.add(key)
            clean_points.append(p_formatted)

    if not clean_points:
        return ["(Add clearer board text to generate notes)"]

    return clean_points[:max_points]


def make_fill_blank_question(sentence, all_long_words):
    words = [w.strip(string.punctuation) for w in sentence.split()]
    long_words = [w for w in words if len(w) > 4]
    if not long_words:
        return None

    answer = random.choice(long_words)
    question_text = sentence.replace(answer, "____", 1)

    pool = [w for w in all_long_words if w.lower() != answer.lower()]
    distractors = set(random.sample(pool, min(3, len(pool)))) if pool else set()
    while len(distractors) < 3:
        distractors.add(random.choice(["Concept", "Process", "Value", "Factor"]))

    options = list(distractors) + [answer]
    random.shuffle(options)

    return {
        "question": f"Fill in the blank: {question_text}",
        "options": options,
        "answer": answer,
    }


def make_true_false_question(sentence, all_sentences):
    """
    Creates a True/False question by either keeping the sentence as-is (True)
    or swapping in a numeric/keyword change to make it False, using another
    sentence's content as the distractor source. Adds variety alongside
    fill-in-the-blank questions.
    """
    numbers_in_sentence = re.findall(r"\d+(?:\.\d+)?", sentence)
    is_true = random.choice([True, False])

    if numbers_in_sentence and not is_true:
        # Alter a number to make the statement false
        original_number = random.choice(numbers_in_sentence)
        altered_number = str(int(float(original_number)) + random.choice([1, 2, 5, 10]))
        statement = sentence.replace(original_number, altered_number, 1)
        answer = "False"
    elif not is_true and len(all_sentences) > 1:
        # Swap in a fragment from a different sentence to make it false
        other = random.choice([s for s in all_sentences if s != sentence])
        other_words = other.split()
        this_words = sentence.split()
        if len(other_words) >= 3 and len(this_words) >= 3:
            statement = " ".join(this_words[:-2] + other_words[-2:])
            answer = "False"
        else:
            statement = sentence
            answer = "True"
    else:
        statement = sentence
        answer = "True"

    return {
        "question": f"True or False: \"{statement}\"",
        "options": ["True", "False"],
        "answer": answer,
    }


def generate_mcqs(sentences, num_questions=3):
    """
    Rule-based MCQ generator with two question styles (fill-in-the-blank and
    true/false) so quizzes don't feel repetitive. This is a placeholder for
    Phi-3.5 Mini Instruct in the final on-device build, which will generate
    genuinely comprehension-based questions instead of pattern-based ones.
    """
    candidates = [s for s in sentences if len(s.split()) >= 5]
    if not candidates:
        return []

    random.shuffle(candidates)
    all_words = [w.strip(string.punctuation) for s in candidates for w in s.split()]
    all_long_words = [w for w in all_words if len(w) > 4]

    mcqs = []
    for i, s in enumerate(candidates[:num_questions]):
        # Alternate style: even index -> fill-in-blank, odd index -> true/false
        if i % 2 == 0:
            q = make_fill_blank_question(s, all_long_words)
        else:
            q = make_true_false_question(s, candidates)

        if q:
            mcqs.append(q)

    return mcqs


sentences = split_sentences(final_text)

if final_text:
    summary = generate_summary(sentences)
    notes = generate_notes(sentences)
    mcqs = generate_mcqs(sentences)

    st.subheader("Quick Summary")
    st.info(summary)

    st.subheader("Notes")
    notes_markdown = "\n".join(f"- {point}" for point in notes)
    st.markdown(notes_markdown)

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
