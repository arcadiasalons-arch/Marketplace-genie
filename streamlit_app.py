import streamlit as st
from google import genai
from groq import Groq # You will need to add 'groq' to requirements.txt
from PIL import Image
import datetime
import base64
import io

st.set_page_config(page_title="Marketplace Genie Pro", page_icon="🧞")
st.title("🧞 Marketplace Genie Pro")

# 1. Setup All API Clients
def get_clients():
    clients = {}
    if "GOOGLE_API_KEY" in st.secrets:
        clients['google'] = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    if "GROQ_API_KEY" in st.secrets:
        clients['groq'] = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return clients

clients = get_clients()

# 2. Category & Inputs (Keeping your smart multi-box setup)
category = st.selectbox("What are you selling?", ["Select Category", "Phones", "Furniture", "Other"])
details = {}
if category == "Phones":
    col1, col2 = st.columns(2)
    with col1:
        details['model'] = st.text_input("Exact Model", placeholder="e.g. iPhone 17 Pro Max")
        details['storage'] = st.selectbox("Storage", ["128GB", "256GB", "512GB", "1TB"])
    with col2:
        details['condition'] = st.select_slider("Condition", options=["Broken", "Poor", "Fair", "Good", "Mint"])
elif category == "Furniture":
    details['type'] = st.text_input("Item Type", placeholder="e.g. Sectional Sofa")
    details['condition'] = st.select_slider("Condition", options=["Used", "Like New"])

img_file = st.file_uploader("Upload Photo", type=['jpg', 'png', 'jpeg'])

# 3. The Waterfall Function
def run_appraisal(prompt, img):
    # --- STEP 1: TRY GOOGLE ---
    if 'google' in clients:
        try:
            response = clients['google'].models.generate_content(
                model="gemini-2.5-flash-lite", 
                contents=[prompt, img]
            )
            return response.text, "Google Gemini"
        except Exception as e:
            st.warning(f"Google is busy... trying Backup Brain (Groq).")

    # --- STEP 2: TRY GROQ (Backup) ---
    if 'groq' in clients:
        try:
            # Convert image for Groq
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            response = clients['groq'].chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                    ]
                }]
            )
            return response.choices[0].message.content, "Groq Llama"
        except Exception as e:
            st.error(f"Backup Brain failed too: {e}")
    
    return None, None

# 4. Execute
if st.button("Generate Appraisal ✨"):
    if img_file and category != "Select Category":
        with st.spinner("Genie is searching all available 2026 data..."):
            img = Image.open(img_file)
            today = datetime.date.today().strftime("%B %d, %2026")
            prompt = f"DATE: {today}. Appraise {category}: {details}. USE USED MARKET 2026 PRICES ONLY."
            
            result, provider = run_appraisal(prompt, img)
            if result:
                st.success(f"Appraisal generated via {provider}")
                st.markdown("---")
                st.info(result)
