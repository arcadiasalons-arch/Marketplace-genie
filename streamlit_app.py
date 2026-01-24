import streamlit as st
from google import genai
from google.genai import types
from openai import OpenAI
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import re
from tenacity import retry, stop_after_attempt, wait_random_exponential

# --- SETUP ---
st.set_page_config(page_title="Marketplace Genie", layout="centered", page_icon="🧞")

# Ensure inputs are defined BEFORE use to prevent NameErrors
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
grok = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")

# --- BULLETPROOF AI CALLS ---
@retry(wait=wait_random_exponential(min=2, max=10), stop=stop_after_attempt(3), reraise=True)
def run_genie_scan(prompt, image):
    # Fix for 400/404 errors: Using 2.0-Flash and correct tool nesting
    search_tool = types.Tool(google_search=types.GoogleSearch())
    return client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, image],
        config=types.GenerateContentConfig(tools=[search_tool])
    )

st.title("🧞 Marketplace Genie Kiosk")
st.write("Instant Diagnostics. Zero Friction.")

# User Inputs
item_name = st.text_input("Device Name", placeholder="e.g. iPhone 17 Pro Max")
data_scan = st.file_uploader("📷 Step 1: Upload Settings > About Screen", type=['jpg','png','jpeg'])
mirror_scan = st.file_uploader("📷 Step 2: Upload a Mirror Photo (Front & Back)", type=['jpg','png','jpeg'])

if st.button("🚀 EXECUTE DIAGNOSTICS"):
    if not (item_name and data_scan and mirror_scan):
        st.error("Missing inputs! The Genie needs both photos to work.")
    else:
        with st.spinner("Analyzing hardware..."):
            try:
                # 1. Automated IMEI/Serial Extraction
                img_data = Image.open(data_scan)
                data_res = run_genie_scan("Extract IMEI and Serial from this screen.", img_data)
                imei = re.search(r'\d{15}', data_res.text).group(0) if re.search(r'\d{15}', data_res.text) else "Unknown"

                # 2. Visual Damage & Pricing
                img_mirror = Image.open(mirror_scan)
                price_res = run_genie_scan(f"Appraise this {item_name}. Look for cracks. Offer a payout.", img_mirror)

                # 3. Hype Meter (Grok)
                grok_res = grok.chat.completions.create(
                    model="grok-4",
                    messages=[{"role": "user", "content": f"Score 1-10 hype for {item_name}."}]
                )
                score = int(re.search(r'\b([1-9]|10)\b', grok_res.choices[0].message.content).group(1))

                # --- UI DISPLAY ---
                st.success(f"✅ Device Identified: IMEI {imei}")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("🔥 Hype Meter")
                    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, gauge={'axis': {'range': [1,10]}, 'bar': {'color': "gold"}}))
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    st.subheader("💰 Instant Payout")
                    st.metric("Cash Offer", "$450.00")
                    st.write(price_res.text[:200] + "...")

            except Exception as e:
                st.error(f"Genie Hiccup: {str(e)}")
