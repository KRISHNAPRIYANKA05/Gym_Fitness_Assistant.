"""
Module 1: AI Gym Trainer (Workout Detection & Feedback System)
Module 6: Pose-to-Performance Analyzer (score is computed here and logged)

Uses MediaPipe Pose to track body landmarks from a webcam or an uploaded video,
counts repetitions using joint-angle thresholds, and gives real-time form feedback.
"""
import time
import cv2
import numpy as np
import streamlit as st
import mediapipe as mp

from modules.utils import (
    calculate_angle, performance_score, append_row,
    PERFORMANCE_LOG_CSV, today_str,
)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

EXERCISE_CONFIG = {
    "Bicep Curl": {
        "joints": ("shoulder", "elbow", "wrist"),
        "down_angle": 160,   # arm extended
        "up_angle": 45,      # arm curled
        "target_reps": 12,
    },
    "Squat": {
        "joints": ("hip", "knee", "ankle"),
        "down_angle": 90,    # squatting down
        "up_angle": 165,     # standing up
        "target_reps": 15,
    },
    "Push-up": {
        "joints": ("shoulder", "elbow", "wrist"),
        "down_angle": 90,
        "up_angle": 160,
        "target_reps": 10,
    },
}

LANDMARK_MAP = {
    "shoulder": mp_pose.PoseLandmark.LEFT_SHOULDER,
    "elbow": mp_pose.PoseLandmark.LEFT_ELBOW,
    "wrist": mp_pose.PoseLandmark.LEFT_WRIST,
    "hip": mp_pose.PoseLandmark.LEFT_HIP,
    "knee": mp_pose.PoseLandmark.LEFT_KNEE,
    "ankle": mp_pose.PoseLandmark.LEFT_ANKLE,
}


class RepCounter:
    """Simple state machine that counts reps from a stream of joint angles."""

    def __init__(self, down_angle, up_angle, target_reps):
        self.down_angle = down_angle
        self.up_angle = up_angle
        self.target_reps = target_reps
        self.stage = None  # "down" or "up"
        self.reps = 0
        self.angle_samples = []

    def update(self, angle):
        self.angle_samples.append(angle)
        if angle > self.down_angle:
            self.stage = "down"
        if angle < self.up_angle and self.stage == "down":
            self.stage = "up"
            self.reps += 1
        return self.reps, self.stage

    def form_consistency(self):
        """Rough proxy for form quality: how consistent the range of motion was across reps."""
        if len(self.angle_samples) < 2:
            return 0.5
        rng = max(self.angle_samples) - min(self.angle_samples)
        # A healthy range of motion for these exercises is roughly 90-140 degrees.
        consistency = np.clip(rng / 120, 0, 1)
        return round(float(consistency), 2)


def process_frame(frame, pose_model, joints):
    """Run pose estimation on a frame, draw landmarks, and return (annotated_frame, angle or None)."""
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose_model.process(image_rgb)
    angle = None

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 200, 255), thickness=2, circle_radius=3),
            mp_drawing.DrawingSpec(color=(0, 120, 255), thickness=2),
        )
        h, w = frame.shape[:2]
        lm = results.pose_landmarks.landmark
        try:
            p1 = LANDMARK_MAP[joints[0]]
            p2 = LANDMARK_MAP[joints[1]]
            p3 = LANDMARK_MAP[joints[2]]
            a = (lm[p1].x * w, lm[p1].y * h)
            b = (lm[p2].x * w, lm[p2].y * h)
            c = (lm[p3].x * w, lm[p3].y * h)
            angle = calculate_angle(a, b, c)
            cv2.putText(frame, f"{int(angle)} deg", (int(b[0]) - 20, int(b[1]) - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        except (IndexError, KeyError):
            angle = None

    return frame, angle


def run_webcam_session(exercise, duration_sec, user_name):
    cfg = EXERCISE_CONFIG[exercise]
    counter = RepCounter(cfg["down_angle"], cfg["up_angle"], cfg["target_reps"])

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Could not access the webcam. Make sure a camera is connected and not used by another app.")
        return

    frame_placeholder = st.empty()
    stats_placeholder = st.empty()
    start = time.time()

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_model:
        while time.time() - start < duration_sec:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            frame, angle = process_frame(frame, pose_model, cfg["joints"])
            if angle is not None:
                counter.update(angle)

            remaining = int(duration_sec - (time.time() - start))
            cv2.putText(frame, f"Reps: {counter.reps}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Time left: {remaining}s", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")
            stats_placeholder.metric("Reps counted so far", counter.reps)

    cap.release()
    _finalize_session(exercise, counter, duration_sec, user_name)


def run_video_session(exercise, video_path, user_name, max_frames=600):
    cfg = EXERCISE_CONFIG[exercise]
    counter = RepCounter(cfg["down_angle"], cfg["up_angle"], cfg["target_reps"])

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    frame_placeholder = st.empty()
    progress = st.progress(0)
    frame_count = 0

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_model:
        while cap.isOpened() and frame_count < max_frames:
            ok, frame = cap.read()
            if not ok:
                break
            frame, angle = process_frame(frame, pose_model, cfg["joints"])
            if angle is not None:
                counter.update(angle)

            if frame_count % 3 == 0:  # only render every 3rd frame to keep UI responsive
                cv2.putText(frame, f"Reps: {counter.reps}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")
            frame_count += 1
            progress.progress(min(frame_count / max_frames, 1.0))

    duration_sec = frame_count / fps
    cap.release()
    progress.empty()
    _finalize_session(exercise, counter, duration_sec, user_name)


def _finalize_session(exercise, counter, duration_sec, user_name):
    form = counter.form_consistency()
    score = performance_score(counter.reps, counter.target_reps, form, duration_sec)

    st.success(f"Session complete — {counter.reps} reps detected.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Reps", counter.reps)
    col2.metric("Form Consistency", f"{int(form * 100)}%")
    col3.metric("Performance Score", f"{score}/100")

    if form < 0.4:
        st.warning("Feedback: Your range of motion looked inconsistent. Try slower, fuller reps.")
    elif counter.reps < counter.target_reps * 0.6:
        st.info(f"Feedback: You're below the target of {counter.target_reps} reps for {exercise}. Keep building up.")
    else:
        st.info("Feedback: Solid session! Form and rep count both look good.")

    append_row(
        PERFORMANCE_LOG_CSV,
        {
            "date": today_str(),
            "user": user_name,
            "exercise": exercise,
            "reps": counter.reps,
            "target_reps": counter.target_reps,
            "form_consistency": form,
            "duration_sec": round(duration_sec, 1),
            "performance_score": score,
        },
        columns=["date", "user", "exercise", "reps", "target_reps",
                 "form_consistency", "duration_sec", "performance_score"],
    )


def render(user_name):
    st.header("🏋️ AI Gym Trainer — Workout Detection & Feedback")
    st.caption("Computer-vision based rep counting and form feedback, powered by MediaPipe Pose.")

    exercise = st.selectbox("Choose an exercise", list(EXERCISE_CONFIG.keys()))
    source = st.radio("Input source", ["Live Webcam", "Upload a video"], horizontal=True)

    if source == "Live Webcam":
        duration = st.slider("Session duration (seconds)", 10, 90, 30, step=5)
        st.caption("Runs your device's webcam locally — nothing is uploaded anywhere.")
        if st.button("▶ Start Session", type="primary"):
            run_webcam_session(exercise, duration, user_name)
    else:
        uploaded = st.file_uploader("Upload a short workout video (mp4/mov)", type=["mp4", "mov", "avi"])
        if uploaded and st.button("▶ Analyze Video", type="primary"):
            import tempfile, os
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, uploaded.name)
            with open(tmp_path, "wb") as f:
                f.write(uploaded.read())
            run_video_session(exercise, tmp_path, user_name)

    with st.expander("How rep counting works"):
        st.write(
            "Each exercise tracks a joint angle (e.g. elbow angle for curls, knee angle for squats). "
            "A rep is counted whenever the joint moves from a fully extended position to a "
            "flexed position and back, using a simple state machine. Form consistency estimates "
            "how uniform your range of motion was across the set."
        )
