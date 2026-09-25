"""
Module 7: Gym Recommender & Planner

A weighted scoring recommender that suggests gyms/programs based on the user's
goal, location and budget preference from a mock local dataset.
"""
import streamlit as st
from modules.utils import load_csv, GYMS_CSV

TYPE_BUDGET_SCORE = {"Budget": {"Low": 1.0, "Medium": 0.6, "High": 0.2},
                      "Premium": {"Low": 0.2, "Medium": 0.7, "High": 1.0},
                      "Boutique": {"Low": 0.3, "Medium": 0.8, "High": 0.9}}


def score_gym(row, goal, budget):
    score = 0.0
    if row["specialty"] == goal:
        score += 3.0
    score += (row["rating"] / 5.0) * 2.0
    score += TYPE_BUDGET_SCORE.get(row["type"], {}).get(budget, 0.3)
    return round(score, 2)


def render(user_name):
    st.header("📍 Gym Recommender & Planner")
    st.caption("Suggests nearby gyms and programs using a weighted match-scoring engine "
               "over a local demo dataset (swap in a real Places/CRM API for production).")

    gyms_df = load_csv(GYMS_CSV)

    col1, col2, col3 = st.columns(3)
    city = col1.selectbox("City", sorted(gyms_df["city"].unique()))
    goal = col2.selectbox("Fitness goal", sorted(gyms_df["specialty"].unique()))
    budget = col3.selectbox("Budget preference", ["Low", "Medium", "High"])

    if st.button("Find Recommendations", type="primary"):
        candidates = gyms_df[gyms_df["city"] == city].copy()
        candidates["match_score"] = candidates.apply(lambda r: score_gym(r, goal, budget), axis=1)
        candidates = candidates.sort_values("match_score", ascending=False).head(5)

        st.subheader(f"Top matches in {city}")
        for _, row in candidates.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{row['name']}** — {row['type']} · {row['specialty']}")
                c1.caption(f"Rating: {row['rating']}⭐ · Monthly fee: ₹{row['monthly_fee']}")
                c2.metric("Match score", row["match_score"])

    with st.expander("How matching works"):
        st.write(
            "Each gym gets a score built from: specialty match with your goal (+3), "
            "its community rating (scaled up to +2), and how well its pricing tier fits your "
            "stated budget preference (up to +1). This is a transparent weighted-sum "
            "recommender — the same pattern used by many real-world recommendation engines "
            "before moving to a learned ranking model."
        )
