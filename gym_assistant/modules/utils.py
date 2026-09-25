"""
Shared helper functions used across the AI Gym & Fitness Assistant modules.
"""
import os
import math
import numpy as np
import pandas as pd
from datetime import datetime, date

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

EXERCISES_CSV = os.path.join(DATA_DIR, "exercises.csv")
GYMS_CSV = os.path.join(DATA_DIR, "gyms.csv")
FOODS_CSV = os.path.join(DATA_DIR, "foods.csv")

WORKOUT_LOG_CSV = os.path.join(DATA_DIR, "workout_log.csv")
PERFORMANCE_LOG_CSV = os.path.join(DATA_DIR, "performance_log.csv")
DIET_LOG_CSV = os.path.join(DATA_DIR, "diet_log.csv")


# ---------- Data loading ----------
def load_csv(path, columns=None):
    """Load a csv file, creating an empty one with headers if it does not exist yet."""
    if not os.path.exists(path):
        if columns:
            pd.DataFrame(columns=columns).to_csv(path, index=False)
        else:
            return pd.DataFrame()
    return pd.read_csv(path)


def append_row(path, row_dict, columns):
    """Append a single row (dict) to a csv log file, creating it if needed."""
    df = load_csv(path, columns=columns)
    df = pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)
    df.to_csv(path, index=False)
    return df


# ---------- Fitness math ----------
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def calculate_bmr(weight_kg, height_cm, age, gender):
    """Mifflin-St Jeor Equation."""
    if gender == "Male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


ACTIVITY_FACTORS = {
    "Sedentary (little/no exercise)": 1.2,
    "Lightly active (1-3 days/week)": 1.375,
    "Moderately active (3-5 days/week)": 1.55,
    "Very active (6-7 days/week)": 1.725,
}

GOAL_CALORIE_ADJUSTMENT = {
    "Weight Loss": -500,
    "Maintenance": 0,
    "Muscle Gain": +400,
}


def calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level, goal):
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = bmr * ACTIVITY_FACTORS.get(activity_level, 1.375)
    target = tdee + GOAL_CALORIE_ADJUSTMENT.get(goal, 0)
    return round(tdee), round(target)


def calculate_angle(a, b, c):
    """Angle (in degrees) at point b, formed by points a-b-c. Each point is (x, y)."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle


def performance_score(reps, target_reps, form_consistency, duration_sec, ideal_duration=60):
    """
    Combine rep achievement, form consistency (0-1) and pacing into a single 0-100 score.
    This is a simplified heuristic, not a clinical measurement.
    """
    rep_score = min(reps / max(target_reps, 1), 1.2) * 50  # up to 50 pts, slight bonus for exceeding
    form_score = form_consistency * 35  # up to 35 pts
    pacing_ratio = min(duration_sec, ideal_duration) / max(duration_sec, ideal_duration) if duration_sec else 0
    pacing_score = pacing_ratio * 15  # up to 15 pts
    total = rep_score + form_score + pacing_score
    return round(min(total, 100), 1)


def today_str():
    return date.today().isoformat()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
