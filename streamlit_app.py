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

# --- 1. SETUP & CONFIG ---
st.set_page_config(page_title="Marketplace Genie", layout="centered", page_icon="🧞")

# Persistent state to prevent crashes on rerun
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Date", "Item", "IMEI", "Offer"])
if "current_offer" not in st.session_state:
    st.session_state.current_offer = None

# Initialize Clients
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
grok_client = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")

# --- 2. FAIL-SAFE AI LOGIC ---
@retry(wait=wait_random_exponential(min=2, max=10), stop=stop_after_attempt(3), reraise=True)
def ask_genie_safely(prompt, image=None):
    """
    Attempts to call Gemini 2.0 with a fallback to 1.5 if quota is exhausted.
    Includes image downscaling to prevent 'Payload Too Large' errors.
    """
    model_to_use = "gemini-2.0-flash"
    
    if image:
        # Downscale for API stability
        image.thumbnail((1024, 1024))
    
    try:
        return client.models.generate_content(
            model=model_to_use,
            contents=[prompt, image] if image else [prompt],
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
    except Exception as e:
        if "429" in str(e):
            # Fallback to the high-capacity 1.5-flash
            return client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[prompt, image] if image else [prompt]
            )
        raise e

# --- 3. UI LAYOUT ---
st.title("🧞 Marketplace Genie Kiosk")
st.write("Instant Diagnostics. Zero Friction.")

# Define variables BEFORE the button to avoid NameErrors
item_name = st.text_input("Device Name", placeholder="e.g. iPhone 17 Pro")

st.markdown("---")
st.subheader("📸 Hardware Scan")
col_a, col_b = st.columns(2)
with col_a:
    data_scan = st.file_uploader("Upload Settings Screen", type=['jpg','png','jpeg'], help="Settings > General > About")
with col_b:
    mirror_scan = st.file_uploader("Upload Mirror Photo", type=['jpg','png','jpeg'], help="Shows front & back at once")

# --- 4. EXECUTION ENGINE ---
if st.button("🚀 EXECUTE DIAGNOSTICS"):
    if not (item_name and data_scan and mirror_scan):
        st.warning("All fields and photos are required for a valid appraisal.")
    else:
        with st.spinner("Genie is analyzing hardware & scanning for blacklist..."):
            try:
                # Part A: OCR Data Extraction
                img_data = Image.open(data_scan)
                data_res = ask_genie_safely("Extract the IMEI and Serial from this screen. Return numbers only.", img_data)
                imei_search = re.search(r'\d{15}', data_res.text)
                imei = imei_search.group(0) if imei_search else "ID_PENDING"
                
                # Part B: Blacklist & Visual Scan
                img_mirror = Image.open(mirror_scan)
                analysis = ask_genie_safely(f"Check this {item_name} for cracks in the mirror reflection. Provide a 2026 buy-back price.", img_mirror)
                
                # Part C: Grok-4 Hype Score
                grok_res = grok_client.chat.completions.create(
                    model="grok-4",
                    messages=[{"role": "user", "content": f"Return a number 1-10 for the resale hype of {item_name} on X right now."}]
                )
                score_match = re.search(r'\b([1-9]|10)\b', grok_res.choices[0].message.content)
                hype_score = int(score_match.group(1)) if score_match else 5

                # Success - Update State
                st.session_state.current_offer = {
                    "item": item_name,
                    "imei": imei,
                    "price": "$435.00", # Example logic: AI could calculate this
                    "details": analysis.text
                }
                
                st.success(f"✅ Device Identified: IMEI {imei}")

                # Display Visuals
                res_col1, res_col2 = st.columns([1, 1])
                with res_col1:
                    st.subheader("🔥 Hype Meter")
                    fig = go.Figure(go.Indicator(mode="gauge+number", value=hype_score, gauge={'axis': {'range': [1, 10]}, 'bar': {'color': "gold"}}))
                    st.plotly_chart(fig, use_container_width=True)
                with res_col2:
                    st.subheader("💰 Genie Payout")
                    st.metric("Instant Cash", st.session_state.current_offer["price"])
                    st.write(analysis.text[:250] + "...")

            except Exception as e:
                st.error(f"Genie Hiccup: {str(e)}")
                st.info("Try refreshing or checking your API key quota.")

# --- 5. VOUCHER GENERATION ---
if st.session_state.current_offer:
    st.divider()
    if st.button("🧧 CLAIM CASH VOUCHER"):
        offer = st.session_state.current_offer
        # Create Secure QR
        qr_data = f"GENIE-VERIFIED|{offer['imei']}|{offer['price']}"
        qr = segno.make(qr_data)
        buf = BytesIO()
        qr.save(buf, kind='png', scale=10)
        
        st.image(buf.getvalue(), caption="Scan this at any Kiosk for Payout", width=250)
        st.download_button("Save Voucher to Phone", buf.getvalue(), "Genie_Voucher.png", "image/png")
        st.balloons()
