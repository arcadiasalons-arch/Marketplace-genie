import streamlit as st
import json
import base64
import requests
from PIL import Image
import io

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="Marketplace Genie Pro", page_icon="🧞", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; }
    .ad-card { padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; background-color: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .price-container { display: flex; gap: 10px; margin: 20px 0; }
    .price-box { flex: 1; padding: 20px; border-radius: 20px; text-align: center; background: #f8fafc; border: 2px solid #e2e8f0; }
    .highlight-price { border-color: #6366f1; background: #f5f3ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API SETUP (DIRECT WEB CALL) ---
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

def call_genie_direct(prompt, image_b64=None):
    # Using the absolute most stable production endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Building the payload manually to avoid SDK bugs
    parts = [{"text": prompt}]
    if image_b64:
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image_b64
            }
        })
        
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Extract the text content from the deep JSON response
        text_content = result['candidates'][0]['content']['parts'][0]['text']
        return json.loads(text_content)
    except Exception as e:
        # If v1beta fails, try the stable v1 endpoint as a last resort
        try:
            stable_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            response = requests.post(stable_url, headers=headers, json=payload)
            response.raise_for_status()
            text_content = response.json()['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text_content)
        except:
            st.error(f"Genie Connection Error: {e}")
            return None

# --- 3. STATE MANAGEMENT ---
if "step" not in st.session_state: st.session_state.step = "search"
if "selected_item" not in st.session_state: st.session_state.selected_item = None
if "item_specs" not in st.session_state: st.session_state.item_specs = {}
if "user_specs" not in st.session_state: st.session_state.user_specs = {}
if "condition" not in st.session_state: st.session_state.condition = None
if "suggestions" not in st.session_state: st.session_state.suggestions = []

def reset():
    for key in ["step", "selected_item", "item_specs", "user_specs", "condition", "result", "suggestions"]:
        if key in st.session_state: del st.session_state[key]
    st.session_state.step = "search"
    st.rerun()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🧞 Genie Pro")
    st.markdown("---")
    st.markdown("### 📢 Featured Partner")
    st.markdown('<div class="ad-card"><b>📦 PakMail Supplies</b><br><small>Boxes and bubble wrap delivered.</small><br><br><a href="#">Get 20% Off</a></div>', unsafe_allow_html=True)
    if st.button("🔄 Start New Appraisal"):
        reset()

# --- 5. MAIN APP FLOW ---

# STEP 1: SEARCH
if st.session_state.step == "search":
    st.title("What are you selling?")
    query = st.text_input("Item Name", placeholder="Ex: iPhone 15", label_visibility="collapsed")
    
    if st.button("Find Item 🔍") and query:
        with st.spinner("Genie is searching..."):
            prompt = f"User is selling '{query}'. Suggest 5 specific models in a JSON string array."
            st.session_state.suggestions = call_genie_direct(prompt)
            
    if st.session_state.suggestions:
        st.subheader("Select your item:")
        for item in st.session_state.suggestions:
            if st.button(item, key=item):
                st.session_state.selected_item = item
                st.session_state.step = "specs"
                st.rerun()

# STEP 2: SPECS
elif st.session_state.step == "specs":
    st.title(f"Details for {st.session_state.selected_item}")
    if not st.session_state.item_specs:
        with st.spinner("Generating options..."):
            prompt = f"For '{st.session_state.selected_item}', return 3 variations (Size, Color, etc) in a JSON object with options."
            st.session_state.item_specs = call_genie_direct(prompt) or {}
            st.rerun()

    for name, opts in st.session_state.item_specs.items():
        st.session_state.user_specs[name] = st.selectbox(f"Select {name}", opts)
    
    if st.button("Continue →"):
        st.session_state.step = "condition"
        st.rerun()

# STEP 3: CONDITION
elif st.session_state.step == "condition":
    st.title("Condition")
    c = st.radio("Rate it:", ["New Unopened", "Opened / Like New", "Used / Well Loved"], index=None)
    if c:
        st.session_state.condition = c
        if st.button("Take Photo →"):
            st.session_state.step = "photo"
            st.rerun()

# STEP 4: PHOTO & FINAL
elif st.session_state.step == "photo":
    st.title("Capture Item")
    img_file = st.camera_input("Photo")
    if img_file:
        if st.button("Generate Listing ✨"):
            with st.spinner("Analyzing..."):
                b64 = base64.b64encode(img_file.getvalue()).decode()
                prompt = f"Appraise: {st.session_state.selected_item}. Specs: {json.dumps(st.session_state.user_specs)}. Condition: {st.session_state.condition}. Return JSON with verified:bool, note, title, description, quick, max prices."
                res = call_genie_direct(prompt, image_b64=b64)
                if res:
                    st.session_state.result = res
                    st.session_state.step = "result"
                    st.rerun()

# STEP 5: RESULT
elif st.session_state.step == "result":
    res = st.session_state.result
    st.title("Your Appraisal")
    st.success(f"Verified: {res.get('note', 'Match found')}")
    st.markdown(f'<div class="price-container"><div class="price-box">QUICK: {res["quick"]}</div><div class="price-box highlight-price">MAX: {res["max"]}</div></div>', unsafe_allow_html=True)
    st.text_input("Title", res['title'])
    st.text_area("Description", res['description'], height=200)
    if st.button("Done"): reset()

