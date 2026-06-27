"""
Configuration module for Project Wand.
Holds hardware, detection, telemetry, and display parameters.
"""
import os

# Camera Settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Vision & Hand Detector Settings (MediaPipe Tasks)
MODEL_FILENAME = "hand_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

HAND_MAX_HANDS = 1
HAND_MIN_DETECTION_CONFIDENCE = 0.7
HAND_MIN_TRACKING_CONFIDENCE = 0.7

# Telemetry & Benchmarking
TELEMETRY_ENABLED = True
TELEMETRY_FILE = os.path.join(os.path.dirname(__file__), "telemetry_log.csv")
BENCHMARK_MODE = True  # Captures detailed CPU load, frame latency breakdown, and cursor updates

# Motion Engine Optimizations
# Dynamic Tracking Box (Scale relative to physical hand size in the frame)
DYNAMIC_BOX_SCALE_X = 1.5
DYNAMIC_BOX_SCALE_Y = 1.1

# Biomechanical Skew: Pulls difficult corners closer to the center (0.0 = Rectangle, 0.5 = Diamond-like)
BIOMECHANICAL_SKEW = 0.4

# One Euro Filter settings (Lower min_cutoff reduces jitter at low speed. Higher beta reduces lag at high speed)
FILTER_MIN_CUTOFF = 0.0001
FILTER_BETA = 0.7
FILTER_D_CUTOFF = 1.0

# Display & Visuals
SHOW_WINDOW = True
SHOW_DIAGNOSTICS = True
FINGERTIP_COLOR = (0, 255, 255)  # Vibrant Yellow/Cyan highlight (BGR format)
FINGERTIP_RADIUS = 10
