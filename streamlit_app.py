import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Marketplace Genie", page_icon="🧞")
st.title("🧞 Marketplace Genie")

# Setup AI
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Setup Error: {e}")
else:
    st.error("Missing Key! Go to Settings > Secrets and add GOOGLE_API_KEY")

# Inputs
name = st.text_input("What are you selling?", placeholder="e.g. Vintage Camera")
img_file = st.file_uploader("Upload a photo", type=['jpg', 'png', 'jpeg'])

if st.button("Generate Listing ✨"):
    if name and img_file:
        with st.spinner("Genie is analyzing your item..."):
            try:
                img = Image.open(img_file)
                # This updated line handles the AI request more safely
                response = model.generate_content([
                    f"Create a professional marketplace listing for: {name}. Include a title, price suggestion, and description.", 
                    img
                ])
                st.success("Listing Created!")
                st.markdown("---")
                st.write(response.text)
            except Exception as e:
                st.error("The Genie hit a snag. Please check if your API Key is active in Google AI Studio.")
                st.info(f"Technical error: {e}")
    else:
        st.warning("Please provide both a name and a photo!")
