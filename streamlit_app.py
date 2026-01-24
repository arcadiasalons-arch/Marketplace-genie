import time
from tenacity import retry, stop_after_attempt, wait_random_exponential

# This decorator tells the function to retry if it hits a 429 error
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def call_gemini_safely(prompt, image):
    return client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, image],
        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
    )

if st.button("🚀 EXECUTE FULL ANALYSIS") and item_name and uploaded_file:
    with st.spinner("Genie is busy, retrying if needed..."):
        try:
            img = Image.open(uploaded_file)
            # Call our new 'safe' function
            gemini_response = call_gemini_safely(
                f"Appraise {item_name} for Jan 2026 market.", 
                img
            )
            st.success("Analysis Complete!")
            st.write(gemini_response.text)
            
        except Exception as e:
            if "429" in str(e):
                st.error("🧞 The Genie is exhausted! The daily limit of 100 requests has been reached. Try again in a few hours or upgrade to Tier 1.")
            else:
                st.error(f"Error: {e}")
