import streamlit as st
from google import genai
from PIL import Image
import datetime

st.set_page_config(page_title="Marketplace Genie Pro", page_icon="🧞")
st.title("🧞 Marketplace Genie Pro")

# 1. Setup AI
if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key in Secrets!")

# 2. Dynamic Input System
category = st.selectbox("What are you selling?", ["Select Category", "Electronics/Phones", "Furniture", "Vehicles", "Other"])

# This dictionary stores the specific details we gather
details = {}

if category == "Electronics/Phones":
    col1, col2 = st.columns(2)
    with col1:
        details['model'] = st.text_input("Exact Model", placeholder="e.g. iPhone 17 Pro Max")
        details['storage'] = st.selectbox("Storage", ["128GB", "256GB", "512GB", "1TB"])
    with col2:
        details['carrier'] = st.selectbox("Network", ["Unlocked", "AT&T", "Verizon", "T-Mobile"])
        details['condition'] = st.select_slider("Condition", options=["Broken", "Poor", "Fair", "Good", "Mint"])

elif category == "Furniture":
    details['type'] = st.text_input("Item Type", placeholder="e.g. Sectional Sofa")
    details['brand'] = st.text_input("Brand/Designer", placeholder="e.g. West Elm")
    details['condition'] = st.select_slider("Condition", options=["Damaged", "Used", "Like New"])

# 3. Photo Upload
img_file = st.file_uploader("Upload a clear photo of the item", type=['jpg', 'png', 'jpeg'])

# 4. Smart Appraisal Logic
if st.button("Generate Pro Appraisal ✨"):
    if img_file and category != "Select Category":
        with st.spinner("Genie is cross-referencing 2026 market data..."):
            try:
                img = Image.open(img_file)
                
                # We build a "Bulletproof" prompt using the data we gathered
                current_date = datetime.date.today().strftime("%B %d, %2026")
                
                info_string = ", ".join([f"{k}: {v}" for k, v in details.items()])
                
                prompt = f"""
                TODAY'S DATE: {current_date}
                ACT AS: A Senior Marketplace Data Analyst.
                ITEM DATA: {info_string}
                
                TASK: Provide a ruthless, realistic used-market appraisal. 
                - DO NOT guess or use data from 5 years ago. 
                - THIS IS THE LATEST {category}.
                - Consider the condition '{details.get('condition', 'Used')}' visible in the photo.
                
                REPORT FORMAT:
                1. **Market Value**: Suggest a 'Quick Sale' and 'Fair Market' price.
                2. **2026 Context**: Explain why this price is accurate for the current year.
                3. **Selling Strategy**: Best platform to sell on (eBay, Marketplace, etc.)
                4. **Pro Listing**: Write a title and description based ONLY on the facts provided.
                """

                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=[prompt, img]
                )
                
                st.success("Appraisal Ready!")
                st.markdown("---")
                st.info(response.text)
                
            except Exception as e:
                st.error(f"Snag: {e}")
    else:
        st.warning("Please select a category and upload a photo!")
