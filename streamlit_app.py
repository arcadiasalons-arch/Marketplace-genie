import streamlit as st
from google import genai
import json
import base64
from PIL import Image
import io

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="Marketplace Genie Pro", page_icon="🧞", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { border-color: #6366f1; color: #6366f1; }
    .ad-card { padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; background-color: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .price-container { display: flex; gap: 10px; margin: 20px 0; }
    .price-box { flex: 1; padding: 20px; border-radius: 20px; text-align: center; background: #f8fafc; border: 2px solid #e2e8f0; }
    .highlight-price { border-color: #6366f1; background: #f5f3ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY", "")
client = genai.Client(api_key=api_key)

# --- 3. STATE MANAGEMENT ---
if "step" not in st.session_state:
    st.session_state.step = "search"
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None
if "item_specs" not in st.session_state:
    st.session_state.item_specs = {}
if "user_specs" not in st.session_state:
    st.session_state.user_specs = {}
if "condition" not in st.session_state:
    st.session_state.condition = None
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

def reset():
    for key in ["step", "selected_item", "item_specs", "user_specs", "condition", "result", "suggestions"]:
        if key in st.session_state: del st.session_state[key]
    st.session_state.step = "search"
    st.rerun()

# --- 4. AI LOGIC (WITH CACHING TO SAVE QUOTA) ---
@st.cache_data(show_spinner=False)
def get_cached_suggestions(query):
    # We use 1.5-flash here because the free tier is much more forgiving
    model_id = "gemini-1.5-flash"
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[f"User is selling '{query}'. Suggest 5 specific models/item names in a JSON string array. Examples: ['LG C3 OLED TV', 'Samsung QLED 4K']"],
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Genie Error: {e}")
        return []

def get_ai_json(prompt, image_data=None):
    # Using 1.5-flash for broader free-tier compatibility
    model_id = "gemini-1.5-flash" 
    try:
        contents = [prompt]
        if image_data:
            contents.append({"inline_data": {"mime_type": "image/jpeg", "data": image_data}})
            
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Genie Error: {e}")
        return None

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🧞 Genie Pro")
    st.markdown("---")
    st.markdown("### 📢 Featured Partner")
    st.markdown("""
    <div class="ad-card">
        <p style="color: #6366f1; font-weight: bold; margin-bottom: 5px;">📦 PakMail Supplies</p>
        <small>Get professional-grade bubble wrap and boxes delivered to your door.</small>
        <br><br>
        <a href="#" style="text-decoration: none; color: white; background: #6366f1; padding: 5px 10px; border-radius: 5px; font-size: 12px;">Get 20% Off</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 Start New Appraisal"):
        reset()

# --- 6. MAIN APP FLOW ---

# STEP 1: SMART SEARCH
if st.session_state.step == "search":
    st.title("What are you selling?")
    st.write("Type anything from a 'TV' to a 'Half-used Perfume'.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Item Name", placeholder="Start typing...", label_visibility="collapsed")
    with col2:
        # Added a strict button to prevent accidental API calls
        search_pressed = st.button("Find Item 🔍")
    
    if search_pressed and query:
        with st.spinner("Genie is thinking..."):
            st.session_state.suggestions = get_cached_suggestions(query)
            
    if st.session_state.suggestions:
        st.subheader("Select your exact item:")
        for item in st.session_state.suggestions:
            if st.button(item, key=item):
                st.session_state.selected_item = item
                st.session_state.step = "specs"
                st.rerun()

# STEP 2: DYNAMIC SPECS
elif st.session_state.step == "specs":
    st.title(f"Details for your {st.session_state.selected_item}")
    
    if not st.session_state.item_specs:
        with st.spinner("Analyzing variations..."):
            specs = get_ai_json(f"For '{st.session_state.selected_item}', return 3 technical specs (e.g. Size, Scent, Material) with 3 options each in a JSON object.")
            st.session_state.item_specs = specs or {}
            st.rerun()

    for name, opts in st.session_state.item_specs.items():
        st.session_state.user_specs[name] = st.selectbox(f"What {name} is it?", opts)
    
    if st.button("Next: Condition →"):
        st.session_state.step = "condition"
        st.rerun()

# STEP 3: CONDITION
elif st.session_state.step == "condition":
    st.title("Item Condition")
    c = st.radio("How would you rate it?", ["New Unopened", "Opened / Like New", "Used / Well Loved"], index=None)
    if c:
        st.session_state.condition = c
        if st.button("Continue to Photo →"):
            st.session_state.step = "photo"
            st.rerun()

# STEP 4: PHOTO & FINAL ANALYSIS
elif st.session_state.step == "photo":
    st.title("Verify with Photo")
    img_file = st.camera_input("Take a photo of the item")
    
    if img_file:
        if st.button("Generate Appraisal & Description ✨"):
            with st.spinner("Finalizing marketplace data..."):
                b64_img = base64.b64encode(img_file.getvalue()).decode()
                prompt = f"""
                Appraise: {st.session_state.selected_item}
                Specs: {json.dumps(st.session_state.user_specs)}
                Condition: {st.session_state.condition}
                Verify photo matches item. Return JSON:
                {{
                    "verified": bool, "note": "str", "title": "str", 
                    "description": "str", "quick": "$XX", "max": "$XX"
                }}
                """
                res = get_ai_json(prompt, image_data=b64_img)
                if res:
                    st.session_state.result = res
                    st.session_state.step = "result"
                    st.rerun()

# STEP 5: RESULTS & ADS
elif st.session_state.step == "result":
    res = st.session_state.result
    st.title("Your Appraisal")
    
    if res.get("verified"):
        st.success(f"Verified: {res['note']}")
    else:
        st.warning(f"Note: {res['note']}")

    st.markdown(f"""
    <div class="price-container">
        <div class="price-box">
            <small>QUICK SELL</small><br>
            <b style="font-size: 24px; color: #6366f1;">{res['quick']}</b>
        </div>
        <div class="price-box highlight-price">
            <small>MARKET VALUE</small><br>
            <b style="font-size: 24px; color: #1e293b;">{res['max']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Copy & Paste Listing")
    st.text_input("Recommended Title", res['title'])
    st.text_area("Full Description", res['description'], height=200)

    # AD SPACE: RESULTS PAGE
    st.markdown("---")
    st.markdown("### 🚀 Grow Your Sale")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="ad-card"><b>Ship Instantly</b><br><small>Get pre-paid UPS labels for 15% less.</small></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="ad-card"><b>Professional Cleaning</b><br><small>Polish this item for $5 extra profit.</small></div>""", unsafe_allow_html=True)
    
    if st.button("List Another Item"):
        reset()


