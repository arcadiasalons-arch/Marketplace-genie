import streamlit as st
from google import genai
from google.genai import types
from openai import OpenAI
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import segno
from io import BytesIO
import re
import datetime

# --- CONFIG ---
st.set_page_config(page_title="Genie Kiosk", layout="centered", page_icon="🧞")

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Date", "Item", "Status", "Hype"])

# Setup Clients
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
grok_client = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")

st.title("🧞 Marketplace Genie: Redemption Build")

# --- INPUTS ---
item_name = st.text_input("Item to Appraise", placeholder="e.g. iPhone 17 Pro")
data_scan = st.file_uploader("📷 Step 1: Upload Settings > About Screen", type=['jpg','png','jpeg'])
mirror_scan = st.file_uploader("📷 Step 2: Upload a Mirror Photo (Front & Back)", type=['jpg','png','jpeg'])

# --- CORE LOGIC ---
if st.button("🚀 EXECUTE FULL ANALYSIS") and item_name and data_scan and mirror_scan:
    with st.spinner("Genie is syncing brains..."):
        try:
            # 1. VISUAL OCR (Hardware Identification)
            img_data = Image.open(data_scan)
            data_res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=["Extract the IMEI and Serial Number from this screen.", img_data]
            )
            imei = re.search(r'\d{15}', data_res.text).group(0) if re.search(r'\d{15}', data_res.text) else "Unknown"

            # 2. MARKET VALUATION (Google Search Grounding)
            search_tool = types.Tool(google_search=types.GoogleSearch())
            img_mirror = Image.open(mirror_scan)
            gemini_res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[f"Appraise this {item_name} for Jan 2026. Check mirror for cracks.", img_mirror],
                config=types.GenerateContentConfig(tools=[search_tool])
            )

            # 3. GROK HYPE (Social Sentiment)
            grok_res = grok_client.chat.completions.create(
                model="grok-3", # Stable model from that specific session
                messages=[{"role": "user", "content": f"Check X hype for {item_name}. Give a score 1-10."}]
            )
            score_match = re.search(r'\b([1-9]|10)\b', grok_res.choices[0].message.content)
            hype_val = int(score_match.group(1)) if score_match else 5

            # --- DISPLAY RESULTS ---
            st.success(f"✅ Device Identified: IMEI {imei}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🔥 Hype Meter")
                fig = go.Figure(go.Indicator(mode="gauge+number", value=hype_val, gauge={'axis': {'range': [1, 10]}, 'bar': {'color': "gold"}}))
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.subheader("💰 Instant Payout")
                st.metric("Cash Offer", "$435.00")
                st.write(gemini_res.text[:300] + "...")

            # Save state for voucher
            st.session_state.current_imei = imei

        except Exception as e:
            st.error(f"Genie Hiccup: {e}")

# --- VOUCHER SECTION ---
if "current_imei" in st.session_state:
    st.divider()
    if st.button("🧧 CLAIM CASH VOUCHER"):
        qr = segno.make(f"GENIE-PAY-{st.session_state.current_imei}-$435.00")
        buf = BytesIO()
        qr.save(buf, kind='png', scale=10)
        st.image(buf.getvalue(), caption="Scan at any Kiosk", width=250)
        st.balloons()
