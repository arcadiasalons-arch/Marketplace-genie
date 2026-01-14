import streamlit as st
from google import genai
from google.genai import types
from openai import OpenAI
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import datetime
import re

st.set_page_config(page_title="The Genius App", layout="wide", page_icon="🧞")

# --- INITIALIZATION ---
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Date", "Item", "Value", "Hype"])

# Setup Clients
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
grok_client = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")

st.title("🧞 The Genius Multi-Brain")
st.markdown("---")

# --- INPUT SECTION ---
col_in1, col_in2 = st.columns([2, 1])
with col_in1:
    item = st.text_input("What are we appraising?", placeholder="e.g. 2024 MacBook Pro M3")
with col_in2:
    imgs = st.file_uploader("Upload Item Photo", type=['jpg', 'png', 'jpeg'])

# --- THE MAGIC PROCESS ---
if st.button("🚀 Run Multi-Brain Analysis") and item and imgs:
    with st.spinner("Consulting Gemini (Market) & Grok (Hype)..."):
        try:
            # 1. GEMINI: MARKET DATA (Visual Grounding)
            search_tool = types.Tool(google_search=types.GoogleSearch())
            img_obj = Image.open(imgs)
            
            gem_res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[f"Appraise {item} for Jan 2026 resale market.", img_obj],
                config=types.GenerateContentConfig(tools=[search_tool])
            )
            
            # 2. GROK: SENTIMENT (X-Platform Hype)
            # We explicitly ask for a numeric score for the Hype Meter
            grok_res = grok_client.chat.completions.create(
                model="grok-4", # Using the latest 2026 reasoning model
                messages=[{"role": "user", "content": f"Analyze X/Twitter hype for {item}. Return ONLY a number 1-10 followed by your analysis."}]
            )
            grok_text = grok_res.choices[0].message.content
            
            # Extract Score for Gauge (Safe Parsing)
            score_match = re.search(r'\b([1-9]|10)\b', grok_text)
            hype_score = int(score_match.group(1)) if score_match else 5

            # 3. DISPLAY RESULTS
            st.success("Appraisal Successful!")
            
            # Row 1: The Gauge & Summary
            res_col1, res_col2 = st.columns([1, 2])
            
            with res_col1:
                st.subheader("🔥 Hype Meter")
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = hype_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Grok Hype Score"},
                    gauge = {
                        'axis': {'range': [None, 10]},
                        'bar': {'color': "darkblue"},
                        'steps' : [
                            {'range': [0, 4], 'color': "lightgray"},
                            {'range': [4, 7], 'color': "gray"},
                            {'range': [7, 10], 'color': "gold"}
                        ],
                        'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 9}
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)

            with res_col2:
                st.subheader("📊 Gemini Market Analysis")
                st.write(gem_res.text)

            # Row 2: Grok's Full Commentary
            st.markdown("---")
            st.subheader("🐦 Grok Social Insights")
            st.write(grok_text)

            # Save to Session Log
            new_row = pd.DataFrame([{
                "Date": datetime.date.today(),
                "Item": item,
                "Value": "Analyzed",
                "Hype": hype_score
            }])
            st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)

        except Exception as e:
            st.error(f"Brain Sync Error: {e}")

# --- PANDA ANALYTICS ---
if not st.session_state.history.empty:
    st.write("---")
    st.subheader("🐼 Panda History Analytics")
    if st.button("Analyze Sales History"):
        history_str = st.session_state.history.to_string()
        panda_res = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"You are Panda, a data analyst. Based on this history:\n{history_str}\n\nWhat are the major trends?"
        )
        st.info(panda_res.text)
