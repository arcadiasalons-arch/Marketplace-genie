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
from tenacity import retry, stop_after_attempt, wait_random_exponential

# --- INITIALIZATION ---
st.set_page_config(page_title="Marketplace Genie", layout="centered", page_icon="🧞")

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Item", "IMEI", "Offer"])

# API Clients
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
grok = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")

# --- RECOVERY LOGIC (Fixes 429 Errors) ---
@retry(wait=wait_random_exponential(min=2, max=10), stop=stop_after_attempt(3))
def ask_genie_safely(prompt, image=None):
    content = [prompt]
    if image: content.append(image)
    return client.models.generate_content(
        model="gemini-2.0-flash",
        contents=content,
        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
    )

# --- APP INTERFACE ---
st.title("🧞 Marketplace Genie Kiosk")
st.write("Instant Buy-Back. Zero Manual Entry.")

# STEP 1: Define Inputs (Avoids NameErrors)
item_name = st.text_input("What are we appraising?", placeholder="e.g. iPhone 17 Pro")
data_scan = st.file_uploader("📷 Step 1: Upload photo of Settings > General > About", type=['jpg','png','jpeg'])
mirror_scan = st.file_uploader("📷 Step 2: Upload a mirror shot (Front & Back)", type=['jpg','png','jpeg'])

# --- ANALYSIS ENGINE ---
if st.button("🚀 EXECUTE DIAGNOSTICS"):
    if not (item_name and data_scan and mirror_scan):
        st.warning("Please provide the item name and both photos to proceed.")
    else:
        with st.spinner("Genie is analyzing hardware & market hype..."):
            try:
                # 1. OCR Data Extraction (IMEI/Serial)
                img_data = Image.open(data_scan)
                data_res = ask_genie_safely("Extract ONLY the IMEI and Serial Number from this screen.", img_data)
                imei = re.search(r'\d{15}', data_res.text).group(0) if re.search(r'\d{15}', data_res.text) else "Pending"
                
                # 2. Visual & Market Appraisal
                img_mirror = Image.open(mirror_scan)
                market_res = ask_genie_safely(f"Appraise this {item_name}. Check mirror for cracks. Give an 'Instant Cash' offer vs eBay value.", img_mirror)
                
                # 3. Grok Hype Sentiment
                grok_res = grok.chat.completions.create(
                    model="grok-4",
                    messages=[{"role": "user", "content": f"Is {item_name} trending? Give a hype score 1-10 and 1 sentence why."}]
                )
                hype_score = int(re.search(r'\b([1-9]|10)\b', grok_res.choices[0].message.content).group(1))

                # --- RESULTS DISPLAY ---
                st.success(f"✅ Diagnostics Complete: IMEI {imei}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🔥 Hype Meter")
                    fig = go.Figure(go.Indicator(mode="gauge+number", value=hype_score, gauge={'axis': {'range': [1, 10]}, 'bar': {'color': "gold"}}))
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("💰 Instant Offer")
                    st.metric("Cash Payout", "$420.00", "Top Tier")
                    st.write(market_res.text[:300] + "...")

                # Store for Voucher
                st.session_state.current_offer = {"item": item_name, "imei": imei, "price": "$420.00"}

            except Exception as e:
                st.error(f"Genie Hiccup: {e}")

# --- VOUCHER GENERATOR ---
if "current_offer" in st.session_state:
    st.divider()
    if st.button("🧧 Claim Instant Payout Voucher"):
        offer = st.session_state.current_offer
        qr = segno.make(f"GENIE-PAY-{offer['imei']}-{offer['price']}")
        buf = BytesIO()
        qr.save(buf, kind='png', scale=10)
        
        st.image(buf.getvalue(), caption="Scan at Kiosk", width=250)
        st.download_button("Download PDF Voucher", buf.getvalue(), "Genie_Voucher.png", "image/png")
        st.balloons()
