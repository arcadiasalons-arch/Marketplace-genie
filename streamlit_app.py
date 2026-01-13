import streamlit as st
from google import genai
from groq import Groq
import datetime
import base64
import io
from PIL import Image

# 1. Language Configuration
LANG_MAP = {
    "English 🇺🇸": {
        "title": "My Genie, Price to Sell!",
        "lang_ask": "Choose your language:",
        "cat_label": "What are you selling?",
        "model_label": "Exact Model Name",
        "storage_label": "Storage Capacity",
        "cond_label": "Condition",
        "upload_label": "Upload Item Photo",
        "btn_text": "Get My Price! 💰",
        "loading": "Genie is analyzing the 2026 market...",
        "success_msg": "Appraisal Ready via",
        "prompt_intro": "Act as a professional marketplace appraiser in January 2026."
    },
    "Español 🇲🇽": {
        "title": "¡Mi Genio, Precio de Venta!",
        "lang_ask": "Elige tu idioma:",
        "cat_label": "¿Qué estás vendiendo?",
        "model_label": "Nombre Exacto del Modelo",
        "storage_label": "Capacidad de Almacenamiento",
        "cond_label": "Estado del Artículo",
        "upload_label": "Subir Foto del Artículo",
        "btn_text": "¡Obtener Mi Precio! 💰",
        "loading": "El Genio está analizando el mercado 2026...",
        "success_msg": "Tasación Lista vía",
        "prompt_intro": "Actúa como un tasador profesional del mercado en enero de 2026."
    }
}

# 2. IMMEDIATE Language Selection (Top of Page)
# Using radio buttons makes it visible without even clicking a dropdown
selected_lang_name = st.radio(
    "🌐 Language / Idioma", 
    list(LANG_MAP.keys()), 
    horizontal=True
)
t = LANG_MAP[selected_lang_name]

# 3. Branding
st.title(t["title"])
st.markdown("---")

# 4. Client Setup
def get_clients():
    clients = {}
    if "GOOGLE_API_KEY" in st.secrets:
        clients['google'] = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    if "GROQ_API_KEY" in st.secrets:
        clients['groq'] = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return clients

clients = get_clients()

# 5. Dynamic Form
category = st.selectbox(t["cat_label"], ["Select", "Phones", "Furniture", "Other"])
details = {}

if category == "Phones":
    col1, col2 = st.columns(2)
    with col1:
        details['model'] = st.text_input(t["model_label"], placeholder="iPhone 17 Pro Max")
        details['storage'] = st.selectbox(t["storage_label"], ["128GB", "256GB", "512GB", "1TB"])
    with col2:
        details['condition'] = st.select_slider(t["cond_label"], options=["Broken", "Poor", "Fair", "Good", "Mint"])

img_file = st.file_uploader(t["upload_label"], type=['jpg', 'png', 'jpeg'])

# 6. Waterfall Logic
def run_appraisal(prompt, img):
    if 'google' in clients:
        try:
            response = clients['google'].models.generate_content(
                model="gemini-2.5-flash-lite", 
                contents=[prompt, img]
            )
            return response.text, "Google Gemini"
        except Exception:
            st.warning("⚠️ Primary brain busy... switching to backup.")

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
            return None, None
    return None, None

# 7. Action
if st.button(t["btn_text"]):
    if img_file and category != "Select":
        with st.spinner(t["loading"]):
            img = Image.open(img_file)
            today = datetime.date.today().strftime("%B %d, %2026")
            
            final_prompt = f"""
            {t['prompt_intro']} 
            DATE: {today}. 
            LANGUAGE: Respond in {selected_lang_name}.
            ITEM: {category} - {details}.
            GOAL: Give a 2026 USED market price. 
            """
            
            result, provider = run_appraisal(final_prompt, img)
            if result:
                st.success(f"✅ {t['success_msg']} {provider}")
                st.info(result)
