import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import GoogleGemini
from openai import OpenAI
import datetime
import io
import base64
from PIL import Image

# 1. Init & Styling
st.set_page_config(page_title="Genius App: Multi-Brain", layout="wide")
st.title("🧞 The Multi-Brain Genius")

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Date", "Item", "Value"])

# 2. Sequential Genius Interview
if "step" not in st.session_state: st.session_state.step = 1
def next_step(): st.session_state.step += 1

if st.session_state.step == 1:
    st.session_state.item = st.text_input("What are we appraising?")
    if st.session_state.item: st.button("Next ➡️", on_click=next_step)

elif st.session_state.step >= 2:
    imgs = st.file_uploader("Upload 360° Photos", accept_multiple_files=True)
    
    if imgs and st.button("🚀 Consult the Multi-Brain"):
        with st.spinner("Genius, Grok, and Panda are talking..."):
            try:
                # --- GEMINI: MARKET DATA ---
                client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
                gem_res = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[f"Price {st.session_state.item} for Jan 2026", Image.open(imgs[0])],
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                )
                
                # --- GROK: SOCIAL SENTIMENT ---
                grok = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")
                grok_res = grok.chat.completions.create(
                    model="grok-3",
                    messages=[{"role": "user", "content": f"Is demand for {st.session_state.item} high on X/Twitter right now?"}]
                )
                
                # --- PANDA: DATA ANALYTICS ---
                new_row = {"Date": datetime.date.today(), "Item": st.session_state.item, "Value": 500} # Simulated val
                st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
                
                # Display
                st.success("Analysis Complete!")
                colA, colB = st.columns(2)
                with colA: st.info(f"**Gemini Market View:**\n{gem_res.text}")
                with colB: st.warning(f"**Grok Social View:**\n{grok_res.choices[0].message.content}")

                if not st.session_state.history.empty:
                    st.write("---")
                    st.subheader("🐼 Panda History Analytics")
                    panda_brain = GoogleGemini(api_key=st.secrets["GOOGLE_API_KEY"])
                    sdf = SmartDataframe(st.session_state.history, config={"llm": panda_brain})
                    st.write(sdf.chat("Summary of my appraisals?"))

            except Exception as e:
                st.error(f"Sync Error: {e}")
