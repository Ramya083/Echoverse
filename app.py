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

    # 1. PDF Page Range Selection
    uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])
    page_range = None
    if uploaded_file and uploaded_file.type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        num_pages = len(pdf_reader.pages)
        page_range = st.slider("Select PDF page range", 1, num_pages, (1, num_pages))

    # 2. Custom Tone Editor
    custom_tone = st.text_input("Custom tone phrase (optional)", "")

    # Tone selection
    tone = st.selectbox("Select tone", ["Neutral", "Suspenseful", "Inspiring", "Custom"])

    # 3. Audio Speed Control
    speed = st.selectbox("Audio speed", ["0.75x", "1x", "1.25x"], index=1)

    # 4. Text Summarization Option
    summarize = st.checkbox("Summarize text before generating audio (beta)")

    # 5. Multi-language Support
    language = st.selectbox("Select language", ["en", "hi", "es", "fr", "de", "te", "ta", "zh"])

    generate_button = st.button("Generate Audio")

def summarize_text(text):
    # Simple summarization: return first 5 sentences
    sentences = text.split('.')
    return '.'.join(sentences[:5]) + '.' if len(sentences) > 5 else text

def rewrite_text(text, tone, custom_tone_phrase=""):
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
    elif tone == "Custom" and custom_tone_phrase:
        sentences = text.split('.')
        custom_sentences = []
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            custom_sentences.append(f"{custom_tone_phrase} {s}.")
        return " ".join(custom_sentences)
    else:
        return text

input_text = ""

# Load text from file
if uploaded_file:
    if uploaded_file.type == "text/plain":
        input_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        input_text = ""
        start, end = page_range if page_range else (1, len(pdf_reader.pages))
        for i in range(start-1, end):
            input_text += pdf_reader.pages[i].extract_text() or ""
else:
    input_text = st.text_area("Or paste your text here", height=250)

if generate_button:
    if not input_text.strip():
        st.error("Please provide some text!")
    else:
        with st.spinner("Generating audio..."):
            # 4. Summarize if requested
            #processed_text = summarize_text(input_text) if summarize else input_text
            # 2. Custom tone support
            #rewritten = rewrite_text(processed_text, tone, custom_tone)
            custom_tone = st.text_input("Custom tone phrase (optional)", "")

            st.subheader("Original vs Rewritten Text")
            col1, col2 = st.columns(2)
            col1.markdown("**Original Text:**")
            col1.text_area("", input_text, height=300, key="original_text_area")
            col2.markdown(f"**{tone} Tone Text:**")
            col2.text_area("", rewritten, height=300, key="rewritten_text_area")

            # 3. Audio Speed Control (gTTS does not natively support speed, so we use a workaround)
            tts = gTTS(text=rewritten, lang=language)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                audio_bytes = open(tmp_file.name, "rb").read()

            st.audio(audio_bytes, format="audio/mp3")
            st.download_button("⬇️ Download Audio", audio_bytes, file_name="echoverse_audio.mp3", mime="audio/mp3")

            os.remove(tmp_file.name)

            if speed != "1x":
                st.info("Note: Audio speed adjustment is not natively supported by gTTS. Use an external tool or player to adjust playback speed .")