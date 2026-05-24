import streamlit as st
import os
# Assuming the backend pipeline can be imported like this based on the repo structure
# You may need to inspect core/pipeline.py to see the exact function names
from core.pipeline import process_video 

st.title("ReFlow Studio - Web Interface")

# 1. File Uploaders
uploaded_video = st.file_uploader("Upload Video", type=["mp4", "mkv", "avi"])
uploaded_voice = st.file_uploader("Upload Voice Reference (Optional)", type=["wav", "mp3"])

# 2. Configuration Options
target_language = st.selectbox("Target Language", ["English", "Hindi", "Spanish", "French", "Japanese"])
preserve_bg = st.checkbox("Preserve Background Audio (UVR5)")
enable_lipsync = st.checkbox("Enable Lip Sync")
enable_face_enhancer = st.checkbox("Enable Face Enhancer (GFPGAN)")

# 3. Processing
if st.button("Start Processing"):
    if uploaded_video is not None:
        st.info("Processing started! Check the backend terminal for progress.")
        
        # Save the uploaded files to a temp directory so the backend can read them
        video_path = os.path.join("temp", uploaded_video.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_video.getbuffer())
            
        voice_path = None
        if uploaded_voice:
            voice_path = os.path.join("temp", uploaded_voice.name)
            with open(voice_path, "wb") as f:
                f.write(uploaded_voice.getbuffer())
        
        # Pass the configurations to the ReFlow Studio backend pipeline
        # (You will need to adjust the arguments based on how core.pipeline is structured)
        try:
            output_file = process_video(
                video_path=video_path,
                voice_ref_path=voice_path,
                language=target_language,
                preserve_bg=preserve_bg,
                lip_sync=enable_lipsync,
                enhance_face=enable_face_enhancer
            )
            
            st.success("Processing Complete!")
            st.video(output_file)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload a video first.")
