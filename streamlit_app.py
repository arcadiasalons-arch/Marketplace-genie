import streamlit as st
from google import genai
from groq import Groq
import datetime
import base64
import io
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Marketplace Genie Pro", page_icon="🧞", layout="centered")
st.title("🧞 Marketplace Genie Pro")
st.markdown("---")

# 2. Setup All API Clients
def get_clients():
    clients = {}
    if "GOOGLE_API_KEY" in st.secrets:
        clients['google'] = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    if "GROQ_API_KEY" in st.secrets:
        clients['groq'] = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return clients

clients = get_clients()

# 3. Smart Category Selection & Inputs
category = st.selectbox("What are you selling?", ["Select Category", "Phones", "Furniture", "Other"])
details = {}

if category == "Phones":
    col1, col2 = st.columns(2)
    with col1:
        details['model'] = st.text_input("Exact Model", placeholder="e.g. iPhone 17 Pro Max")
        details['storage'] = st.selectbox("Storage", ["128GB", "256GB", "512GB", "1TB"])
    with col2:
        details['carrier'] = st.selectbox("Carrier", ["Unlocked", "AT&T", "Verizon", "T-Mobile"])
        details['condition'] = st.select_slider("Condition", options=["Broken", "Poor", "Fair", "Good", "Mint"])
elif category == "Furniture":
    details['type'] = st.text_input("Item Type", placeholder="e.g. Leather Sofa")
    details['condition'] = st.select_slider("Condition", options=["Damaged", "Used", "Like New"])

img_file = st.file_uploader("Upload a clear photo", type=['jpg', 'png', 'jpeg'])

# 4. The Triple Waterfall Logic
def run_appraisal(prompt, img):
    # --- LEVEL 1: GOOGLE GEMINI (2.5 Flash-Lite) ---
    if 'google' in clients:
        try:
            response = clients['google'].models.generate_content(
                model="gemini-2.5-flash-lite", 
                contents=[prompt, img]
            )
            return response.text, "Google Gemini 2.5"
        except Exception:
            st.warning("🧞 Google is busy... trying Backup Brain 1.")

    # --- LEVEL 2: GROQ LLAMA 4 SCOUT (Fastest 2026 Vision) ---
    if 'groq' in clients:
        try:
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            response = clients['groq'].chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                    ]
                }]
            )
            return response.choices[0].message.content, "Groq Llama 4"
        except Exception as e:
            st.error(f"Genie is fully exhausted! Error: {e}")
    
    return None, None

# 5. The "Magic" Trigger
if st.button("Generate Appraisal ✨"):
    if img_file and category != "Select Category":
        with st.spinner("Analyzing market data across 2026 marketplaces..."):
            img = Image.open(img_file)
            today = datetime.date.today().strftime("%B %d, 2026")
            info_text = ", ".join([f"{k}: {v}" for k, v in details.items()])
            
            final_prompt = f"""TODAY'S DATE: {today}. 
            ACT AS: Professional Marketplace Appraiser.
            ITEM: {category} ({info_text}).
            
            TASK: Use realistic 2026 used-market resale values. Do NOT suggest retail prices.
            REPORT:
            1. **Valuation**: 'Quick Sale' and 'Fair Market' prices.
            2. **Market Likelihood**: Score 1-10 on demand.
            3. **Time to Sell**: Days/Weeks to find a buyer.
            4. **Pro Listing**: Catchy title and SEO description."""
            
            result, provider = run_appraisal(final_prompt, img)
            if result:
                st.success(f"Appraisal Generated via {provider}")
                st.markdown("---")
                st.info(result)
    else:
        st.warning("Please select a category and upload a photo first!")
