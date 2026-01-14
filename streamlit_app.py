import streamlit as st
from google import genai
from google.genai import types 
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

if st.session_state.step >= 4:
    st.session_state.log['imgs'] = st.file_uploader(
        "Upload ALL angles (Front, Back, Sides) for 360° analysis", 
        type=['jpg', 'png', 'jpeg'],
        accept_multiple_files=True
    )

# 3. The Magic Process (Fixed Config for Live Search)
if st.session_state.step >= 4 and st.session_state.log.get('imgs'):
    if st.button("🚀 Begin Magic Process"):
        with st.spinner("Genius is checking live 2026 marketplace data..."):
            # Initialize Client
            client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
            
            # Setup Grounding (The fix for bad pricing)
            google_search_tool = types.Tool(google_search=types.GoogleSearch())
            
            # Prepare Prompt & Images
            val_prompt = f"""
            DATE: {datetime.date.today().strftime('%B %d, %2026')}. 
            ITEM: {st.session_state.log['model']} ({st.session_state.log['storage']}) in {st.session_state.log['cond']} condition.
            TASK: Use Google Search to find real-time prices for: Same Day, 1 Week, and 1 Month. 
            Also write a professional description for each.
            """
            
            content_list = [val_prompt]
            img_b64_list = []
            
            for uploaded_file in st.session_state.log['imgs']:
                raw_data = uploaded_file.read()
                content_list.append(Image.open(io.BytesIO(raw_data)))
                img_b64_list.append(base64.b64encode(raw_data).decode())

            # 4. Execute with Grounding Config
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=content_list,
                config=types.GenerateContentConfig(
                    tools=[google_search_tool]
                )
            )
            
            st.success("Analysis Complete using Live Market Data!")
            
            # 5. Display Logic
            t1, t2, t3 = st.tabs(["⚡ Same Day", "📅 1 Week", "🏆 1 Month"])
            
            def generate_reel_html(label, color):
                img_cycle = "".join([f"{i*33}% {{ background-image: url(data:image/jpeg;base64,{img_b64_list[i % len(img_b64_list)]}); }}" for i in range(4)])
                return f"""
                <div style="background:{color}; padding:20px; border-radius:15px; text-align:center;">
                    <h2 style="color:white;">{label} REEL</h2>
                    <div style="width:100%; height:300px; background-size:cover; background-position:center; border-radius:10px; animation: slide 9s infinite;"></div>
                </div>
                <style>@keyframes slide {{ {img_cycle} }}</style>
                """

            with t1:
                st.markdown(generate_reel_html("SAME DAY", "#FF4B4B"), unsafe_allow_html=True)
                st.write(response.text)
            with t2:
                st.markdown(generate_reel_html("1 WEEK", "#FFAA00"), unsafe_allow_html=True)
                st.info("Pricing based on live marketplace trends.")
            with t3:
                st.markdown(generate_reel_html("1 MONTH", "#00C851"), unsafe_allow_html=True)
                st.info("Premium value for patient sellers.")
