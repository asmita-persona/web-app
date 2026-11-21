import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Debate Arena", page_icon="⚖️")
st.title("⚖️ AI Debate Arena")

# Initialize memory (session_state) so the debate stays on screen across rounds
if "messages" not in st.session_state:
    st.session_state.messages = []
if "debate_active" not in st.session_state:
    st.session_state.debate_active = False
if "round_num" not in st.session_state:
    st.session_state.round_num = 1

@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def get_ai_reply(prompt):
    client = get_client()
    models = ["gemini-3.8-flash-lite", "gemini-3.8-flash", "gemini-3.5-flash"]
    for m in models:
        try:
            def stream():
                for chunk in client.models.generate_content_stream(
                    model=m,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                        max_output_tokens=450
                    )
                ):
                    if chunk.text:
                        yield chunk.text
            return st.write_stream(stream)
        except Exception:
            continue
    st.error("AI server is busy—please try submitting again!")
    return None

# --- SETUP SCREEN (Before Debate Starts) ---
if not st.session_state.debate_active:
    username = st.text_input("Enter a Username (Required)", placeholder="e.g., ariasBTS26")
    display_name = st.text_input("Display Name (Optional)", placeholder="Leave blank to stay anonymous")
    st.divider()
    topic = st.text_input("Debate Motion / Topic", placeholder="e.g., Feminism is essential for modern society")
    stance = st.radio("Choose Your Side:", ["For", "Against"], horizontal=True)
    opening = st.text_area("Round 1: Your Opening Argument", height=150)

    if st.button("Start Debate"):
        if not username or not topic or not opening:
            st.warning("Please enter your username, topic, and opening argument!")
        else:
            st.session_state.username = username
            st.session_state.topic = topic
            st.session_state.stance = stance
            st.session_state.ai_stance = "Against" if stance == "For" else "For"
            st.session_state.debate_active = True
            st.session_state.messages.append({"role": "user", "round": "Round 1: Opening", "text": opening})
            st.rerun()

# --- ACTIVE DEBATE SCREEN ---
else:
    st.caption(f"**Motion:** {st.session_state.topic} | **You ({st.session_state.username}):** {st.session_state.stance} | **AI:** {st.session_state.ai_stance}")
    
    # Display all past arguments in order
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.info(f"**🧑 {st.session_state.username} — {msg['round']}**\n\n{msg['text']}")
        elif msg["role"] == "ai":
            st.warning(f"**🤖 AI Opponent — {msg['round']}**\n\n{msg['text']}")
        else:
            st.success(f"**⚖️ AI Judge Verdict**\n\n{msg['text']}")

    # Generate AI turn if the user just spoke
    if st.session_state.messages[-1]["role"] == "user":
        last_user_text = st.session_state.messages[-1]["text"]
        current_round_name = st.session_state.messages[-1]["round"]
        
        with st.chat_message("assistant"):
            st.markdown(f"**🤖 AI Opponent ({st.session_state.ai_stance}) — {current_round_name}**")
            history = "\n".join([f"{m['role']}: {m['text']}" for m in st.session_state.messages])
            prompt = (
                f"You are a sharp, respectful competitive debater arguing '{st.session_state.ai_stance}' on '{st.session_state.topic}'. "
                f"Here is the debate so far:\n{history}\n\n"
                f"Respond directly to {st.session_state.username}'s latest points in 2 concise, logical paragraphs."
            )
            reply = get_ai_reply(prompt)
            if reply:
                st.session_state.messages.append({"role": "ai", "round": current_round_name, "text": reply})
                st.session_state.round_num += 1
                st.rerun()

    # Next Round Input Box (Rounds 2 & 3)
    elif st.session_state.round_num <= 3:
        round_label = "Round 2: Rebuttal" if st.session_state.round_num == 2 else "Round 3: Closing Statement"
        st.divider()
        next_arg = st.text_area(f"Your Turn — {round_label}:", height=130)
        if st.button(f"Submit {round_label}"):
            if next_arg:
                st.session_state.messages.append({"role": "user", "round": round_label, "text": next_arg})
                st.rerun()

    # Final AI Judge Scoring after Round 3
    elif st.session_state.messages[-1]["role"] == "ai":
        st.divider()
        if st.button("⚖️ Get AI Judge Verdict & Score"):
            history = "\n".join([f"{m['role']} ({m['round']}): {m['text']}" for m in st.session_state.messages])
            judge_prompt = (
                f"You are an impartial Yale Debate Judge evaluating a 3-round debate on '{st.session_state.topic}'. "
                f"Transcript:\n{history}\n\n"
                f"1. Score {st.session_state.username} out of 10 on Logic, Evidence, and Rebuttal.\n"
                f"2. Highlight their strongest point and give 2 actionable tips to improve.\n"
                f"3. Declare who won the debate and why."
            )
            verdict = get_ai_reply(judge_prompt)
            if verdict:
                st.session_state.messages.append({"role": "judge", "round": "Verdict", "text": verdict})
                st.rerun()

    # Reset Button
    st.divider()
    if st.button("🔄 Start a New Debate"):
        st.session_state.clear()
        st.rerun()
