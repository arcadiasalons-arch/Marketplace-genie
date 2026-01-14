import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
from openai import OpenAI
from PIL import Image

st.set_page_config(page_title="The Genius App", layout="wide")
st.title("🧞 The Genius App (2026 Stable)")

# Initialize history without the PandasAI library
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Item", "Condition", "Market_Status"])

# Setup the Client with the STABLE API version (v1)
client = genai.Client(
    api_key=st.secrets["GOOGLE_API_KEY"],
    http_options={'api_version': 'v1'} # Forces production version to avoid 404s
)

item = st.text_input("What are we appraising?")
imgs = st.file_uploader("Upload Photo", type=['jpg', 'png', 'jpeg'])

if st.button("🚀 Run Analysis") and item and imgs:
    with st.spinner("Genius is consulting..."):
        try:
            # Using 1.5-flash with explicit v1 support
            # Use 'gemini-1.5-flash' for high stability in v1
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[f"Appraise this {item} for Jan 2026.", Image.open(imgs)],
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            st.success("Appraisal Complete!")
            st.write(response.text)
            
            # Save to history
            new_row = pd.DataFrame([{"Item": item, "Condition": "Good", "Market_Status": "Analyzed"}])
            st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)

        except Exception as e:
            st.error(f"Genie Error: {e}")

# Stable 'Panda' Analytics (Direct AI Analysis)
if not st.session_state.history.empty:
    st.write("---")
    st.subheader("🐼 Panda History Intelligence")
    if st.button("Analyze My History"):
        history_summary = st.session_state.history.to_string()
        # Use the same client to analyze the text data
        analysis = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Analyze this sales history and summarize: {history_summary}"
        )
        st.info(analysis.text)
