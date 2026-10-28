
import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
import whisper
from deep_translator import GoogleTranslator
from moviepy.editor import VideoFileClip, AudioFileClip

st.set_page_config(page_title="Myanmar AI Dubbing", page_icon="🎬")

st.title("🎬 Myanmar AI Auto Dubbing")
st.write("Upload video → Transcribe → Translate → Burmese Voice")

uploaded = st.file_uploader(
    "ဗီဒီယိုဖိုင် ရွေးပါ",
    type=["mp4", "mov", "mkv"]
)

if uploaded:
    st.video(uploaded)

    if st.button("မြန်မာအသံ ပြောင်းမယ်"):
        with tempfile.TemporaryDirectory() as tmp:
            video_path = os.path.join(tmp, "input.mp4")
            audio_path = os.path.join(tmp, "source.wav")
            voice_path = os.path.join(tmp, "burmese.mp3")
            output_path = os.path.join(tmp, "dubbed.mp4")

            with open(video_path, "wb") as f:
                f.write(uploaded.getbuffer())

            try:
                with st.spinner("ဗီဒီယိုအသံကို ဖတ်နေပါတယ်..."):
                    video = VideoFileClip(video_path)
                    if video.audio is None:
                        st.error("ဒီဗီဒီယိုမှာ အသံမပါပါ")
                        st.stop()

                    video.audio.write_audiofile(
                        audio_path, logger=None
                    )

                    model = whisper.load_model("base")
                    result = model.transcribe(audio_path)
                    original_text = result["text"].strip()

                st.subheader("မူရင်းစကားပြောစာသား")
                st.write(original_text)

                with st.spinner("မြန်မာဘာသာပြန်နေပါတယ်..."):
                    translated = GoogleTranslator(
                        source="auto", target="my"
                    ).translate(original_text)

                st.subheader("မြန်မာဘာသာပြန်စာသား")
                st.write(translated)

                with st.spinner("မြန်မာအသံ ဖန်တီးနေပါတယ်..."):
                    async def make_voice():
                        tts = edge_tts.Communicate(
                            translated,
                            voice="my-MM-NilarNeural"
                        )
                        await tts.save(voice_path)

                    asyncio.run(make_voice())

                with st.spinner("ဗီဒီယိုနှင့် အသံ ပေါင်းနေပါတယ်..."):
                    voice = AudioFileClip(voice_path)
                    final_video = video.set_audio(voice)
                    final_video.write_videofile(
                        output_path,
                        codec="libx264",
                        audio_codec="aac",
                        logger=None
                    )

                    with open(output_path, "rb") as f:
                        video_bytes = f.read()

                    st.success("ပြီးပါပြီ!")
                    st.download_button(
                        "ဗီဒီယိုကို Download လုပ်ရန်",
                        data=video_bytes,
                        file_name="myanmar_dubbed.mp4",
                        mime="video/mp4"
                    )

                    voice.close()
                    final_video.close()
                    video.close()

            except Exception as e:
