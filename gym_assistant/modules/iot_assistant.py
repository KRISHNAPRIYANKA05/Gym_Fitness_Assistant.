"""
Module 3: Smart Gym Assistant (AI + IoT Integration)

No physical IoT hardware is available for this project, so this module SIMULATES
sensor streams from smart gym equipment (treadmill speed, resistance level, heart
rate) and applies simple rules to recommend resistance/rest adjustments in real time.
This keeps the same interface a real MQTT/Node-RED integration would expose.
"""
import time
import random
import streamlit as st
import pandas as pd


def simulate_reading(prev_hr, intensity):
    """Generate the next simulated sensor reading based on the previous heart rate and chosen intensity."""
    drift = {"Light": -1, "Moderate": 1, "Intense": 3}[intensity]
    hr = prev_hr + drift + random.randint(-3, 3)
    hr = max(60, min(hr, 190))
    speed = round({"Light": 4, "Moderate": 7, "Intense": 10}[intensity] + random.uniform(-0.5, 0.5), 1)
    resistance = {"Light": 2, "Moderate": 5, "Intense": 8}[intensity] + random.randint(-1, 1)
    resistance = max(1, min(resistance, 10))
    return hr, speed, resistance


def recommend(hr, age):
    max_hr = 220 - age
    pct = hr / max_hr
    if pct > 0.9:
        return "⚠️ Heart rate very high — reduce resistance and take a 60s rest.", "red"
    elif pct > 0.75:
        return "🔶 Working hard — consider easing intensity slightly.", "orange"
    elif pct < 0.5:
        return "🔵 Heart rate low — you could safely increase intensity.", "blue"
    else:
        return "✅ Heart rate in a healthy training zone — keep going.", "green"


def render(user_name, age=25):
    st.header("🔌 Smart Gym Assistant — AI + IoT Integration (Simulated)")
    st.caption(
        "Real IoT gym equipment (smart treadmills, resistance machines) streams sensor data over "
        "MQTT. Since no physical hardware is connected, this module simulates that data stream so "
        "the recommendation logic can be demonstrated end-to-end."
    )

    col1, col2 = st.columns(2)
    intensity = col1.selectbox("Workout intensity", ["Light", "Moderate", "Intense"])
    duration = col2.slider("Simulation duration (seconds)", 10, 60, 20, step=5)

    if st.button("▶ Start Simulated Session", type="primary"):
        chart_placeholder = st.empty()
        rec_placeholder = st.empty()
        table_placeholder = st.empty()

        history = []
        hr = 80
        start = time.time()
        while time.time() - start < duration:
            hr, speed, resistance = simulate_reading(hr, intensity)
            history.append({"t": len(history), "Heart Rate (bpm)": hr,
                             "Speed (km/h)": speed, "Resistance": resistance})
            df = pd.DataFrame(history).set_index("t")

            chart_placeholder.line_chart(df[["Heart Rate (bpm)"]])
            msg, _color = recommend(hr, age)
            rec_placeholder.info(f"**Live sensor reading** — HR: {hr} bpm | Speed: {speed} km/h | "
                                  f"Resistance: {resistance}/10  \n{msg}")
            time.sleep(0.6)

        table_placeholder.dataframe(pd.DataFrame(history), width='stretch', hide_index=True)
        st.success("Simulated session ended. In a real deployment, this same logic would "
                   "subscribe to live MQTT topics published by the gym equipment instead of "
                   "the `simulate_reading()` function used here.")

    with st.expander("How this would work with real hardware"):
        st.write(
            "- Equipment publishes sensor readings (heart rate strap, treadmill speed, resistance "
            "motor position) to an MQTT broker.\n"
            "- A Node-RED flow (or a Python MQTT client) subscribes to these topics and forwards "
            "readings to this dashboard.\n"
            "- The same `recommend()` rule engine (or a trained ML model) decides whether to "
            "suggest a rest, or send an adjust-resistance command back to the equipment."
        )
