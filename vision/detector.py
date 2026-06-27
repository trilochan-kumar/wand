"""
Computer vision module wrapper around MediaPipe Tasks HandLandmarker.
Extracts hand coordinate outputs and monitors CV process latency.
"""
import os
import time
import urllib.request
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config

class HandDetector:
    def __init__(self, 
                 max_hands: int = None, 
                 min_det_conf: float = None, 
                 min_track_conf: float = None):
        
        self.max_hands = max_hands or config.HAND_MAX_HANDS
        self.min_det_conf = min_det_conf or config.HAND_MIN_DETECTION_CONFIDENCE
        self.min_track_conf = min_track_conf or config.HAND_MIN_TRACKING_CONFIDENCE
        
        # Ensure model asset file exists
        self.model_path = config.MODEL_PATH
        if not os.path.exists(self.model_path):
            print(f"Downloading MediaPipe HandLandmarker model asset to {self.model_path}...")
            urllib.request.urlretrieve(config.MODEL_URL, self.model_path)
            print("Model download complete.")

        # Configure MediaPipe Tasks HandLandmarker
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=self.max_hands,
            min_hand_detection_confidence=self.min_det_conf,
            min_hand_presence_confidence=self.min_track_conf,
            min_tracking_confidence=self.min_track_conf
        )
        
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.last_detection_latency_ms = 0.0

    def process(self, frame_bgr) -> tuple[object, float]:
        """
        Converts the input OpenCV BGR frame to MediaPipe Image format and runs detection.
        Measures and stores processing latency for benchmarking.
        """
        # Convert BGR frame to RGB and construct mp.Image
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        timestamp_ms = int(time.perf_counter() * 1000)
        
        start_time = time.perf_counter()
        results = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        end_time = time.perf_counter()
        
        self.last_detection_latency_ms = (end_time - start_time) * 1000.0
        return results, self.last_detection_latency_ms

    def close(self) -> None:
        """Closes MediaPipe HandLandmarker resources safely."""
        if hasattr(self, 'landmarker') and self.landmarker:
            self.landmarker.close()
