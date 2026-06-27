# Project Wand
<img src="icon.png" width="150" align="right">

Project Wand is a highly advanced, camera-based motion engine that turns your hand into a precision cursor control device. It leverages MediaPipe's AI hand tracking and applies custom biomechanical motion mapping to provide an incredibly smooth, trackpad-like experience without needing any physical hardware.

## Features

- **Biomechanical Parallelogram Tracking**: The engine automatically detects if you are using your left or right hand. It then generates a customized, skewed tracking area that perfectly matches the natural windshield-wiper arc of your wrist, eliminating the strain of reaching for corners.
- **Affine Transformation Math**: The physical parallelogram tracking area is warped via an Affine matrix into a perfect square on your screen, ensuring straight finger movements always result in straight cursor movements.
- **Edge Smoothing (Smoothstep Acceleration)**: Precision tracking near the edges of your screen. Cursor velocity smoothly decelerates as you reach the borders, giving you microscopic control over small UI elements in the corners without slamming into the edge.
- **One Euro Filter**: Enterprise-grade jitter reduction algorithm dynamically applies heavy smoothing when you are holding still and reduces smoothing when you move quickly.

## Installation

### Option 1: Quick Start (Windows Only)
The easiest way to use Project Wand is to download the standalone executable. No installation or Python setup is required.

**[⬇️ Download Project Wand (.exe) Direct Link](https://github.com/trilochan-kumar/wand/releases/latest/download/Project_Wand.exe)**

1. Click the link above to download `Project_Wand.exe`.
2. Double-click the file to run it. (If Windows SmartScreen warns you, click "More info" -> "Run anyway").
3. Ensure your webcam is connected!

### Option 2: Run from Source
1. Clone this repository:
   ```bash
   git clone https://github.com/trilochan-kumar/wand.git
   cd wand
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv wand
   .\wand\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## How to Use

1. Launch the application. A window will appear showing your webcam feed.
2. Hold your hand up to the camera (index finger pointing out, or an open palm). 
3. The engine will draw a purple **Biomechanical Parallelogram** around your hand.
4. Move your hand to move the cursor. 
5. To re-center the cursor, simply push your finger outside the bounds of the purple box. The box will glide in that direction, acting as an automatic clutch!
6. To exit the application, press the **'q'** key while the camera window is in focus.

## Configuration

You can tweak the motion engine to fit your exact preferences by editing `config.py`:
- `BIOMECHANICAL_SKEW`: Determines how dramatically the corners of the tracking box are pulled inwards. (Default: 0.4. Try 0.0 for a perfect rectangle).
- `DYNAMIC_BOX_SCALE_X` / `Y`: Adjusts the overall sensitivity by scaling the tracking box relative to your hand size.
- `FILTER_MIN_CUTOFF`: Decrease this to apply heavier smoothing at low speeds (reduces jitter).
