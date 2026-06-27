# Project Wand Roadmap

This document outlines the milestones and evolutionary phases of Project Wand as we build the world's best webcam-based pointing device.

---

## Milestone 1: Baseline Cursor Engine (Current)
- [x] Establish modular codebase (Vision, Motion Engine, Mouse Abstraction, Telemetry).
- [x] Abstract mouse hardware interaction via a generic `Mouse` class.
- [x] Single index fingertip tracking with raw cursor mapping.
- [x] Benchmark Mode tracking latency, frame rates, CPU usage, and cursor updates.
- [x] Basic diagnostics overlay (FPS, latency, confidence).
- [x] Save raw motion paths for replay tools.

## Milestone 2: Low-Latency OS Integration
- [ ] Migrate `Mouse` backend from PyAutoGUI to Win32 `SendInput` to minimize operating system dispatch latency.
- [ ] Implement precise screen bounding-box mapping to handle multi-monitor setups and custom coordinate scaling.

## Milestone 3: Motion Engine Optimization (Smoothing & Filtering)
- [ ] Build a motion replay utility that passes recorded raw paths through filters.
- [ ] Implement and evaluate standard filter layers:
  - Moving Average
  - One Euro Filter
  - Kalman Filter
- [ ] Benchmark filter latency vs. jitter suppression to find the optimal trade-off.

## Milestone 4: Core Touchpad Actions (Clicks & Drags)
- [ ] Define precise, reliable, and low-latency click gestures (e.g., tap, hover-dwell, pinch).
- [ ] Implement dragging support.
- [ ] Minimize false triggers during rapid movement.

## Milestone 5: Advanced Control & Productivity
- [ ] Edge handling (coasting / virtual boundary scrolling).
- [ ] Gestures for scrolling, panning, and zooming.
- [ ] Adaptive cursor acceleration based on velocity.
