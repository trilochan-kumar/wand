"""
Landmark parsing and visualization helpers for MediaPipe Tasks.
Isolates the index fingertip and calculates hand model confidence.
"""
from dataclasses import dataclass
import cv2
import config

# Standard hand connectivity graph (21 keypoints)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (5, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # Pinky
]

@dataclass
class HandAnalysisResult:
    has_hand: bool
    confidence: float
    index_tip_norm: tuple[float, float, float]  # (x, y, z) normalized coordinates
    hand_size_norm: float
    handedness: str
    raw_landmarks: object = None

def parse_results(results) -> HandAnalysisResult:
    """
    Parses MediaPipe Tasks HandLandmarkerResult to extract tracking confidence and
    the normalized index fingertip coordinates.
    """
    # Check if hand landmarks were detected
    if not results or not results.hand_landmarks:
        return HandAnalysisResult(
            has_hand=False,
            confidence=0.0,
            index_tip_norm=(0.0, 0.0, 0.0),
            hand_size_norm=0.1,  # Default safe size
            handedness="Right",
            raw_landmarks=None
        )
    
    # Process only the first hand detected
    landmarks = results.hand_landmarks[0]
    
    # Extract classification confidence score and handedness
    confidence = 0.0
    handedness = "Right"
    if results.handedness and len(results.handedness) > 0:
        confidence = results.handedness[0][0].score
        handedness = results.handedness[0][0].category_name
        
    # Extract Index Fingertip coordinate (Landmark ID 8)
    index_tip_lm = landmarks[8]
    index_tip_norm = (index_tip_lm.x, index_tip_lm.y, index_tip_lm.z)
    
    # Calculate hand size (distance from wrist [0] to middle MCP [9])
    import math
    wrist = landmarks[0]
    middle_mcp = landmarks[9]
    hand_size_norm = math.sqrt((wrist.x - middle_mcp.x)**2 + (wrist.y - middle_mcp.y)**2)
    # Prevent divide-by-zero later by enforcing a minimum size
    hand_size_norm = max(0.01, hand_size_norm)
    
    return HandAnalysisResult(
        has_hand=True,
        confidence=confidence,
        index_tip_norm=index_tip_norm,
        hand_size_norm=hand_size_norm,
        handedness=handedness,
        raw_landmarks=landmarks
    )

def draw_landmarks_and_highlight(frame, landmarks) -> None:
    """
    Draws the hand skeletal layout and overlays a highlight at the index fingertip.
    """
    if not landmarks:
        return
        
    height, width, _ = frame.shape
    
    # Draw wireframe connections
    for start_idx, end_idx in HAND_CONNECTIONS:
        pt1 = (int(landmarks[start_idx].x * width), int(landmarks[start_idx].y * height))
        pt2 = (int(landmarks[end_idx].x * width), int(landmarks[end_idx].y * height))
        cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

    # Draw joint points
    for lm in landmarks:
        pt = (int(lm.x * width), int(lm.y * height))
        cv2.circle(frame, pt, 3, (255, 0, 0), cv2.FILLED)
    
    # Highlight the index fingertip specifically (Landmark 8)
    index_tip = landmarks[8]
    cx = int(index_tip.x * width)
    cy = int(index_tip.y * height)
    
    cv2.circle(
        frame,
        (cx, cy),
        config.FINGERTIP_RADIUS,
        config.FINGERTIP_COLOR,
        cv2.FILLED
    )
