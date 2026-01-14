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

# 2. Sequential Genius Interview (Appears one by one)
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

if st.session_state.step >= 4:
    st.session_state.log['img'] = st.file_uploader("Upload Item Photo for High-Res Analysis", type=['jpg', 'png'])

# 3. The Magic Process & Triple Timeframe Logic
if st.session_state.step >= 4 and st.session_state.log.get('img'):
    if st.button("✨ Begin Magic Process"):
        with st.spinner("Genius is scouring the internet..."):
            # --- AI BRAIN VALUATION ---
            client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
            img = Image.open(st.session_state.log['img'])
            
            prompt = f"DATE: Jan 2026. Appraise {st.session_state.log['model']}. Provide: 1. Same Day Price, 2. One Week Price, 3. One Month Price. Write a pro description for each."
            response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=[prompt, img])
            
            st.success("Analysis Complete!")
            
            # 4. Triple Timeframe Display
            t1, t2, t3 = st.tabs(["⚡ Same Day", "📅 1 Week", "🏆 1 Month"])
            
            # --- SIMULATED VIDEO ENGINE (CSS ANIMATION) ---
            # We convert the image to base64 so it can be 'animated' in the video
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode()

            def generate_video_html(price, label, color):
                return f"""
                <div style="background:{color}; padding:20px; border-radius:15px; text-align:center; animation: fadeIn 2s;">
                    <h2 style="color:white; font-family:sans-serif;">{label}</h2>
                    <div style="overflow:hidden; border-radius:10px;">
                        <img src="data:image/jpeg;base64,{img_b64}" style="width:100%; animation: zoom 10s infinite alternate;">
                    </div>
                    <h1 style="color:white; font-size:50px;">{price}</h1>
                    <p style="color:white;">{st.session_state.log['model']} - {st.session_state.log['cond']}</p>
                </div>
                <style>
                @keyframes zoom {{ from {{transform: scale(1);}} to {{transform: scale(1.2);}} }}
                @keyframes fadeIn {{ from {{opacity: 0;}} to {{opacity: 1;}} }}
                </style>
                """

            with t1:
                st.markdown(generate_video_html("QUICK SALE", "SAME DAY", "#FF4B4B"), unsafe_allow_html=True)
                st.write(response.text)
            
            with t2:
                st.markdown(generate_video_html("MARKET PRICE", "1 WEEK", "#FFAA00"), unsafe_allow_html=True)
                st.write("Best for Facebook Marketplace or local groups.")

            with t3:
                st.markdown(generate_video_html("PREMIUM VALUE", "1 MONTH", "#00C851"), unsafe_allow_html=True)
                st.write("Best for eBay or specialized collectors.")
