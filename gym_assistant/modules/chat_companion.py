"""
Module 5: Virtual Gym Buddy (AI Chat Companion)

A lightweight, fully offline conversational companion. It uses keyword + lexicon based
sentiment detection (no external API key required) to infer mood and reply with
context-appropriate motivational guidance. This keeps the project runnable by anyone
without needing an OpenAI/Hugging Face API key.
"""
import random
import streamlit as st

POSITIVE_WORDS = {"great", "good", "happy", "motivated", "strong", "energetic", "excited", "proud", "ready"}
NEGATIVE_WORDS = {"tired", "sore", "lazy", "sad", "stressed", "exhausted", "unmotivated", "bored", "hurt", "quit"}

RESPONSES = {
    "tired": ["Rest is part of training too. A light stretch or short walk might be enough for today.",
               "Your body might need recovery — try 7-8 hours of sleep tonight and a lighter session."],
    "sore": ["Soreness usually means your muscles are adapting. Consider a lighter, mobility-focused session.",
              "Try some gentle stretching and stay hydrated — soreness should ease in a day or two."],
    "lazy": ["Even a 10-minute workout beats zero — momentum builds motivation, not the other way around.",
              "Just put your shoes on and start. You can always stop after 5 minutes, but you rarely will."],
    "sad": ["I'm sorry you're feeling low. Movement can genuinely help mood — even a short walk helps.",
             "It's okay to have an off day. Be kind to yourself, and maybe try a gentle activity today."],
    "stressed": ["Exercise is one of the best stress-relievers. A cardio session could help clear your head.",
                  "Try some deep breathing before your workout — it can help you reset."],
    "unmotivated": ["Remember why you started. Revisit your goal and take one small step today.",
                      "Motivation follows action, not the other way around — start small."],
    "quit": ["Don't give up on yourself — progress isn't linear. Let's plan a lighter comeback session.",
              "Everyone hits plateaus. Let's adjust your plan instead of stopping altogether."],
    "positive": ["That's the spirit! Let's channel that energy into today's session. 🔥",
                  "Love the energy — let's make today count!"],
    "default": ["I'm here to help you stay on track. How are you feeling about your workout today?",
                 "Tell me how your body's feeling and I'll tailor a suggestion for you."],
}

QUICK_REPLIES = ["I'm feeling tired", "I'm sore today", "I'm not motivated", "Feeling great today!"]


def detect_mood(text):
    text_lower = text.lower()
    for key in RESPONSES:
        if key not in ("positive", "default") and key in text_lower:
            return key
    words = set(text_lower.split())
    if words & NEGATIVE_WORDS:
        return "unmotivated"
    if words & POSITIVE_WORDS:
        return "positive"
    return "default"


def generate_reply(text):
    mood = detect_mood(text)
    return random.choice(RESPONSES[mood]), mood


def render(user_name):
    st.header("💬 Virtual Gym Buddy — AI Chat Companion")
    st.caption("An offline, rule-based motivational companion (no external API key required).")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": f"Hey {user_name}! How are you feeling about training today?"}
        ]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    cols = st.columns(len(QUICK_REPLIES))
    quick_pick = None
    for c, label in zip(cols, QUICK_REPLIES):
        if c.button(label):
            quick_pick = label

    user_input = st.chat_input("Type how you're feeling...")
    final_input = user_input or quick_pick

    if final_input:
        st.session_state.chat_history.append({"role": "user", "content": final_input})
        reply, mood = generate_reply(final_input)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    with st.expander("How this works"):
        st.write(
            "Mood is detected with a small keyword lexicon (positive vs. negative fitness-related "
            "words). This mirrors the sentiment-analysis concept from the original proposal, "
            "implemented without requiring a paid LLM API key so the project is easy to run and "
            "share as-is."
        )
