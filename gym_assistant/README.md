# AI Gym & Fitness Assistant (Local Streamlit Prototype)

A local, runnable prototype of the **AI Gym & Fitness Assistant** proposal — a unified
AI-powered fitness ecosystem covering workout detection, diet planning, behavior
tracking, IoT-based smart gym assistance, and a conversational AI companion.

This build turns each of the 7 modules from the original proposal into a working
Streamlit page. It runs entirely on your own computer — no cloud account, and no paid
API key, is required.

---

## 1. What's inside

| # | Proposal module | What this prototype does |
|---|---|---|
| 1 | AI Gym Trainer (Workout Detection & Feedback) | Live webcam **or** uploaded video is analyzed with **MediaPipe Pose**; joint angles are tracked to count reps (Bicep Curl / Squat / Push-up) and give real-time form feedback. |
| 2 | AI Dietician & Calorie Coach | Computes BMI and daily calorie needs (Mifflin-St Jeor formula), generates a rule-based meal plan + grocery list from a food database, and lets you log intake with a calorie chart. |
| 3 | Smart Gym Assistant (AI + IoT) | **Simulates** a smart-equipment sensor stream (heart rate, speed, resistance) since no physical IoT hardware is available, and applies live rules to recommend intensity/rest changes. |
| 4 | AI Fitness Habit Tracker (Behavioral AI) | Logs workouts, computes streaks and consistency %, and predicts skip-risk (Low/Medium/High) with a transparent rule-based model plus a motivational nudge. |
| 5 | Virtual Gym Buddy (AI Chat Companion) | A fully offline chatbot that detects mood from keywords (tired, sore, stressed, motivated, etc.) and replies with tailored encouragement — no OpenAI/Hugging Face key needed. |
| 6 | Pose-to-Performance Analyzer | Every AI Gym Trainer session is logged automatically; this page builds a weekly Performance Score trend and progress charts from that log. |
| 7 | Gym Recommender & Planner | A weighted match-scoring engine recommends gyms from a local demo dataset based on city, goal and budget. |

> **Note on scope:** Modules 3 and 5 in the original proposal call for real IoT hardware
> and a paid conversational LLM API respectively. To keep the project **fully working,
> free, and shareable with anyone** (no hardware, no API keys, no cloud billing), those
> two modules are implemented with realistic simulations/rule-based logic instead —
> this is explained on-screen in each module's "How this works" section, and is worth
> mentioning in your assignment write-up as a scoping decision.

---

## 2. Project structure

```
gym_assistant/
├── app.py                     # Main Streamlit entry point (navigation + routing)
├── requirements.txt           # Pinned dependencies
├── README.md
├── .streamlit/config.toml     # Theme
├── data/
│   ├── exercises.csv          # Exercise reference data
│   ├── foods.csv              # Food database for the dietician module
│   ├── gyms.csv               # Mock gym dataset for the recommender
│   └── *_log.csv              # Auto-created as you use the app (workout/diet/performance logs)
└── modules/
    ├── utils.py                # Shared math/helpers (BMI, BMR, angles, scoring)
    ├── gym_trainer.py           # Module 1 + 6 (logging)
    ├── dietician.py              # Module 2
    ├── iot_assistant.py           # Module 3
    ├── habit_tracker.py            # Module 4
    ├── chat_companion.py            # Module 5
    ├── performance_analyzer.py       # Module 6 (reporting)
    └── gym_recommender.py             # Module 7
```

---

## 3. Running it locally (for you or a friend)

**Requirements:** Python 3.9–3.12 installed, and a webcam if you want to try the live
Gym Trainer session (optional — video upload also works, and every other module works
without a camera at all).

### Step-by-step

1. **Unzip the project folder** you received (or `git clone` it if shared via a repo).
2. Open a terminal inside the project folder.
3. **Create a virtual environment** (recommended, keeps things clean):
   ```bash
   python -m venv venv
   ```
4. **Activate it:**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
5. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
6. **Run the app:**
   ```bash
   streamlit run app.py
   ```
7. Your browser will open automatically at `http://localhost:8501`. If not, open that
   link manually.

That's it — everything (data, logs, models) runs and stays on your own machine.

### Common issues
- **`mediapipe` fails to install:** Make sure you're on Python 3.9–3.12 (mediapipe does
  not yet support every new Python release). Check with `python --version`.
- **Webcam doesn't open:** Close any other app using the camera (Zoom, Teams, etc.), and
  make sure your OS has granted the terminal/browser camera permission.
- **Port already in use:** Run `streamlit run app.py --server.port 8502` instead.

---

## 4. How to demo it (suggested flow for a presentation/assignment)

1. Open **Home** — set your name/age in the sidebar (used across every module).
2. Go to **AI Gym Trainer** → pick "Squat" → Live Webcam → Start a 20–30s session.
3. Go to **Performance Analyzer** → show the session you just logged plotted automatically.
4. Go to **AI Dietician** → fill in your stats → generate a meal plan + grocery list.
5. Go to **Habit Tracker** → log a workout → show the streak/consistency/skip-risk.
6. Go to **Virtual Gym Buddy** → type "I'm feeling tired today" → show the tailored reply.
7. Go to **Smart Gym Assistant (IoT)** → run a simulated session → show the live
   recommendation engine reacting to heart rate.
8. Go to **Gym Recommender** → pick a city/goal/budget → show the ranked matches.

---

## 5. Technical stack actually used

| Layer | Technology |
|---|---|
| Frontend / App shell | Streamlit |
| Computer vision | MediaPipe Pose, OpenCV |
| Data handling | Pandas, CSV-based local storage |
| Visualization | Plotly |
| AI logic | Rule-based scoring engines (BMI/BMR formulas, joint-angle state machines, keyword/lexicon sentiment, weighted recommenders) |

This mirrors the original proposal's stack (React/FastAPI/TensorFlow/MongoDB/MQTT were
scoped down to a single-language, single-process Streamlit app so it can be run and
shared as one lightweight folder — a common, legitimate step when moving from a
"proposed" architecture to a working proof-of-concept prototype).

---

## 6. Sharing with a friend

Just zip the whole `gym_assistant` folder (or share it via Google Drive/GitHub) —
everything needed to run it (code + sample data + requirements.txt) is self-contained.
Your friend only needs Python installed and to follow **Section 3** above.
