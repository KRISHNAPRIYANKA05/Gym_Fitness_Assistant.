"""
Module 2: AI Dietician & Calorie Coach

Recommends a daily diet plan based on BMI, calorie needs and dietary preference,
generates a grocery list, and tracks logged nutritional intake over time.
"""
import random
import streamlit as st
import pandas as pd
import plotly.express as px

from modules.utils import (
    load_csv, append_row, calculate_bmi, bmi_category, calculate_daily_calories,
    ACTIVITY_FACTORS, FOODS_CSV, DIET_LOG_CSV, today_str,
)


def build_meal_plan(foods_df, diet_type, target_calories):
    """Greedy selection of one item per meal slot, favouring combos close to the calorie target."""
    plan = {}
    allowed = foods_df[foods_df["diet_type"].isin([diet_type, "Vegan"])] if diet_type != "Vegan" else foods_df[foods_df["diet_type"] == "Vegan"]
    meal_split = {"Breakfast": 0.25, "Lunch": 0.35, "Dinner": 0.30, "Snack": 0.10}

    for meal, share in meal_split.items():
        options = allowed[allowed["meal_type"] == meal]
        if options.empty:
            options = foods_df[foods_df["meal_type"] == meal]
        meal_target = target_calories * share
        options = options.copy()
        options["diff"] = (options["calories"] - meal_target).abs()
        pick = options.sort_values("diff").head(3).sample(1, random_state=random.randint(0, 9999)).iloc[0]
        plan[meal] = pick
    return plan


def render(user_name):
    st.header("🥗 AI Dietician & Calorie Coach")
    st.caption("Rule-based nutrition planning driven by your BMI, activity level and goals.")

    foods_df = load_csv(FOODS_CSV)

    with st.form("profile_form"):
        col1, col2, col3 = st.columns(3)
        weight = col1.number_input("Weight (kg)", 30.0, 200.0, 70.0, step=0.5)
        height = col2.number_input("Height (cm)", 120.0, 220.0, 170.0, step=0.5)
        age = col3.number_input("Age", 12, 90, 25)

        col4, col5 = st.columns(2)
        gender = col4.selectbox("Gender", ["Male", "Female"])
        goal = col5.selectbox("Goal", ["Weight Loss", "Maintenance", "Muscle Gain"])

        col6, col7 = st.columns(2)
        activity = col6.selectbox("Activity level", list(ACTIVITY_FACTORS.keys()))
        diet_pref = col7.selectbox("Dietary preference", ["Veg", "Non-Veg", "Vegan"])

        submitted = st.form_submit_button("Generate My Plan", type="primary")

    if submitted:
        bmi = calculate_bmi(weight, height)
        category = bmi_category(bmi)
        tdee, target_cal = calculate_daily_calories(weight, height, age, gender, activity, goal)

        c1, c2, c3 = st.columns(3)
        c1.metric("BMI", bmi, category)
        c2.metric("Maintenance calories", f"{tdee} kcal")
        c3.metric("Target calories", f"{target_cal} kcal")

        plan = build_meal_plan(foods_df, diet_pref, target_cal)
        st.subheader("Today's suggested meal plan")
        total = 0
        for meal, item in plan.items():
            total += item["calories"]
            st.write(f"**{meal}:** {item['name']} — {item['calories']} kcal "
                     f"(P: {item['protein_g']}g, C: {item['carbs_g']}g, F: {item['fat_g']}g)")
        st.caption(f"Estimated total: {total} kcal vs target {target_cal} kcal")

        st.session_state["last_meal_plan"] = plan
        st.session_state["target_cal"] = target_cal

    if "last_meal_plan" in st.session_state:
        st.subheader("🛒 Grocery list (7-day supply, based on today's plan)")
        items = [item["name"] for item in st.session_state["last_meal_plan"].values()]
        grocery = pd.DataFrame({"Item": items, "Qty (servings/week)": [7] * len(items)})
        st.dataframe(grocery, hide_index=True, width='stretch')

    st.divider()
    st.subheader("📈 Log today's intake")
    with st.form("log_form", clear_on_submit=True):
        colA, colB = st.columns([2, 1])
        food_name = colA.text_input("Food item")
        cals = colB.number_input("Calories", 0, 3000, 200, step=10)
        log_it = st.form_submit_button("Add to log")
    if log_it and food_name:
        append_row(
            DIET_LOG_CSV,
            {"date": today_str(), "user": user_name, "food": food_name, "calories": cals},
            columns=["date", "user", "food", "calories"],
        )
        st.success(f"Logged {food_name} ({cals} kcal)")

    log_df = load_csv(DIET_LOG_CSV)
    if not log_df.empty:
        user_log = log_df[log_df["user"] == user_name]
        if not user_log.empty:
            daily = user_log.groupby("date", as_index=False)["calories"].sum()
            fig = px.bar(daily, x="date", y="calories", title="Daily logged calorie intake")
            target_line = st.session_state.get("target_cal")
            if target_line:
                fig.add_hline(y=target_line, line_dash="dash", line_color="red",
                               annotation_text="Target")
            st.plotly_chart(fig, width='stretch')
