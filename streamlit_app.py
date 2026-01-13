import streamlit as st
from google import genai
from PIL import Image

# 1. App Configuration
st.set_page_config(page_title="Marketplace Genie", page_icon="🧞")
st.title("🧞 Marketplace Genie")
st.subheader("2026 Professional Appraisal & Listing")

# 2. Connect to the AI (Using 2026 Client)
if "GOOGLE_API_KEY" in st.secrets:
    try:
        # Standard 2026 setup
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"Setup Error: {e}")
else:
    st.error("Missing Key! Go to Settings > Secrets and add GOOGLE_API_KEY")

# 3. User Inputs
name = st.text_input("What are you selling?", placeholder="e.g. iPhone 12 Pro Max")
img_file = st.file_uploader("Upload a photo", type=['jpg', 'png', 'jpeg'])

# 4. The Appraisal Magic
if st.button("Generate Appraisal ✨"):
    if name and img_file:
        with st.spinner("Genie is analyzing 2026 market trends..."):
            try:
                img = Image.open(img_file)
                
                # Your Custom 2026 Appraisal Prompt
                prompt = f"""Act as a professional marketplace appraiser for: {name}. 
                Use current 2026 market trends for your estimates.
                Analyze the provided image and provide a report with:
                1. **Market Valuation**: A 'Quick Sale' price and a 'Fair Market' price for today's market.
                2. **Likelihood of Sale**: A score from 1-10 on how high demand is right now.
                3. **Estimated Time to Sell**: How many days/weeks to find a buyer at these prices.
                4. **Professional Listing**: A catchy title and SEO-optimized description.
                5. **Condition Report**: Any visible wear or selling points you see in the photo."""

                # Calling the stable 2.5 Flash model
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=[prompt, img]
                )
                
                st.success("Appraisal Complete!")
                st.markdown("---")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"The Genie hit a snag: {e}")
    else:
        st.warning("Please provide both a name and a photo!")
