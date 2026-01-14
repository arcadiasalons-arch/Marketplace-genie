import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
from openai import OpenAI
import datetime
import io
import base64
from PIL import Image

# 1. Branding & Persistent History
st.set_page_config(page_title="Genius App: Multi-Brain", layout="wide")
st.title("🧞 The Multi-Brain Genius (v3.13 Stable)")

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Date", "Item", "Condition", "Market_Value"])

# 2. Sequential Genius Interview
if "step" not in st.session_state: st.session_state.step = 1
def next_step(): st.session_state.step += 1

if st.session_state.step == 1:
    st.session_state.item = st.text_input("What are we appraising today?")
    if st.session_state.item: st.button("Next ➡️", on_click=next_step)

elif st.session_state.step == 2:
    st.session_state.cond = st.select_slider("Condition", ["Poor", "Fair", "Good", "Mint"])
    st.button("Next ➡️", on_click=next_step)

elif st.session_state.step >= 3:
    imgs = st.file_uploader("Upload Item Photo", type=['jpg', 'png', 'jpeg'])
    
    if imgs:
        if st.button("🚀 Run Multi-Brain Analysis"):
            with st.spinner("Genius & Grok are calculating..."):
                try:
                    # --- BRAIN 1: GEMINI (Market Data) ---
                    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
                    gem_res = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=[f"Price {st.session_state.item} in {st.session_state.cond} condition for Jan 2026", Image.open(imgs)],
                        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
                    )
                    st.session_state.valuation = gem_res.text
                    
                    # --- BRAIN 2: GROK (Sentiment) ---
                    grok = OpenAI(api_key=st.secrets["XAI_API_KEY"], base_url="https://api.x.ai/v1")
                    grok_res = grok.chat.completions.create(
                        model="grok-3",
                        messages=[{"role": "user", "content": f"Is {st.session_state.item} a good buy in 2026?"}]
                    )
                    st.session_state.sentiment = grok_res.choices[0].message.content
                    
                    # Update History
                    new_row = {"Date": datetime.date.today(), "Item": st.session_state.item, "Condition": st.session_state.cond, "Market_Value": "Analyzed"}
                    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)

                except Exception as e:
                    st.error(f"Brain Error: {e}")

        # 3. Display Results
        if "valuation" in st.session_state:
            st.success("Appraisal Complete!")
            col1, col2 = st.columns(2)
            with col1: st.info(f"**Market View (Gemini):**\n\n{st.session_state.valuation}")
            with col2: st.warning(f"**Hype View (Grok):**\n\n{st.session_state.sentiment}")

        # 4. PANDA ANALYTICS (Custom implementation for Python 3.13)
        if not st.session_state.history.empty:
            st.write("---")
            st.subheader("🐼 Panda History Analytics")
            p_query = st.text_input("Ask Panda about your history:", "Summarize my appraisals")
            
            if p_query:
                # We send the dataframe as text to Gemini to 'act' as Panda
                history_text = st.session_state.history.to_string()
                client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
                panda_res = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=f"You are Panda, a data analyst. Based on this history:\n{history_text}\n\nAnswer: {p_query}"
                )
                st.write(panda_res.text)
