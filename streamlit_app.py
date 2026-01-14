import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import GoogleGemini # Direct integration
from openai import OpenAI 
import datetime
import io
import base64
from PIL import Image

# 1. Branding & Multi-Brain Setup
st.set_page_config(page_title="The Genius App", page_icon="🧞", layout="wide")
st.title("🧞 The Genius App: Multi-Brain (No Extra Keys)")

# 2. Setup Persistent Logs
if "log_data" not in st.session_state:
    st.session_state.log_data = pd.DataFrame(columns=["Date", "Item", "Storage", "Condition", "Price"])

# 3. Sidebar Configuration
st.sidebar.header("🧠 Brain Settings")
active_brain = st.sidebar.radio("Primary Valuation Brain", ["Gemini 2.0 (Live Market)", "Grok-3 (X/Sentiment)"])
enable_panda = st.sidebar.toggle("Enable Panda Analytics", value=True)

# 4. Sequential Interview
if "step" not in st.session_state: st.session_state.step = 1
def next_step(): st.session_state.step += 1

if st.session_state.step == 1:
    cat = st.selectbox("Category", ["Select", "Phone", "Laptop", "Other"])
    if cat != "Select":
        st.session_state.cat = cat
        st.button("Next ➡️", on_click=next_step)

elif st.session_state.step == 2:
    model_name = st.text_input("Model Name", placeholder="e.g. iPhone 17 Pro")
    if model_name:
        st.session_state.model_name = model_name
        st.button("Next ➡️", on_click=next_step)

elif st.session_state.step == 3:
    col1, col2 = st.columns(2)
    with col1: storage = st.selectbox("Storage", ["128GB", "256GB", "512GB", "1TB"])
    with col2: cond = st.select_slider("Condition", ["Poor", "Fair", "Good", "Mint"])
    st.session_state.details = {"storage": storage, "cond": cond}
    st.button("Next ➡️", on_click=next_step)

elif st.session_state.step >= 4:
    imgs = st.file_uploader("Upload 360° Photos", accept_multiple_files=True)
    
    if imgs:
        if st.button("🚀 Begin Multi-Brain Process"):
            with st.spinner(f"Consulting {active_brain}..."):
                try:
                    # --- VALUATION LOGIC ---
                    val_prompt = f"Appraise {st.session_state.model_name} {st.session_state.details['storage']} in {st.session_state.details['cond']} condition for Jan 2026."
                    
                    if active_brain == "Gemini 2.0 (Live Market)":
                        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
                        response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=[val_prompt, Image.open(imgs[0])],
                            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                        )
                        result_text = response.text
                    else:
                        grok = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")
                        response = grok.chat.completions.create(
                            model="grok-3",
                            messages=[{"role": "user", "content": val_prompt}]
                        )
                        result_text = response.choices[0].message.content

                    st.success("Analysis Complete!")
                    st.write(result_text)

                    # --- PANDAS AI (The History Brain) ---
                    # 1. Add this appraisal to our local log
                    new_entry = {
                        "Date": datetime.date.today(),
                        "Item": st.session_state.model_name,
                        "Storage": st.session_state.details['storage'],
                        "Condition": st.session_state.details['cond'],
                        "Price": 1000 # You can replace with logic to extract price from text
                    }
                    st.session_state.log_data = pd.concat([st.session_state.log_data, pd.DataFrame([new_entry])], ignore_index=True)

                    if enable_panda:
                        st.write("---")
                        st.subheader("🐼 Panda Analytics (Chat with your history)")
                        # We use Gemini as the Brain for Panda so NO extra key is needed
                        panda_llm = GoogleGemini(api_key=st.secrets["GOOGLE_API_KEY"])
                        sdf = SmartDataframe(st.session_state.log_data, config={"llm": panda_llm})
                        
                        panda_query = st.text_input("Ask Panda about your sales history:", "Show me a summary of today's appraisals")
                        if panda_query:
                            panda_res = sdf.chat(panda_query)
                            st.info(panda_res)

                except Exception as e:
                    st.error(f"Genie Hiccup: {e}")
