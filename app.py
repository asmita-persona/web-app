import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Debate Arena", page_icon="⚖️", layout="centered")
st.title("⚖️ AI Debate Arena")

# Initialize memory (session_state)
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
    models = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-4-hydrogen"]
    last_error = None
    cfg = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW),
        max_output_tokens=4096,
    )

    for m in models:
        try:
            response = client.models.generate_content(
                model=m, contents=prompt, config=cfg
            )
            st.markdown(response.text)
            return response.text
        except Exception as e:
            last_error = e
            continue

    st.error(f"AI server error—please try submitting again! (Details: {last_error})")
    return None

            continue

    st.error(f"AI server error—please try submitting again! (Details: {last_error})")
    return None


# Create Navigation Tabs
tab1, tab2 = st.tabs(["⚔️ Debate Arena", "📚 Debate Academy & Rules"])

# ==========================================
# TAB 1: THE DEBATE ARENA
# ==========================================
with tab1:
    if not st.session_state.debate_active:
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username (Required)", placeholder="e.g., ariasBTS26")
        with col2:
            display_name = st.text_input(
                "Display Name (Optional)", placeholder="Leave blank to stay anonymous"
            )

        preset_topics = [
            "Custom Topic (Type your own below)",
            "Artificial Intelligence will create more jobs than it destroys",
            "Social media platforms should be legally liable for user misinformation",
            "Universal Basic Income is necessary in an automated economy",
            "Space exploration funding should be redirected to climate change solutions",
        ]
        selected_preset = st.selectbox(
            "Quick-Pick a Debate Motion (or write your own):", preset_topics
        )

        if selected_preset == "Custom Topic (Type your own below)":
            topic = st.text_input(
                "Debate Motion / Topic",
                placeholder="e.g., Artificial Intelligence will create more jobs than it destroys",
            )
        else:
            topic = st.text_input("Debate Motion / Topic", value=selected_preset)

        col3, col4 = st.columns(2)
        with col3:
            stance = st.radio("Choose Your Side:", ["For", "Against"], horizontal=True)
        with col4:
            difficulty = st.select_slider(
                "AI Opponent Strength:",
                options=["Beginner", "Intermediate", "Expert"],
                value="Intermediate",
            )

        opening = st.text_area(
            "Round 1: Your Opening Argument (Tip: Use the PEEL method!)", height=150
        )

        if st.button("Start Debate", type="primary"):
            if not username.strip() or not topic.strip() or not opening.strip():
                st.warning("Please fill in your username, topic, and opening argument!")
            else:
                st.session_state.username = username.strip()
                st.session_state.display_name = (
                    display_name.strip() if display_name.strip() else "Anonymous"
                )
                st.session_state.topic = topic.strip()
                st.session_state.stance = stance
                st.session_state.ai_stance = "Against" if stance == "For" else "For"
                st.session_state.difficulty = difficulty
                st.session_state.debate_active = True
                st.session_state.messages.append(
                    {"role": "user", "round": "Round 1: Opening", "text": opening.strip()}
                )
                st.rerun()

    else:
        st.caption(
            f"**Motion:** {st.session_state.topic} | "
            f"**You ({st.session_state.display_name}):** {st.session_state.stance} | "
            f"**AI ({st.session_state.difficulty}):** {st.session_state.ai_stance}"
        )

        # Display past messages
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.info(
                    f"**🧑 {st.session_state.display_name} – {msg['round']}**\n\n{msg['text']}"
                )
            elif msg["role"] == "ai":
                st.warning(
                    f"**🤖 AI Opponent ({st.session_state.difficulty}) – {msg['round']}**\n\n{msg['text']}"
                )
            else:
                st.success(f"**⚖️ AI Judge Verdict**\n\n{msg['text']}")

        # AI Turn
        if st.session_state.messages[-1]["role"] == "user":
            current_round_name = st.session_state.messages[-1]["round"]

            level_prompts = {
                "Beginner": "Use simple, clear vocabulary and make 1-2 straightforward points so a middle school beginner can easily follow and respond.",
                "Intermediate": "Argue like a strong high school debater with clear logic, real-world examples, and direct rebuttals.",
                "Expert": "Argue like a ruthless Yale varsity champion. Directly expose any logical fallacies, challenge weak assumptions, and dismantle arguments sharply.",
            }
            style_instruction = level_prompts[st.session_state.difficulty]

            with st.chat_message("assistant"):
                st.markdown(
                    f"**🤖 AI Opponent ({st.session_state.ai_stance} • {st.session_state.difficulty}) – {current_round_name}**"
                )
                history = "\n".join(
                    [f"{m['role']} ({m['round']}): {m['text']}" for m in st.session_state.messages]
                )
                prompt = (
                    f"You are debating '{st.session_state.ai_stance}' on the motion: '{st.session_state.topic}'. "
                    f"Difficulty style: {style_instruction} "
                    f"Debate transcript so far:\n{history}\n\n"
                    f"Respond directly to {st.session_state.display_name}'s latest points in 2 concise paragraphs."
                )
                reply = get_ai_reply(prompt)
                if reply:
                    st.session_state.messages.append(
                        {"role": "ai", "round": current_round_name, "text": reply}
                    )
                    st.session_state.round_num += 1
                    st.rerun()

        # Rounds 2 & 3 Input
        elif st.session_state.round_num <= 3:
            round_label = (
                "Round 2: Rebuttal"
                if st.session_state.round_num == 2
                else "Round 3: Closing Statement"
            )
            st.divider()
            next_arg = st.text_area(
                f"Your Turn – {round_label}:",
                height=130,
                key=f"arg_input_round_{st.session_state.round_num}",
            )
            if st.button(f"Submit {round_label}", type="primary"):
                if next_arg.strip():
                    st.session_state.messages.append(
                        {"role": "user", "round": round_label, "text": next_arg.strip()}
                    )
                    st.rerun()
                else:
                    st.warning("Please enter your argument before submitting.")

        # AI Judge Verdict
        elif st.session_state.messages[-1]["role"] == "ai":
            st.divider()
            if st.button("⚖️ Get AI Judge Verdict & Score", type="primary"):
                history = "\n".join(
                    [f"{m['role']} ({m['round']}): {m['text']}" for m in st.session_state.messages]
                )
                judge_prompt = (
                    f"You are an encouraging, impartial debate coach judging a 3-round debate on '{st.session_state.topic}'. "
                    f"Difficulty level: {st.session_state.difficulty}. Transcript:\n{history}\n\n"
                    f"Explain your feedback in clear, easy-to-understand language:\n"
                    f"1. Score {st.session_state.display_name} out of 10 on Logic, Evidence, and Rebuttal.\n"
                    f"2. Highlight their strongest argument and give 2 practical tips to improve.\n"
                    f"3. Declare who won the debate and why."
                )
                verdict = get_ai_reply(judge_prompt)
                if verdict:
                    st.session_state.messages.append(
                        {"role": "judge", "round": "Verdict", "text": verdict}
                    )
                    st.rerun()

        # Download transcript after verdict
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "judge":
            transcript_text = f"Motion: {st.session_state.topic}\n"
            transcript_text += f"Debater: {st.session_state.display_name} ({st.session_state.stance}) vs AI ({st.session_state.ai_stance})\n\n"
            for m in st.session_state.messages:
                transcript_text += f"--- {m['role'].upper()} ({m['round']}) ---\n{m['text']}\n\n"

            st.download_button(
                "📥 Download Debate Transcript",
                data=transcript_text,
                file_name="debate_transcript.txt",
                mime="text/plain",
            )

        st.divider()
        if st.button("🔄 Start a New Debate"):
            st.session_state.clear()
            st.rerun()

# ==========================================
# TAB 2: DEBATE ACADEMY & RULES
# ==========================================
with tab2:
    st.header("How to Debate & Win")
    st.write(
        "Welcome to the Debate Academy! Whether it's your first time arguing a motion or you're preparing for competitive tournaments, use these rules and frameworks to build unbeatable arguments."
    )

    st.subheader("1. How the 3-Round Format Works")
    st.markdown(
        "* **Round 1 — Opening Statement:** State your main thesis clearly and introduce your 2 strongest points.\n"
        "* **Round 2 — Rebuttal:** Attack your opponent's weakest point *first*, explain why their logic fails, and defend your own case. Never introduce brand-new topics here—focus on clashing!\n"
        "* **Round 3 — Closing Statement:** Summarize why your side won the key clashes of the debate and leave the judge with one memorable takeaway."
    )

    st.subheader("2. The PEEL Method (How to Structure Every Point)")
    st.info(
        "* **P – Point:** State your claim in one clear sentence (*\"School uniforms reduce peer pressure.\"*).\n"
        "* **E – Evidence:** Back it up with a fact, statistic, or real-world example.\n"
        "* **E – Explanation:** Explain *why* that evidence proves your point.\n"
        "* **L – Link:** Connect it back to the main debate motion."
    )

    st.subheader("3. Common Logical Fallacies to Avoid")
    with st.expander("🚫 Strawman Fallacy"):
        st.write(
            "Exaggerating or twisting your opponent's argument to make it easier to attack instead of addressing what they actually said."
        )
    with st.expander("🚫 Ad Hominem (Personal Attacks)"):
        st.write(
            "Attacking the person instead of their argument. Always stay respectful and attack ideas, not people."
        )
    with st.expander("🚫 Slippery Slope"):
        st.write(
            "Claiming that one small step will inevitably lead to an extreme disaster without proving how."
        )

    st.subheader("4. Golden Rules of the Arena")
    st.markdown(
        "1. **Respect the Motion:** Stick to your assigned side (**For** or **Against**)—great debaters can argue *both* sides of any issue.\n"
        "2. **Stay Civil:** Zero hate speech, slurs, or personal insults.\n"
        "3. **Address the Clash:** Don't ignore your opponent's best point—tackle it head-on!"
    )
            
