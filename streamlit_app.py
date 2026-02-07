# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Marketplace Genie Pro", page_icon="🧞", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; font-weight: bold; }
    .ad-box { padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; background-color: #f9f9f9; margin-bottom: 20px; }
    .price-card { padding: 20px; border-radius: 15px; text-align: center; background: white; border: 2px solid #6366f1; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE API CLIENT ---
# Ensure your GOOGLE_API_KEY is in st.secrets or set as an environment variable
api_key = st.secrets.get("GOOGLE_API_KEY", "")
client = genai.Client(api_key=api_key)

# --- SESSION STATE MANAGEMENT ---
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

def reset_app():
    for key in ["step", "selected_item", "item_specs", "user_specs", "condition"]:
        st.session_state[key] = None if key != "step" else "search"
    st.rerun()

# --- HELPER FUNCTIONS ---
def call_ai(prompt, image=None, is_json=True):
    model_id = "gemini-2.5-flash-preview-09-2025"
    config = {"response_mime_type": "application/json"} if is_json else None
    
    contents = [prompt]
    if image:
        contents.append(image)
        
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
            config=config
        )
        return json.loads(response.text) if is_json else response.text
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# --- SIDEBAR / AD SPACE 1 ---
with st.sidebar:
    st.title("🧞 Genie Pro")
    st.markdown("---")
    st.markdown("### 📢 Sponsored")
    st.info("**PakMail Solutions**\n\nNeed boxes for your sale? Get 20% off all shipping supplies today!")
    if st.button("Claim Coupon"):
        st.success("Code: GENIE20 applied!")
    st.markdown("---")
    if st.button("Start New Appraisal"):
        reset_app()

# --- MAIN APP LOGIC ---

# STEP 1: SMART SEARCH
if st.session_state.step == "search":
    st.title("What are you selling today?")
    search_query = st.text_input("Enter item name (e.g. LG TV, Chanel Perfume, Rug)", placeholder="Start typing...")
    
    if search_query:
        with st.spinner("Finding models..."):
            suggestions = call_ai(
                f"User is selling: '{search_query}'. Return a JSON array of 5 specific model suggestions."
            )
            if suggestions:
                st.subheader("Select the closest match:")
                for item in suggestions:
                    if st.button(item):
                        st.session_state.selected_item = item
                        st.session_state.step = "specs"
                        st.rerun()

# STEP 2: DYNAMIC SPECS
elif st.session_state.step == "specs":
    st.title(f"Details for {st.session_state.selected_item}")
    
    if not st.session_state.item_specs:
        with st.spinner("Analyzing item specs..."):
            specs = call_ai(
                f"For the item '{st.session_state.selected_item}', return a JSON object of 3 key variations (e.g. Size, Color, Capacity) with options for each."
            )
            st.session_state.item_specs = specs
            st.rerun()

    for spec_name, options in st.session_state.item_specs.items():
        st.session_state.user_specs[spec_name] = st.selectbox(f"Select {spec_name}", options)
    
    if st.button("Continue to Condition"):
        st.session_state.step = "condition"
        st.rerun()

# STEP 3: CONDITION
elif st.session_state.step == "condition":
    st.title("Condition")
    cond = st.radio(
        "How would you describe the item?",
        ["New Unopened", "Opened / Like New", "Used / Well Loved"],
        index=None
    )
    if cond:
        st.session_state.condition = cond
        if st.button("Snap a Photo"):
            st.session_state.step = "photo"
            st.rerun()

# STEP 4: PHOTO CAPTURE & AI ANALYSIS
elif st.session_state.step == "photo":
    st.title("Verify with Photo")
    st.write("Take one photo of the best angle. Our AI will verify the item and condition.")
    
    img_file = st.camera_input("Capture Item")
    
    if img_file:
        if st.button("Generate Final Listing ✨"):
            with st.spinner("Genie is working..."):
                img_bytes = img_file.getvalue()
                # Create a Part object for Gemini
                image_part = {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(img_bytes).decode("utf-8")}}
                
                spec_str = json.dumps(st.session_state.user_specs)
                prompt = f"""
                Appraise this item. 
                Claimed Item: {st.session_state.selected_item}
                Specs: {spec_str}
                Condition: {st.session_state.condition}
                
                Verify if image matches. Return JSON:
                {{
                    "verified": bool,
                    "note": "string",
                    "title": "Viral marketplace title",
                    "description": "High conversion description with bullets",
                    "quick_price": "$XX",
                    "max_price": "$XX"
                }}
                """
                
                result = call_ai(prompt, image=image_part)
                if result:
                    st.session_state.result = result
                    st.session_state.step = "result"
                    st.rerun()

# STEP 5: RESULTS & ADS
elif st.session_state.step == "result":
    res = st.session_state.result
    
    if res.get("verified"):
        st.success(f"✅ AI Verified: {res['note']}")
    else:
        st.warning(f"⚠️ AI Note: {res['note']}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='price-card'><small>QUICK SELL</small><h1>{res['quick_price']}</h1></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='price-card' style='border-color: #10b981'><small>MAX VALUE</small><h1>{res['max_price']}</h1></div>", unsafe_allow_html=True)

    st.markdown("### Listing Content")
    st.text_input("Title", res['title'])
    st.text_area("Description", res['description'], height=250)
    
    st.button("📋 Copy to Clipboard (Title + Desc)") # Logic for copy can be added via JS if needed

    # AD SPACE: POST-APPRAISAL
    st.markdown("---")
    st.markdown("### 🚀 Reach More Buyers")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
            <div class='ad-box'>
                <b>UPS Shipping Partner</b><br>
                <small>Print labels from home and save 15%</small><br><br>
                <a href='#'>Get Labels</a>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class='ad-box'>
                <b>Promote Listing</b><br>
                <small>Boost to 5,000 extra people in your area</small><br><br>
                <a href='#'>Boost Now ($2.99)</a>
            </div>
        """, unsafe_allow_html=True)

