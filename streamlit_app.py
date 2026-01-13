import streamlit as st
from google import genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="Marketplace Genie", page_icon="🧞", layout="centered")
st.title("🧞 Marketplace Genie")
st.markdown("### *2026 Professional Used-Market Appraisal*")

# 2. AI Client Setup
if "GOOGLE_API_KEY" in st.secrets:
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"Setup Error: {e}")
else:
    st.error("Missing Key! Go to Settings > Secrets and add GOOGLE_API_KEY")

# 3. User Inputs
name = st.text_input("What are you selling?", placeholder="e.g. iPhone 12 Pro Max")
img_file = st.file_uploader("Upload a photo", type=['jpg', 'png', 'jpeg'])

# 4. The Appraisal Magic
if st.button("Analyze & Value My Item ✨"):
    if name and img_file:
        with st.spinner("Genie is researching 2026 used market trends..."):
            try:
                img = Image.open(img_file)
                
                # REVISED PROMPT: Ruthless Realistic Pricing
                prompt = f"""Act as a realistic, ruthless marketplace appraiser for a USED {name}. 
                IMPORTANT: Do NOT suggest original retail prices or 'New' prices. 
                Focus ONLY on current 2026 resale values for pre-owned items in the condition seen in the photo.
                
                Analyze the image and provide:
                1. **Realistic Used Valuation**: Give a 'Quick Sale' price (sells today) and a 'Fair Market' price (sells in 1 week). 
                2. **Depreciation Check**: Briefly explain why it is priced this way (e.g. 'This is a 5-year-old model with visible screen wear').
                3. **Likelihood of Sale**: A score from 1-10 on how high demand is for this specific model in 2026.
                4. **Estimated Time to Sell**: How many days it will stay on the market at your suggested price.
                5. **Pro Listing Description**: Write a catchy title and a short, honest description mentioning its used status."""

                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=[prompt, img]
                )
                
                st.success("Appraisal Generated!")
                st.markdown("---")
                # This makes the output look like a clean report
                st.info(response.text)
                
            except Exception as e:
                st.error(f"The Genie hit a snag: {e}")
    else:
        st.warning("Please provide both a name and a photo!")
