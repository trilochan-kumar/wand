# Changelog

All notable changes to Project Wand will be documented in this file.

## [v0.1.0] - Milestone 1: Baseline Cursor Engine - 2026-06-27

### Added
- Created modular project structure (`mouse.py`, `motion_engine.py`, `telemetry.py`, `vision/`).
- Implemented `Mouse` abstraction wrapper around PyAutoGUI.
- Implemented `MotionEngine` with raw linear coordinate mapping for reference benchmarking.
- Implemented MediaPipe hand tracking integration under `vision/detector.py` and `vision/landmarks.py`.
- Added support for single-hand processing and index fingertip isolation.
- Added comprehensive `TelemetryLogger` with support for raw motion path recording (`finger_x`, `finger_y`, `finger_z`, `cursor_x`, `cursor_y`) and `BENCHMARK_MODE` CPU/latency tracking.
- Added real-time diagnostics overlay (FPS, latency, confidence, tracking state).
- Established documentation suite (`docs/DESIGN.md`, `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md`).
