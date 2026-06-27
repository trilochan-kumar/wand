"""
Telemetry module for Project Wand.
Logs frame timings, coordinates, CPU loads, and latency metrics to CSV for offline analysis.
"""
import csv
import time
import os
import psutil
import config

class TelemetryLogger:
    def __init__(self, filepath: str = None, enabled: bool = True):
        self.enabled = enabled and config.TELEMETRY_ENABLED
        self.filepath = filepath or config.TELEMETRY_FILE
        self.file = None
        self.writer = None
        
        if self.enabled:
            # Initialize telemetry file and write header
            file_exists = os.path.exists(self.filepath)
            self.file = open(self.filepath, mode="a", newline="", encoding="utf-8")
            self.writer = csv.writer(self.file)
            
            if not file_exists or os.path.getsize(self.filepath) == 0:
                header = [
                    "timestamp",
                    "finger_x",
                    "finger_y",
                    "finger_z",
                    "cursor_x",
                    "cursor_y",
                    "fps",
                    "detection_fps",
                    "latency_ms",
                    "cpu_usage_pct"
                ]
                self.writer.writerow(header)
                self.file.flush()

    def log(self, 
            finger_x: float, 
            finger_y: float, 
            finger_z: float, 
            cursor_x: int, 
            cursor_y: int, 
            fps: float, 
            detection_fps: float, 
            latency_ms: float) -> None:
        """
        Logs a telemetry entry for the current frame.
        Uses psutil with interval=None to fetch CPU usage non-blockingly.
        """
        if not self.enabled:
            return
            
        timestamp = time.time()
        cpu_usage = psutil.cpu_percent(interval=None)
        
        row = [
            timestamp,
            finger_x,
            finger_y,
            finger_z,
            cursor_x,
            cursor_y,
            fps,
            detection_fps,
            latency_ms,
            cpu_usage
        ]
        
        self.writer.writerow(row)
        # Flush regularly to prevent loss of telemetry data if system crashes
        self.file.flush()

    def close(self) -> None:
        """Closes telemetry resources safely."""
        if self.file:
            self.file.close()
            self.file = None
