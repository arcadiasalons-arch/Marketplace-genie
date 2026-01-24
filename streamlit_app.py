import streamlit as st
from google import genai
from google.genai import types
from openai import OpenAI
import pandas as pd
from PIL import Image
import re

# --- CONFIG ---
st.set_page_config(page_title="Genie Kiosk", layout="centered", page_icon="🧞")
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
grok = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")

st.title("🧞 Marketplace Genie Kiosk")
st.write("Instant Diagnostics. Zero Typing.")

# --- STEP 1: THE DATA SCAN ---
st.info("📱 **Step 1:** Go to **Settings > General > About** and take a screenshot or photo of your IMEI/Serial.")
data_file = st.file_uploader("Upload Settings Photo", type=['jpg', 'png', 'jpeg'], key="data")

if data_file:
    with st.spinner("Extracting hardware ID and battery health..."):
        try:
            # Gemini reads the screen like a human expert
            img = Image.open(data_file)
            analysis = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=["Extract IMEI, Serial Number, and Model Name from this image. Return only the values.", img]
            )
            extracted_text = analysis.text
            
            # Use Regex to find a 15-digit IMEI in the AI's response
            imei_match = re.search(r'\d{15}', extracted_text)
            imei = imei_match.group(0) if imei_match else "Unknown"
            
            st.success(f"✅ Device Identified: {extracted_text}")
            
            # --- STEP 2: THE BLACKLIST CHECK (The 'Ingenious' Part) ---
            # In a real app, you'd call the CheckMEND API here. 
            # For now, we simulate the 'Genie Security' check.
            if imei != "Unknown":
                st.warning(f"🛡️ Checking IMEI: {imei} against global databases...")
                # Simulated result
                st.write("🔍 **Result:** Device is CLEAN and eligible for instant payout.")

            # --- STEP 3: THE MIRROR SCAN (Visuals) ---
            st.markdown("---")
            st.info("📷 **Step 2:** Hold your phone up to a mirror. Take one photo of the reflection.")
            mirror_file = st.file_uploader("Upload Mirror Shot", type=['jpg', 'png'], key="mirror")
            
            if mirror_file:
                m_img = Image.open(mirror_file)
                # Visual damage detection
                vis_res = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=["Inspect the reflection for screen cracks and the back for scratches. Give a grade (A-F).", m_img]
                )
                
                # --- FINAL OFFER ---
                st.subheader("🧞 Genie's Final Offer")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Instant Cash", "$215", "+$25 Hype Bonus")
                    st.caption("Available today at any partner kiosk.")
                with col2:
                    st.metric("Consignment", "$280", "Est. 7 Days")
                    st.caption("We sell it for you via Grok-Hype.")
                
                st.write(f"**Visual Grade:** {vis_res.text}")

        except Exception as e:
            st.error(f"Kiosk Error: {e}")
