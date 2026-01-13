import streamlit as st
from google import genai
from groq import Groq
import datetime
import base64
import io
from PIL import Image

# 1. Language Dictionary
LANGUAGES = {
    "English": {
        "title": "🧞 Marketplace Genie Pro",
        "select_cat": "What are you selling?",
        "model": "Exact Model",
        "storage": "Storage",
        "condition": "Condition",
        "upload": "Upload a clear photo",
        "button": "Generate Appraisal ✨",
        "spinner": "Analyzing market data...",
        "success": "Appraisal Generated via",
        "prompt_instruction": "USE REALISTIC 2026 USED RESALE PRICES ONLY."
    },
    "Español": {
        "title": "🧞 Genio del Mercado Pro",
        "select_cat": "¿Qué estás vendiendo?",
        "model": "Modelo Exacto",
        "storage": "Almacenamiento",
        "condition": "Estado",
        "upload": "Sube una foto clara",
        "button": "Generar Tasación ✨",
        "spinner": "Analizando datos del mercado...",
        "success": "Tasación generada por",
        "prompt_instruction": "USE SOLO PRECIOS DE REVENTA USADOS REALISTAS DE 2026."
    }
}

# 2. Sidebar Language Selector
with st.sidebar:
    selected_lang = st.selectbox("🌐 Language / Idioma", list(LANGUAGES.keys()))
    t = LANGUAGES[selected_lang] # 't' stands for text/translations

st.title(t["title"])
st.markdown("---")

# 3. Setup All API Clients
def get_clients():
    clients = {}
    if "GOOGLE_API_KEY" in st.secrets:
        clients['google'] = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    if "GROQ_API_KEY" in st.secrets:
        clients['groq'] = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return clients

clients = get_clients()

# 4. Inputs using the translated labels
category = st.selectbox(t["select_cat"], ["Select", "Phones", "Furniture"])
details = {}

if category == "Phones":
    col1, col2 = st.columns(2)
    with col1:
        details['model'] = st.text_input(t["model"])
        details['storage'] = st.selectbox(t["storage"], ["128GB", "256GB", "512GB"])
    with col2:
        details['condition'] = st.select_slider(t["condition"], options=["Poor", "Fair", "Good", "Mint"])

img_file = st.file_uploader(t["upload"], type=['jpg', 'png', 'jpeg'])

# 5. Logic
def run_appraisal(prompt, img):
    if 'google' in clients:
        try:
            response = clients['google'].models.generate_content(
                model="gemini-2.5-flash-lite", 
                contents=[prompt, img]
            )
            return response.text, "Google Gemini"
        except Exception:
            pass
    if 'groq' in clients:
        try:
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            response = clients['groq'].chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]}]
            )
            return response.choices[0].message.content, "Groq Llama 4"
        except Exception:
            return "Error", "None"
    return None, None

if st.button(t["button"]):
    if img_file and category != "Select":
        with st.spinner(t["spinner"]):
            img = Image.open(img_file)
            today = datetime.date.today().strftime("%B %d, %2026")
            final_prompt = f"DATE: {today}. Appraise {category}. Language: {selected_lang}. {t['prompt_instruction']}"
            result, provider = run_appraisal(final_prompt, img)
            st.success(f"{t['success']} {provider}")
            st.info(result)
