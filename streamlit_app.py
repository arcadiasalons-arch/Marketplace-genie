import streamlit as st
from google import genai
from google.genai import types 
import datetime
import io
import base64
import time
from PIL import Image

# 1. Branding
st.set_page_config(page_title="The Genius App", page_icon="🧞", layout="wide")
st.title("🧞 The Genius App: Self-Healing Edition")

# 2. State Management
if "step" not in st.session_state: st.session_state.step = 1
if "log" not in st.session_state: st.session_state.log = {}

def next_step(): st.session_state.step += 1

# --- INTERVIEW INTERFACE ---
if st.session_state.step == 1:
    st.session_state.log['cat'] = st.selectbox("What are we selling?", ["Select", "Phone", "Laptop", "Other"])
    if st.session_state.log['cat'] != "Select": st.button("Next ➡️", on_click=next_step)

elif st.session_state.step == 2:
    st.session_state.log['model'] = st.text_input("Exact Model Name")
    if st.session_state.log['model']: st.button("Next ➡️", on_click=next_step)

elif st.session_state.step == 3:
    col1, col2 = st.columns(2)
    with col1: st.session_state.log['storage'] = st.selectbox("Storage", ["128GB", "256GB", "512GB", "1TB"])
    with col2: st.session_state.log['cond'] = st.select_slider("Condition", ["Poor", "Fair", "Good", "Mint"])
    st.button("Next ➡️", on_click=next_step)

elif st.session_state.step >= 4:
    st.session_state.log['imgs'] = st.file_uploader("Upload Item Photos", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

# 3. THE SELF-HEALING ENGINE (Exponential Backoff)
def call_genie_with_retry(client, prompt, image, max_retries=3):
    delay = 2  # Start with 2 second delay
    for i in range(max_retries):
        try:
            # We try Gemini 1.5 Flash first as it has higher free limits in 2026
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            return response
        except Exception as e:
            if "429" in str(e) and i < max_retries - 1:
                st.warning(f"🧞 Genie is catching its breath... Retrying in {delay}s (Attempt {i+1}/{max_retries})")
                time.sleep(delay)
                delay *= 2 # Wait longer each time
            else:
                raise e

# 4. Execution
if st.session_state.step >= 4 and st.session_state.log.get('imgs'):
    if st.button("🚀 Begin Magic Process"):
        with st.spinner("Genius is analyzing market data (this may take 30-60s due to free tier limits)..."):
            try:
                client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
                
                # Setup
                val_prompt = f"ACT AS: The Genius App. Search live Jan 2026 prices for {st.session_state.log['model']} {st.session_state.log['storage']} in {st.session_state.log['cond']} condition. Provide Same Day, 1 Week, and 1 Month prices."
                
                # Use only the 1st image to save quota
                main_img_file = st.session_state.log['imgs'][0]
                main_img = Image.open(main_img_file)
                
                # Execute with retry logic
                response = call_genie_with_retry(client, val_prompt, main_img)
                
                st.success("Appraisal Successful!")
                
                # 5. Display & Video Reel
                main_img_file.seek(0)
                img_b64 = base64.b64encode(main_img_file.read()).decode()
                
                t1, t2, t3 = st.tabs(["⚡ Same Day", "📅 1 Week", "🏆 1 Month"])
                
                def get_reel(color):
                    return f'<div style="background:{color}; padding:10px; border-radius:10px; text-align:center;"><img src="data:image/jpeg;base64,{img_b64}" width="100%" style="border-radius:10px; animation: pulse 4s infinite;"></div><style>@keyframes pulse {{ 0%{{opacity:0.8;}} 50%{{opacity:1;}} 100%{{opacity:0.8;}} }}</style>'

                with t1:
                    st.markdown(get_reel("#FF4B4B"), unsafe_allow_html=True)
                    st.write(response.text)
                with t2: st.markdown(get_reel("#FFAA00"), unsafe_allow_html=True)
                with t3: st.markdown(get_reel("#00C851"), unsafe_allow_html=True)

            except Exception as e:
                st.error("The Free Tier is currently overloaded. Please wait 1 minute before clicking 'Begin' again.")
