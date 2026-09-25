"""
Module 4: AI Fitness Habit Tracker (Behavioral AI)

Logs workouts, computes streaks/consistency, and uses a rule-based behavioral model
to estimate the risk that the user will skip their next workout, along with a
motivational nudge.
"""
import datetime
import streamlit as st
import pandas as pd
import plotly.express as px

from modules.utils import load_csv, append_row, WORKOUT_LOG_CSV, today_str

NUDGES = {
    "Low": "You're on a great streak — keep the momentum going today! 💪",
    "Medium": "You've missed a day or two. A short 15-minute session still counts!",
    "High": "It's been a while — even a 5-minute walk restarts the habit. You've got this.",
}


def predict_skip_risk(log_df, user_name):
    user_log = log_df[log_df["user"] == user_name].copy()
    if user_log.empty:
        return "Medium", 0, 0.0

    user_log["date"] = pd.to_datetime(user_log["date"])
    user_log = user_log.sort_values("date")
    last_date = user_log["date"].max().date()
    days_since = (datetime.date.today() - last_date).days

    # Consistency = workouts logged / days since first log
    span_days = max((user_log["date"].max() - user_log["date"].min()).days + 1, 1)
    consistency = len(user_log) / span_days

    # Current streak: consecutive days up to the most recent log
    dates = sorted(set(user_log["date"].dt.date))
    streak = 1
    for i in range(len(dates) - 1, 0, -1):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
        else:
            break

    if days_since >= 4 or consistency < 0.3:
        risk = "High"
    elif days_since >= 2 or consistency < 0.6:
        risk = "Medium"
    else:
        risk = "Low"

    return risk, streak, round(consistency * 100, 1)


def render(user_name):
    st.header("📅 AI Fitness Habit Tracker — Behavioral AI")
    st.caption("Tracks consistency and predicts when you're at risk of skipping your next workout.")

    with st.form("log_workout_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        workout_date = col1.date_input("Date", datetime.date.today())
        exercise = col2.selectbox("Exercise", ["Bicep Curl", "Squat", "Push-up", "Cardio", "Yoga", "Other"])
        completed = col3.selectbox("Completed?", ["Yes", "No"])
        logged = st.form_submit_button("Log Workout", type="primary")

    if logged:
        append_row(
            WORKOUT_LOG_CSV,
            {"date": workout_date.isoformat(), "user": user_name,
             "exercise": exercise, "completed": completed},
            columns=["date", "user", "exercise", "completed"],
        )
        st.success("Workout logged!")

    log_df = load_csv(WORKOUT_LOG_CSV)
    if log_df.empty or log_df[log_df["user"] == user_name].empty:
        st.info("No workouts logged yet for this profile. Log your first one above!")
        return

    risk, streak, consistency = predict_skip_risk(log_df, user_name)

    col1, col2, col3 = st.columns(3)
    col1.metric("Current streak", f"{streak} day(s)")
    col2.metric("Consistency", f"{consistency}%")
    col3.metric("Skip risk (next session)", risk)

    if risk == "High":
        st.error(NUDGES[risk])
    elif risk == "Medium":
        st.warning(NUDGES[risk])
    else:
        st.success(NUDGES[risk])

    st.subheader("Workout history")
    user_log = log_df[log_df["user"] == user_name].sort_values("date")
    st.dataframe(user_log, hide_index=True, width='stretch')

    counts = user_log.groupby("date").size().reset_index(name="workouts")
    fig = px.bar(counts, x="date", y="workouts", title="Workouts logged over time")
    st.plotly_chart(fig, width='stretch')

    with st.expander("How skip-risk is estimated"):
        st.write(
            "This is a transparent rule-based model (not a trained classifier): it looks at how "
            "many days have passed since your last workout and your overall logging consistency "
            "to bucket risk into Low / Medium / High. A production version could replace this "
            "with a trained model (e.g. logistic regression) over historical adherence data."
        )
