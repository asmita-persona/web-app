import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Debate Arena", page_icon="⚖️")
st.title("⚖️ AI Debate Arena")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "debate_active" not in st.session_state:
    st.session_state.debate_active = False
if "round_num" not in st.session_state:
    st.session_state.round_num = 1


def ask_ai(prompt):
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    models = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-4-hydrogen"]
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW),
        max_output_tokens=4096,
    )
    for model_name in models:
        try:
            response = client.models.generate_content(model=model_name, contents=prompt, config=config)
            return response.text
        except Exception as error:
            last_error = error
    st.error(f"AI error: {last_error}")
    return None


tab1, tab2 = st.tabs(["⚔️ Debate Arena", "📚 Rules & Tips"])

with tab1:
    if not st.session_state.debate_active:
        name = st.text_input("Display Name (Optional)", placeholder="Leave blank for Anonymous")
        topic = st.selectbox(
            "Pick a Debate Topic:",
            [
                "Artificial Intelligence will create more jobs than it destroys",
                "Social media platforms should be legally liable for misinformation",
                "Universal Basic Income is necessary in an automated economy",
                "Space exploration funding should go to climate change instead",
            ],
        )
        custom_topic = st.text_input("Or type your own topic here:")
        final_topic = custom_topic.strip() if custom_topic.strip() else topic

        side = st.radio("Your Side:", ["For", "Against"], horizontal=True)
        level = st.select_slider("AI Difficulty:", ["Beginner", "Intermediate", "Expert"], value="Intermediate")
        opening = st.text_area("Round 1: Your Opening Argument", height=140)

        if st.button("Start Debate", type="primary"):
            if not opening.strip():
                st.warning("Write your opening argument first!")
            else:
                st.session_state.name = name.strip() if name.strip() else "Anonymous"
                st.session_state.topic = final_topic
                st.session_state.side = side
                st.session_state.ai_side = "Against" if side == "For" else "For"
                st.session_state.level = level
                st.session_state.debate_active = True
                st.session_state.messages.append({"role": "user", "round": "Round 1: Opening", "text": opening.strip()})
                st.rerun()

    else:
        st.caption(f"Topic: {st.session_state.topic} | You ({st.session_state.name}): {st.session_state.side} | AI ({st.session_state.level}): {st.session_state.ai_side}")

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.info(f"**🧑 {st.session_state.name} – {msg['round']}**\n\n{msg['text']}")
            elif msg["role"] == "ai":
                st.warning(f"**🤖 AI ({st.session_state.level}) – {msg['round']}**\n\n{msg['text']}")
            else:
                st.success(f"**⚖️ Judge Verdict**\n\n{msg['text']}")

        if st.session_state.messages[-1]["role"] == "user":
            round_name = st.session_state.messages[-1]["round"]
            with st.spinner("AI is thinking..."):
                history = "\n".join([f"{m['role']} ({m['round']}): {m['text']}" for m in st.session_state.messages])
                prompt = f"Debate '{st.session_state.ai_side}' on '{st.session_state.topic}' at {st.session_state.level} level. History:\n{history}\nReply to {st.session_state.name} in 2 short paragraphs."
                reply = ask_ai(prompt)
                if reply:
                    st.session_state.messages.append({"role": "ai", "round": round_name, "text": reply})
                    st.session_state.round_num += 1
                    st.rerun()

        elif st.session_state.round_num <= 3:
            round_label = "Round 2: Rebuttal" if st.session_state.round_num == 2 else "Round 3: Closing"
            next_arg = st.text_area(f"Your Turn – {round_label}:", height=120, key=f"round_{st.session_state.round_num}")
            if st.button(f"Submit {round_label}", type="primary"):
                if next_arg.strip():
                    st.session_state.messages.append({"role": "user", "round": round_label, "text": next_arg.strip()})
                    st.rerun()
                else:
                    st.warning("Type your argument before submitting!")

        elif st.session_state.messages[-1]["role"] == "ai":
            if st.button("⚖️ Get Judge Verdict", type="primary"):
                with st.spinner("Judge is scoring the debate..."):
                    history = "\n".join([f"{m['role']} ({m['round']}): {m['text']}" for m in st.session_state.messages])
                    judge_prompt = f"Judge this 3-round debate on '{st.session_state.topic}'. Transcript:\n{history}\nScore {st.session_state.name} out of 10 on Logic, Evidence, and Rebuttal, give 2 tips, and declare the winner."
                    verdict = ask_ai(judge_prompt)
                    if verdict:
                        st.session_state.messages.append({"role": "judge", "round": "Verdict", "text": verdict})
                        st.rerun()

        if st.button("🔄 New Debate"):
            st.session_state.clear()
            st.rerun()

with tab2:
    st.header("How to Debate & Win")
    st.markdown("- **Round 1 (Opening):** State your main point and 2 strong reasons.\n- **Round 2 (Rebuttal):** Attack the AI's weakest point and defend yours.\n- **Round 3 (Closing):** Summarize why your side won.")
    st.info("**PEEL Method:** **P**oint (your claim) → **E**vidence (fact/example) → **E**xplanation (why it proves your point) → **L**ink (connect back to the topic).")
