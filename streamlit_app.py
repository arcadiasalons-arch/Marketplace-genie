import streamlit as st
from google import genai
from google.genai import types 
import datetime
import io
import base64
from PIL import Image

# 1. Branding
st.set_page_config(page_title="The Genius App", page_icon="🧞", layout="wide")
st.title("🧞 The Genius App: Real Data, AI Magic!")
st.write("---")

# 2. Sequential Genius Interview
if "step" not in st.session_state: st.session_state.step = 1
if "log" not in st.session_state: st.session_state.log = {}

def next_step(): st.session_state.step += 1

if st.session_state.step >= 1:
    st.session_state.log['cat'] = st.selectbox("What are you selling?", ["Select", "Phone", "Laptop", "Other"])
    if st.session_state.log['cat'] != "Select" and st.session_state.step == 1: st.button("Next ➡️", on_click=next_step)

if st.session_state.step >= 2:
    st.session_state.log['model'] = st.text_input("Exact Model Name", placeholder="e.g. iPhone 17 Pro")
    if st.session_state.log['model'] and st.session_state.step == 2: st.button("Next ➡️", on_click=next_step)

if st.session_state.step >= 3:
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.log['storage'] = st.selectbox("Storage", ["128GB", "256GB", "512GB", "1TB"])
    with col2:
        st.session_state.log['cond'] = st.select_slider("Condition", ["Poor", "Fair", "Good", "Mint"])
    if st.session_state.step == 3: st.button("Next ➡️", on_click=next_step)

if st.session_state.step >= 4:
    st.session_state.log['imgs'] = st.file_uploader(
        "Upload angles (Front, Back, Sides)", 
        type=['jpg', 'png', 'jpeg'],
        accept_multiple_files=True
    )

# 3. The Stabilized Magic Process
if st.session_state.step >= 4 and st.session_state.log.get('imgs'):
    if st.button("🚀 Begin Magic Process"):
        with st.spinner("Genius is checking live 2026 marketplace data..."):
            try:
                client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
                
                # Setup Grounding
                google_search_tool = types.Tool(google_search=types.GoogleSearch())
                
                # Prepare data
                val_prompt = f"Search live 2026 prices for {st.session_state.log['model']} ({st.session_state.log['storage']}) in {st.session_state.log['cond']} condition. Provide Same Day, 1 Week, and 1 Month prices with descriptions."
                
                # To prevent ClientError, we send the prompt and the main (first) image for search grounding
                main_img_file = st.session_state.log['imgs'][0]
                main_img = Image.open(main_img_file)
                
                # Save base64 for the video reel
                main_img_file.seek(0)
                img_b64 = base64.b64encode(main_img_file.read()).decode()

                # Execute stabilized call
                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=[val_prompt, main_img],
                    config=types.GenerateContentConfig(
                        tools=[google_search_tool]
                    )
                )
                
                st.success("Analysis Complete!")
                
                # 4. Display
                t1, t2, t3 = st.tabs(["⚡ Same Day", "📅 1 Week", "🏆 1 Month"])
                
                def generate_reel(label, color):
                    return f"""
                    <div style="background:{color}; padding:20px; border-radius:15px; text-align:center;">
                        <h2 style="color:white;">{label} REEL</h2>
                        <div style="width:100%; height:300px; background-image: url(data:image/jpeg;base64,{img_b64}); background-size:cover; background-position:center; border-radius:10px; animation: zoom 8s infinite alternate;"></div>
                    </div>
                    <style>@keyframes zoom {{ from {{transform: scale(1);}} to {{transform: scale(1.1);}} }}</style>
                    """

                with t1:
                    st.markdown(generate_reel("SAME DAY", "#FF4B4B"), unsafe_allow_html=True)
                    st.write(response.text)
                with t2:
                    st.markdown(generate_reel("1 WEEK", "#FFAA00"), unsafe_allow_html=True)
                with t3:
                    st.markdown(generate_reel("1 MONTH", "#00C851"), unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Genius encountered a hiccup: {e}")
                st.info("Try uploading just 1 or 2 high-quality photos if this persists.")
