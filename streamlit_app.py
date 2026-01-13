import streamlit as st
from google import genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Marketplace Genie", page_icon="🧞")
st.title("🧞 Marketplace Genie")

# 2. Setup AI with 2026 Toolkit
if "GOOGLE_API_KEY" in st.secrets:
    try:
        # Create the client using the new 2026 SDK
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"Setup Error: {e}")
else:
    st.error("Missing Key! Go to Settings > Secrets and add GOOGLE_API_KEY")

# 3. User Inputs
name = st.text_input("What are you selling?", placeholder="e.g. iPhone 12 Pro Max")
img_file = st.file_uploader("Upload a photo", type=['jpg', 'png', 'jpeg'])

# 4. The Magic
if st.button("Generate Listing ✨"):
    if name and img_file:
        with st.spinner("Genie is analyzing your item..."):
            try:
                img = Image.open(img_file)
                # Using the stable 2026 Flash model
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=[f"Create a professional marketplace listing for: {name}", img]
                )
                st.success("Success!")
                st.markdown("---")
                st.write(response.text)
            except Exception as e:
                st.error(f"The Genie hit a snag: {e}")
    else:
        st.warning("Please provide both a name and a photo!")
