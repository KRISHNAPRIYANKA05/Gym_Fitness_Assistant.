"""
Module 6: Pose-to-Performance Analyzer

Reads the performance log written by the AI Gym Trainer module (reps, form
consistency, performance score per session) and builds a weekly progress report.
"""
import pandas as pd
import streamlit as st
import plotly.express as px

from modules.utils import load_csv, PERFORMANCE_LOG_CSV


def render(user_name):
    st.header("📊 Pose-to-Performance Analyzer")
    st.caption("Weekly progress built from every session recorded in the AI Gym Trainer module.")

    df = load_csv(PERFORMANCE_LOG_CSV)
    if df.empty or df[df["user"] == user_name].empty:
        st.info("No workout sessions recorded yet. Complete a session in the "
                 "**AI Gym Trainer** tab first — it automatically logs data here.")
        return

    user_df = df[df["user"] == user_name].copy()
    user_df["date"] = pd.to_datetime(user_df["date"])

    latest = user_df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sessions logged", len(user_df))
    col2.metric("Avg performance score", f"{user_df['performance_score'].mean():.1f}/100")
    col3.metric("Best score", f"{user_df['performance_score'].max():.1f}/100")
    col4.metric("Latest score", f"{latest['performance_score']:.1f}/100")

    st.subheader("Performance score trend")
    fig1 = px.line(user_df, x="date", y="performance_score", color="exercise",
                    markers=True, title="Performance Score over time")
    st.plotly_chart(fig1, width='stretch')

    st.subheader("Reps vs target reps")
    fig2 = px.bar(user_df, x="date", y=["reps", "target_reps"], barmode="group",
                   title="Reps achieved vs target")
    st.plotly_chart(fig2, width='stretch')

    st.subheader("Weekly summary")
    weekly = user_df.set_index("date").resample("W").agg(
        sessions=("performance_score", "count"),
        avg_score=("performance_score", "mean"),
        avg_form=("form_consistency", "mean"),
    ).dropna().reset_index()
    weekly["avg_score"] = weekly["avg_score"].round(1)
    weekly["avg_form"] = (weekly["avg_form"] * 100).round(1)
    st.dataframe(weekly.rename(columns={
        "date": "Week ending", "sessions": "Sessions",
        "avg_score": "Avg Score", "avg_form": "Avg Form %"
    }), hide_index=True, width='stretch')

    st.subheader("Full session log")
    st.dataframe(user_df.sort_values("date", ascending=False), hide_index=True, width='stretch')
