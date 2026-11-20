import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Debate Arena", page_icon="⚖️")
st.title("⚖️ AI Debate Arena")

# 1. User Setup
username = st.text_input("Enter a Username (Required)", placeholder="e.g., LogicMaster99")
display_name = st.text_input("Display Name (Optional)", placeholder="Leave blank to stay anonymous")

st.divider()

# 2. Debate Setup
topic = st.text_input("Enter Debate Motion / Topic", placeholder="e.g., Schools should ban homework")
stance = st.radio("Choose Your Side:", ["For", "Against"], horizontal=True)
user_argument = st.text_area("Your Opening Argument:", height=150)

# 3. AI Opponent Response
if st.button("Start Debate"):
    if not username or not topic or not user_argument:
        st.warning("Please fill in your username, topic, and opening argument!")
    else:
        ai_stance = "Against" if stance == "For" else "For"
        st.subheader(f"🤖 AI Opponent (Arguing {ai_stance})")
        
        with st.spinner("AI is preparing its counter-argument..."):
            # Connects to your secret API key in Streamlit
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            prompt = f"You are a skilled debater. The motion is: '{topic}'. The user ({username}) is arguing '{stance}' and said: '{user_argument}'. Argue strongly '{ai_stance}' in 2-3 concise, logical paragraphs."
            
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            st.write(response.text)
