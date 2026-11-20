import streamlit as st
from google import genai

st.set_page_config(page_title="AI Debate Arena", page_icon="⚖️")
st.title("⚖️ AI Debate Arena")

# 1. User Setup
username = st.text_input("Enter a Username (Required)", placeholder="e.g., LogicMaster99")
display_name = st.text_input("Display Name (Optional)", placeholder="Leave blank to stay anonymous")

st.divider()

# 2. Debate Setup
topic = st.text_input("Enter Debate Motion / Topic", placeholder="e.g., Feminism is essential for modern society")
stance = st.radio("Choose Your Side:", ["For", "Against"], horizontal=True)
user_argument = st.text_area("Your Opening Argument:", height=150)

# 3. Fast Streaming AI Opponent
if st.button("Start Debate"):
    if not username or not topic or not user_argument:
        st.warning("Please fill in your username, topic, and opening argument!")
    else:
        ai_stance = "Against" if stance == "For" else "For"
        st.subheader(f"🤖 AI Opponent (Arguing {ai_stance})")
        
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        prompt = f"You are a skilled, respectful debater. The motion is: '{topic}'. The user ({username}) is arguing '{stance}' and said: '{user_argument}'. Argue strongly '{ai_stance}' in 2-3 concise, logical paragraphs."
        
        # Tries the fastest model first, with automatic backup models
        models_to_try = ["gemini-3.8-flash-lite", "gemini-3.8-flash", "gemini-3.5-flash"]
        success = False
        
        for model_name in models_to_try:
            try:
                def stream_reply():
                    for chunk in client.models.generate_content_stream(
                        model=model_name,
                        contents=prompt
                    ):
                        if chunk.text:
                            yield chunk.text
                
                st.write_stream(stream_reply)
                success = True
                break
            except Exception as e:
                continue
        
        if not success:
            st.error("All AI servers are temporarily busy—please click 'Start Debate' again in a moment.")
