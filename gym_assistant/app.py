"""
AI Gym & Fitness Assistant
Main Streamlit entry point — wires together all 7 modules described in the project proposal.

Run locally with:
    streamlit run app.py
"""
import streamlit as st

from modules import gym_trainer, dietician, iot_assistant, habit_tracker
from modules import chat_companion, performance_analyzer, gym_recommender

st.set_page_config(
    page_title="AI Gym & Fitness Assistant",
    page_icon="🏋️",
    layout="wide",
)

# ---------- Session defaults ----------
if "user_name" not in st.session_state:
    st.session_state.user_name = "Guest"
if "user_age" not in st.session_state:
    st.session_state.user_age = 25

# ---------- Sidebar ----------
st.sidebar.title("🏋️ AI Gym & Fitness Assistant")
st.sidebar.text_input("Your name", key="user_name")
st.sidebar.number_input("Your age", 12, 90, key="user_age")
st.sidebar.divider()

PAGES = {
    "🏠 Home": "home",
    "🏋️ AI Gym Trainer": "trainer",
    "🥗 AI Dietician & Calorie Coach": "diet",
    "🔌 Smart Gym Assistant (IoT)": "iot",
    "📅 Habit Tracker": "habit",
    "💬 Virtual Gym Buddy": "chat",
    "📊 Performance Analyzer": "performance",
    "📍 Gym Recommender": "recommender",
}
choice = st.sidebar.radio("Navigate", list(PAGES.keys()))
st.sidebar.divider()
st.sidebar.caption("Built as a local demo for the AI Gym & Fitness Assistant proposal. "
                    "All data stays on this machine (CSV files in the /data folder).")

page = PAGES[choice]
user_name = st.session_state.user_name or "Guest"
user_age = st.session_state.user_age

# ---------- Routing ----------
if page == "home":
    st.title("🏋️ AI Gym & Fitness Assistant")
    st.write(
        "A unified AI-powered fitness ecosystem that acts as a smart personal trainer, "
        "dietician, motivator and data-driven fitness manager — built as a local Streamlit "
        "prototype of the original project proposal."
    )
    st.info(f"Currently set up for: **{user_name}**, age {user_age}. "
            "Change this anytime from the sidebar — it's used across every module.")

    st.subheader("Modules in this prototype")
    cols = st.columns(2)
    descriptions = [
        ("🏋️ AI Gym Trainer", "Real-time rep counting & form feedback using MediaPipe pose detection."),
        ("🥗 AI Dietician & Calorie Coach", "BMI-based diet plans, grocery lists & calorie logging."),
        ("🔌 Smart Gym Assistant (IoT)", "Simulated smart-equipment sensor stream with live recommendations."),
        ("📅 Habit Tracker", "Streaks, consistency %, and rule-based skip-risk prediction."),
        ("💬 Virtual Gym Buddy", "Offline mood-aware motivational chat companion."),
        ("📊 Performance Analyzer", "Weekly performance-score trend built from your trainer sessions."),
        ("📍 Gym Recommender", "Weighted match-scoring recommender for nearby gyms/programs."),
    ]
    for i, (title, desc) in enumerate(descriptions):
        with cols[i % 2]:
            st.markdown(f"**{title}**")
            st.caption(desc)
    st.divider()
    st.caption("💡 Tip: Start with the AI Gym Trainer to log a session, then check the "
               "Performance Analyzer to see it charted automatically.")

elif page == "trainer":
    gym_trainer.render(user_name)
elif page == "diet":
    dietician.render(user_name)
elif page == "iot":
    iot_assistant.render(user_name, age=user_age)
elif page == "habit":
    habit_tracker.render(user_name)
elif page == "chat":
    chat_companion.render(user_name)
elif page == "performance":
    performance_analyzer.render(user_name)
elif page == "recommender":
    gym_recommender.render(user_name)
