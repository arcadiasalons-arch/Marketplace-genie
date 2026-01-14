import streamlit as st
from google import genai
import datetime
import io
import base64
from PIL import Image

# 1. Branding & The Genius Methodology
st.set_page_config(page_title="The Genius App", page_icon="🧞", layout="wide")
st.title("🧞 The Genius App: Real Data, Actual Results, AI Magic!")
st.write("---")

# 2. Sequential Genius Interview
if "step" not in st.session_state: st.session_state.step = 1
if "log" not in st.session_state: st.session_state.log = {}

def next_step(): st.session_state.step += 1

# --- INTERVIEW STEPS ---
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

# --- UPDATED STEP 4: MULTI-PHOTO UPLOADER ---
if st.session_state.step >= 4:
    st.session_state.log['imgs'] = st.file_uploader(
        "Upload ALL angles (Front, Back, Sides) for 360° analysis", 
        type=['jpg', 'png', 'jpeg'],
        accept_multiple_files=True # Allows more than one photo
    )

# 3. The Magic Process (Updated for Multi-Image)
if st.session_state.step >= 4 and st.session_state.log.get('imgs'):
    if st.button("✨ Begin Magic Process"):
        with st.spinner("Genius is scouring the internet and analyzing all angles..."):
            client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
            
            # Prepare the "Brain" content list
            # We add the text prompt first, then append all images
            val_prompt = f"""
            DATE: Jan 2026. 
            ITEM: {st.session_state.log['model']} ({st.session_state.log['storage']}) in {st.session_state.log['cond']} condition.
            TASK: Review ALL attached images for wear/damage. 
            PROVIDE: 1. Same Day Price, 2. One Week Price, 3. One Month Price. 
            Write a professional sales description for each.
            """
            
            content_list = [val_prompt]
            
            # Loop through all uploaded files and open them
            for uploaded_file in st.session_state.log['imgs']:
                content_list.append(Image.open(uploaded_file))
            
            # Send everything to Gemini
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite", 
                contents=content_list
            )
            
            st.success(f"360° Analysis Complete! ({len(st.session_state.log['imgs'])} images processed)")
            
            # 4. Triple Timeframe Display
            t1, t2, t3 = st.tabs(["⚡ Same Day", "📅 1 Week", "🏆 1 Month"])
            
            # --- VIDEO REEL ENGINE (Uses the first image for the animation) ---
            first_img = Image.open(st.session_state.log['imgs'][0])
            buffered = io.BytesIO()
            first_img.save(buffered, format="JPEG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode()

            def generate_video_html(price_label, timeframe, color):
                return f"""
                <div style="background:{color}; padding:20px; border-radius:15px; text-align:center; animation: fadeIn 2s;">
                    <h2 style="color:white; font-family:sans-serif;">{timeframe}</h2>
                    <div style="overflow:hidden; border-radius:10px;">
                        <img src="data:image/jpeg;base64,{img_b64}" style="width:100%; animation: zoom 10s infinite alternate;">
                    </div>
                    <h1 style="color:white; font-size:40px;">{price_label}</h1>
                </div>
                <style>
                @keyframes zoom {{ from {{transform: scale(1);}} to {{transform: scale(1.1);}} }}
                @keyframes fadeIn {{ from {{opacity: 0;}} to {{opacity: 1;}} }}
                </style>
                """

            with t1:
                st.markdown(generate_video_html("QUICK SALE", "SAME DAY", "#FF4B4B"), unsafe_allow_html=True)
                st.write(response.text)
            
            with t2:
                st.markdown(generate_video_html("MARKET PRICE", "1 WEEK", "#FFAA00"), unsafe_allow_html=True)
                st.write("Targeting local marketplace buyers.")

            with t3:
                st.markdown(generate_video_html("PREMIUM VALUE", "1 MONTH", "#00C851"), unsafe_allow_html=True)
                st.write("Targeting collectors and national shipping buyers.")
