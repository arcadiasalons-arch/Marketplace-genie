import streamlit as st
from google import genai
from google.genai import types
from openai import OpenAI
import pandas as pd
from PIL import Image
import datetime

# --- BRANDING & HISTORY ---
st.set_page_config(page_title="Genius App: Multi-Brain", layout="wide")
st.title("🧞 The Multi-Brain Genius (Stable Build)")

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Date", "Item", "Value", "Hype"])

# --- API CLIENTS ---
# Using the standard v1 production endpoints for stability
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
grok = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")

# --- USER INPUT ---
item = st.text_input("What are we appraising today?")
imgs = st.file_uploader("Upload Item Photo", type=['jpg', 'png', 'jpeg'])

if st.button("🚀 Run Multi-Brain Analysis") and item and imgs:
    with st.spinner("Genius & Grok are calculating..."):
        try:
            # BRAIN 1: GEMINI (Market Data)
            # Using 1.5-flash for maximum free-tier reliability
            gem_res = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[f"Provide a 2026 market price for {item}.", Image.open(imgs)],
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            
            # BRAIN 2: GROK (Social Hype)
            grok_res = grok.chat.completions.create(
                model="grok-3",
                messages=[{"role": "user", "content": f"Check X/Twitter: Is {item} a good buy in 2026?"}]
            )
            sentiment = grok_res.choices[0].message.content

            # --- DISPLAY RESULTS ---
            st.success("Appraisal Complete!")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Market View (Gemini)")
                st.write(gem_res.text)
            with col2:
                st.subheader("🐦 Hype View (Grok)")
                st.write(sentiment)

            # Update History Table
            new_row = pd.DataFrame([{
                "Date": datetime.date.today(),
                "Item": item,
                "Value": "Analyzed",
                "Hype": "Verified"
            }])
            st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)

        except Exception as e:
            st.error(f"Brain Sync Error: {e}")

# --- PANDA ANALYTICS (Simulated) ---
if not st.session_state.history.empty:
    st.write("---")
    st.subheader("🐼 Panda History Intelligence")
    st.dataframe(st.session_state.history)
    if st.button("Summarize My Trends"):
        # We use Gemini to act as Panda and summarize the history
        history_text = st.session_state.history.to_string()
        panda_res = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Analyze this history and summarize the trends: {history_text}"
        )
        st.info(panda_res.text)
