"""
Main entry point for Project Wand - Milestone 1: Baseline Cursor Engine.
Orchestrates webcam capture, hand detection, motion translation, telemetry logging, and UI overlays.
"""
import time
import cv2
import psutil
import config
from mouse import Mouse
from motion_engine import MotionEngine
from telemetry import TelemetryLogger
from vision import HandDetector, parse_results, draw_landmarks_and_highlight

def main():
    print("Initializing Project Wand - Baseline Cursor Engine...")
    
    # Initialize components
    mouse = Mouse()
    motion_engine = MotionEngine(mouse)
    detector = HandDetector()
    telemetry = TelemetryLogger()
    
    # Initialize webcam
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    
    if not cap.isOpened():
        print(f"Error: Unable to open webcam on camera index {config.CAMERA_INDEX}.")
        return

    print("Project Wand running. Press 'q' in the camera window to exit.")

    fps = 0.0
    detection_fps = 0.0

    try:
        while cap.isOpened():
            loop_start = time.perf_counter()

            success, frame = cap.read()
            if not success:
                print("Warning: Empty frame received from webcam.")
                continue

            # Mirror frame horizontally so moving right moves the cursor right
            frame = cv2.flip(frame, 1)

            # Process vision detection
            results, det_latency_ms = detector.process(frame)
            hand_analysis = parse_results(results)
            detection_fps = 1000.0 / det_latency_ms if det_latency_ms > 0 else 0.0

            cursor_x, cursor_y = motion_engine.last_cursor_x, motion_engine.last_cursor_y
            norm_x, norm_y, norm_z = 0.0, 0.0, 0.0

            # Perform cursor movement if hand is tracked
            if hand_analysis.has_hand:
                norm_x, norm_y, norm_z = hand_analysis.index_tip_norm
                cursor_x, cursor_y = motion_engine.process(
                    norm_x, norm_y, hand_analysis.hand_size_norm, hand_analysis.handedness
                )
                
                # Render tracking visualization
                if config.SHOW_WINDOW:
                    draw_landmarks_and_highlight(frame, hand_analysis.raw_landmarks, motion_engine.is_clicking or motion_engine.click_cooldown > 0)

            # Draw Active Tracking Area bounding box
            if config.SHOW_WINDOW and motion_engine.current_box_corners:
                import numpy as np
                h, w, _ = frame.shape
                
                # Polygon vertices from the MotionEngine
                pts = np.array([
                    [int(corner[0] * w), int(corner[1] * h)] 
                    for corner in motion_engine.current_box_corners
                ], np.int32)
                
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (255, 0, 255), 2)

            # Calculate frame performance metrics
            loop_end = time.perf_counter()
            latency_ms = (loop_end - loop_start) * 1000.0
            fps = 1000.0 / latency_ms if latency_ms > 0 else 0.0

            # Log frame metrics
            telemetry.log(
                finger_x=norm_x,
                finger_y=norm_y,
                finger_z=norm_z,
                cursor_x=cursor_x,
                cursor_y=cursor_y,
                fps=fps,
                detection_fps=detection_fps,
                latency_ms=latency_ms
            )

            # Draw Diagnostics Overlay
            if config.SHOW_WINDOW and config.SHOW_DIAGNOSTICS:
                # Text configuration
                font = cv2.FONT_HERSHEY_SIMPLEX
                scale = 0.55
                thick = 2
                color_text = (255, 255, 255)
                
                # Tracking state indicator color
                tracking_str = "YES" if hand_analysis.has_hand else "NO"
                tracking_color = (0, 255, 0) if hand_analysis.has_hand else (0, 0, 255)
                
                # Diagnostics lines
                lines = [
                    (f"FPS: {fps:.1f}", color_text),
                    (f"Latency: {latency_ms:.1f} ms", color_text),
                    (f"Tracking: {tracking_str}", tracking_color),
                    (f"Hand Confidence: {hand_analysis.confidence:.2f}", color_text),
                ]
                
                if config.BENCHMARK_MODE:
                    cpu_load = psutil.cpu_percent(interval=None)
                    lines.append((f"CPU Load: {cpu_load:.1f}%", color_text))
                    lines.append((f"Det FPS: {detection_fps:.1f}", color_text))

                # Render overlay panel background box
                overlay_h = len(lines) * 25 + 15
                cv2.rectangle(frame, (10, 10), (220, overlay_h), (0, 0, 0), cv2.FILLED)

                # Render each diagnostics line
                y_offset = 30
                for line_text, color in lines:
                    cv2.putText(frame, line_text, (20, y_offset), font, scale, color, thick)
                    y_offset += 25

                cv2.imshow("Project Wand - Baseline Cursor Engine", frame)

            # Exit on 'q' keypress
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exit signal received.")
                break

    finally:
        # Resource cleanup
        print("Cleaning up resources...")
        cap.release()
        detector.close()
        telemetry.close()
        cv2.destroyAllWindows()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
