import streamlit as st
from google import genai
from google.genai import types
from openai import OpenAI
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import datetime
import re

# --- PAGE SETUP ---
st.set_page_config(page_title="The Genius App", layout="wide", page_icon="🧞")

# Persistent History for Panda
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Date", "Item", "Status", "Hype"])

# --- API CLIENTS ---
# Using Gemini 2.0 (Stable) and Grok-4
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
grok_client = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")

st.title("🧞 The Genius: Triple-Brain Redemption")
st.info("January 2026 Engine: Gemini 2.0 + Grok-4 + Panda Analyst")

# --- USER INTERFACE ---
col1, col2 = st.columns([2, 1])
with col1:
    item_name = st.text_input("Item to Appraise", placeholder="e.g. iPhone 17 Pro Max 512GB")
with col2:
    uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])

if st.button("🚀 EXECUTE FULL ANALYSIS") and item_name and uploaded_file:
    with st.spinner("Brains are syncing..."):
        try:
            # --- BRAIN 1: GEMINI 2.0 (Visual Market Research) ---
            # Correct 2026 Syntax for Google Search Tool
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            img = Image.open(uploaded_file)
            
            gemini_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[f"Provide a 2026 market price for {item_name} based on this image.", img],
                config=types.GenerateContentConfig(tools=[grounding_tool])
            )
            
            # --- BRAIN 2: GROK-4 (Social Hype & Sentiment) ---
            # Grok-4 is specifically prompted to return a number for the gauge
            grok_response = grok_client.chat.completions.create(
                model="grok-4",
                messages=[{"role": "user", "content": f"Check X/Twitter hype for {item_name}. Give me a sentiment score from 1-10 followed by a 2-sentence explanation."}]
            )
            grok_text = grok_response.choices[0].message.content
            
            # --- HYPE METER LOGIC ---
            # Regex extracts the first number (1-10) found in Grok's response
            score_match = re.search(r'\b([1-9]|10)\b', grok_text)
            hype_val = int(score_match.group(1)) if score_match else 5

            # --- DISPLAY RESULTS ---
            st.success("Analysis Synced Successfully!")
            
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                st.subheader("🔥 Grok Hype Meter")
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = hype_val,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    gauge = {
                        'axis': {'range': [1, 10]},
                        'bar': {'color': "#FF4B4B"},
                        'steps': [
                            {'range': [1, 4], 'color': "#E5E5E5"},
                            {'range': [4, 7], 'color': "#FCA311"},
                            {'range': [7, 10], 'color': "#FFD700"}
                        ]
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
                st.write(f"**Grok says:** {grok_text}")

            with res_col2:
                st.subheader("📊 Gemini Market Valuation")
                st.write(gemini_response.text)

            # Update History
            new_entry = pd.DataFrame([{
                "Date": datetime.date.today(),
                "Item": item_name,
                "Status": "Verified",
                "Hype": hype_val
            }])
            st.session_state.history = pd.concat([st.session_state.history, new_entry], ignore_index=True)

        except Exception as e:
            st.error(f"Redemption Failed: {str(e)}")
            st.warning("Ensure your API keys are correct in the Secrets tab.")

# --- BRAIN 3: PANDAS ANALYTICS (AI-Powered) ---
if not st.session_state.history.empty:
    st.divider()
    st.subheader("🐼 Panda History Brain")
    if st.button("Generate Trend Report"):
        history_summary = st.session_state.history.to_string()
        # Gemini acts as the Panda Data Analyst to avoid SciPy library conflicts
        panda_analysis = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"You are a Data Analyst named Panda. Analyze this log:\n{history_summary}"
        )
        st.info(panda_analysis.text)
