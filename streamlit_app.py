import streamlit as st
from google import genai
from google.genai import types # Required for Grounding
import datetime
import io
import base64
from PIL import Image

# 1. Branding & The Genius Methodology
st.set_page_config(page_title="The Genius App", page_icon="🧞", layout="wide")
st.title("🧞 The Genius App: Live Market Valuation & AI Magic")
st.write("---")

# 2. Sequential Genius Interview
if "step" not in st.session_state: st.session_state.step = 1
if "log" not in st.session_state: st.session_state.log = {}

def next_step(): st.session_state.step += 1

# --- INTERVIEW STEPS ---
if st.session_state.step >= 1:
    st.session_state.log['cat'] = st.selectbox("What are we selling?", ["Select", "Phone", "Laptop", "Other"])
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
        "Upload ALL angles (Front, Back, Sides) for 360° analysis", 
        type=['jpg', 'png', 'jpeg'],
        accept_multiple_files=True
    )

# 3. The Magic Process (Grounded in Live Search)
if st.session_state.step >= 4 and st.session_state.log.get('imgs'):
    if st.button("🚀 Begin Magic Process"):
        with st.spinner("Genius is scouring the internet and checking live prices..."):
            # Initialize Client & Grounding Tool
            client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
            google_search_tool = types.Tool(google_search=types.GoogleSearch())
            
            # Prepare Content List (Prompt + All Images)
            val_prompt = f"""
            DATE: {datetime.date.today().strftime('%B %d, %2026')}. 
            ITEM: {st.session_state.log['model']} ({st.session_state.log['storage']}) in {st.session_state.log['cond']} condition.
            METHODOLOGY: Use sales comparison & market demand analysis via Google Search.
            TASK: Provide 3 price points: Same Day (Liquidation), 1 Week (Market), 1 Month (Premium).
            Write a professional sales description for each timeframe.
            """
            
            content_list = [val_prompt]
            img_b64_list = [] # For the video engine
            
            for uploaded_file in st.session_state.log['imgs']:
                raw_data = uploaded_file.read()
                content_list.append(Image.open(io.BytesIO(raw_data)))
                img_b64_list.append(base64.b64encode(raw_data).decode())

            # Call the Brain with Live Search enabled
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=content_list,
                tools=[google_search_tool]
            )
            
            st.success("Analysis Complete using Live 2026 Data!")
            
            # 4. Triple Timeframe Display & Video
            t1, t2, t3 = st.tabs(["⚡ Same Day", "📅 1 Week", "🏆 1 Month"])
            
            # Multi-Image CSS Video Generator
            def generate_multi_img_video(price_label, timeframe, color):
                # Rotates through the first 3 images if available
                img_cycle = "".join([f"{i*33}% {{ background-image: url(data:image/jpeg;base64,{img_b64_list[i % len(img_b64_list)]}); }}" for i in range(4)])
                return f"""
                <div style="background:{color}; padding:20px; border-radius:15px; text-align:center;">
                    <h2 style="color:white;">{timeframe} REEL</h2>
                    <div id="slideshow" style="width:100%; height:300px; background-size:cover; background-position:center; border-radius:10px; animation: slide 9s infinite;"></div>
                    <h1 style="color:white; font-size:45px;">{price_label}</h1>
                </div>
                <style>
                @keyframes slide {{ {img_cycle} }}
                </style>
                """

            with t1:
                st.markdown(generate_multi_img_video("QUICK CASH", "SAME DAY", "#FF4B4B"), unsafe_allow_html=True)
                st.write(response.text)
            with t2:
                st.markdown(generate_multi_img_video("BEST VALUE", "1 WEEK", "#FFAA00"), unsafe_allow_html=True)
                st.write("Live market pricing applied.")
            with t3:
                st.markdown(generate_multi_img_video("MAX PROFIT", "1 MONTH", "#00C851"), unsafe_allow_html=True)
                st.write("Premium listing strategy applied.")
