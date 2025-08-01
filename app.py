import streamlit as st
from gtts import gTTS
import os
import tempfile
import random
from PyPDF2 import PdfReader

st.set_page_config(page_title="EchoVerse", layout="wide")

st.title("EchoVerse 🎙️ - Tone Adaptive Audiobook Generator")

with st.sidebar:
    st.header("Controls")

    # Upload text or PDF file
    uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])

    # Tone selection
    tone = st.selectbox("Select tone", ["Neutral", "Suspenseful", "Inspiring"])

    # Voice type selection (note: gTTS default voice only)
    voice_type = st.selectbox("Select voice type (Note: gTTS default voice only)", ["Male", "Female", "Child"])

    generate_button = st.button("Generate Audio")

def rewrite_text(text, tone):
    if tone == "Neutral":
        return text
    elif tone == "Suspenseful":
        sentences = text.split('.')
        suspense_words = ["Suddenly,", "Unexpectedly,", "In the shadows,", "Without warning,"]
        suspense_sentences = []
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            prefix = random.choice(suspense_words) + " " if random.random() < 0.5 else ""
            suspense_sentences.append(prefix + s + "...")
        return " ".join(suspense_sentences)
    elif tone == "Inspiring":
        sentences = text.split('.')
        inspiring_phrases = ["With great courage,", "Believe in yourself!", "Remember,", "You can achieve anything!"]
        inspiring_sentences = []
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            suffix = " " + random.choice(inspiring_phrases) if random.random() < 0.5 else ""
            inspiring_sentences.append(s + suffix + ".")
        return " ".join(inspiring_sentences)

input_text = ""

# Load text from file
if uploaded_file:
    if uploaded_file.type == "text/plain":
        input_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        input_text = ""
        for page in pdf_reader.pages:
            input_text += page.extract_text() or ""
else:
    input_text = st.text_area("Or paste your text here", height=250)

if generate_button:
    if not input_text.strip():
        st.error("Please provide some text!")
    else:
        with st.spinner("Generating audio..."):
            rewritten = rewrite_text(input_text, tone)

            st.subheader("Original vs Rewritten Text")
            col1, col2 = st.columns(2)
            col1.markdown("**Original Text:**")
            col1.text_area("", input_text, height=300, key="original_text_area")
            col2.markdown(f"**{tone} Tone Text:**")
            col2.text_area("", rewritten, height=300, key="rewritten_text_area")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts = gTTS(text=rewritten, lang="en")
                tts.save(tmp_file.name)
                audio_bytes = open(tmp_file.name, "rb").read()

            st.audio(audio_bytes, format="audio/mp3")
            st.download_button("⬇️ Download Audio", audio_bytes, file_name="echoverse_audio.mp3", mime="audio/mp3")

            os.remove(tmp_file.name)