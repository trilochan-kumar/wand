# Project Wand System Architecture

Project Wand employs a decoupled, highly modular architecture to separate computer vision, motion processing, OS hardware abstraction, and metrics monitoring.

```
+------------------+     +-------------------+     +------------------+     +---------------+
| Webcam (OpenCV)  | --> | Vision Detector   | --> | Motion Engine    | --> | Mouse Layer   |
| (Frame Capture)  |     | (MediaPipe Hands) |     | (Direct Mapping) |     | (PyAutoGUI)   |
+------------------+     +-------------------+     +------------------+     +---------------+
                                   |                         |
                                   v                         v
                         +-----------------------------------------------+
                         | Telemetry Logger & Replay Motion System (CSV) |
                         +-----------------------------------------------+
```

---

## Core Components

1. **Hardware Abstraction Layer (`mouse.py`)**: Defines an interface for OS cursor controls (`move`, `click`, `drag`, `scroll`). Designed to allow low-level backend updates (e.g., Win32 `SendInput`) without modifying upstream components.
2. **Motion Engine (`motion_engine.py`)**: Translates normalized camera coordinates `(x, y)` to screen coordinates. In Milestone 1, this operates in direct raw mode to set a zero-filtering baseline.
3. **Vision Processing (`vision/`)**:
   - `detector.py`: Manages MediaPipe Hands setup, color conversions, and processing execution.
   - `landmarks.py`: Extracts index fingertip landmarks, calculates tracking confidence, and provides visualization rendering helpers.
4. **Telemetry & Benchmark Suite (`telemetry.py`)**: Captures timestamps, tracking coordinates, motion coordinates, frame rates, vision latency, and system CPU load for performance analytics and motion replaying.
5. **Main Controller & Diagnostics (`main.py`)**: Executes the primary pipeline loop and renders real-time performance indicators over the video stream.
