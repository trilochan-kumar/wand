"""
Motion translation engine translating vision tracking space to cursor interactions.
Includes Active Area mapping and One Euro Filter for jitter reduction.
"""
import math
import time
import config
from mouse import Mouse

class OneEuroFilter:
    def __init__(self, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = None
        self.dx_prev = None
        self.t_prev = None

    def smoothing_factor(self, t_e, cutoff):
        r = 2 * math.pi * cutoff * t_e
        return r / (r + 1)

    def exponential_smoothing(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev

    def __call__(self, x, t=None):
        if t is None:
            t = time.perf_counter()
            
        if self.t_prev is None:
            self.x_prev = x
            self.dx_prev = 0.0
            self.t_prev = t
            return x

        t_e = t - self.t_prev
        if t_e <= 0:
            return self.x_prev

        # The filtered derivative of the signal.
        a_d = self.smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = self.exponential_smoothing(a_d, dx, self.dx_prev)

        # The filtered signal.
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self.smoothing_factor(t_e, cutoff)
        x_hat = self.exponential_smoothing(a, x, self.x_prev)

        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat

class MotionEngine:
    def __init__(self, mouse: Mouse):
        self.mouse = mouse
        self.screen_width, self.screen_height = mouse.screen_size
        self.last_cursor_x = 0
        self.last_cursor_y = 0
        
        # Initialize One Euro Filters for X and Y axes
        self.filter_x = OneEuroFilter(config.FILTER_MIN_CUTOFF, config.FILTER_BETA, config.FILTER_D_CUTOFF)
        self.filter_y = OneEuroFilter(config.FILTER_MIN_CUTOFF, config.FILTER_BETA, config.FILTER_D_CUTOFF)
        
        # Dynamic Box State
        self.box_cx = None
        self.box_cy = None
        self.current_box_corners = None
        
        # Y-Axis and Anti-Drift State
        self.y_history = []
        self.xy_history = []  # Stores (screen_x, screen_y)
        self.click_cooldown = 0
        self.is_clicking = False

    def smoothstep(self, x: float) -> float:
        """Applies a smoothstep curve (3x^2 - 2x^3) to decelerate near 0.0 and 1.0"""
        x = max(0.0, min(1.0, x))
        return x * x * (3.0 - 2.0 * x)

    def process(self, norm_x: float, norm_y: float, hand_size_norm: float, handedness: str) -> tuple[int, int]:
        """
        Translates normalized coordinates [0.0, 1.0] to physical screen coordinates.
        Applies Dynamic Box scaling (push-mechanic), Biomechanical Skewing, and One Euro filtering.
        Detects Y-axis tap gestures and freezes coordinates using Anti-Drift.
        """
        W = (hand_size_norm * config.DYNAMIC_BOX_SCALE_X) / 2.0
        H = (hand_size_norm * config.DYNAMIC_BOX_SCALE_Y) / 2.0
        S = config.BIOMECHANICAL_SKEW
        
        # Initialize box center if not set
        if self.box_cx is None or self.box_cy is None:
            self.box_cx = norm_x
            self.box_cy = norm_y
            
        dx = norm_x - self.box_cx
        dy = norm_y - self.box_cy
        
        # The webcam is horizontally flipped, so MediaPipe's "Left" is the physical Right Hand.
        # For a physical right hand, we pull Top-Left and Bottom-Right closer to the center.
        if handedness == "Left": # Physical Right Hand
            # Pull TL and BR
            A = W - S*W/2
            B = -S*W/2
            C = S*H/2
            D = H - S*H/2
            corners = [
                (self.box_cx - W + S*W, self.box_cy - H + S*H), # TL
                (self.box_cx + W,       self.box_cy - H),       # TR
                (self.box_cx + W - S*W, self.box_cy + H - S*H), # BR
                (self.box_cx - W,       self.box_cy + H)        # BL
            ]
        else: # Physical Left Hand
            # Pull TR and BL
            A = W - S*W/2
            B = S*W/2
            C = -S*H/2
            D = H - S*H/2
            corners = [
                (self.box_cx - W,       self.box_cy - H),       # TL
                (self.box_cx + W - S*W, self.box_cy - H + S*H), # TR
                (self.box_cx + W,       self.box_cy + H),       # BR
                (self.box_cx - W + S*W, self.box_cy + H - S*H)  # BL
            ]
            
        # Determinant for Inverse mapping
        det = A*D - B*C
        if det == 0: det = 0.001
        
        # Map physical (dx, dy) to Normalized Square [-1, 1]
        u = (D * dx - B * dy) / det
        v = (-C * dx + A * dy) / det
        
        # Push mechanics: If (u, v) is outside [-1, 1], we push the box center
        if u < -1.0 or u > 1.0 or v < -1.0 or v > 1.0:
            u_clamp = max(-1.0, min(1.0, u))
            v_clamp = max(-1.0, min(1.0, v))
            
            # Error in normalized space
            err_u = u - u_clamp
            err_v = v - v_clamp
            
            # Convert error back to physical space to shift center
            shift_dx = A * err_u + B * err_v
            shift_dy = C * err_u + D * err_v
            
            self.box_cx += shift_dx
            self.box_cy += shift_dy
            
            u = u_clamp
            v = v_clamp
            
            # Re-calculate corners based on new pushed center
            if handedness == "Left":
                corners = [
                    (self.box_cx - W + S*W, self.box_cy - H + S*H),
                    (self.box_cx + W,       self.box_cy - H),
                    (self.box_cx + W - S*W, self.box_cy + H - S*H),
                    (self.box_cx - W,       self.box_cy + H)
                ]
            else:
                corners = [
                    (self.box_cx - W,       self.box_cy - H),
                    (self.box_cx + W - S*W, self.box_cy - H + S*H),
                    (self.box_cx + W,       self.box_cy + H),
                    (self.box_cx - W + S*W, self.box_cy + H - S*H)
                ]

        self.current_box_corners = corners
        
        # Map normalized square [-1, 1] to screen [0, 1]
        mapped_x = (u + 1.0) / 2.0
        mapped_y = (v + 1.0) / 2.0
        
        # Apply Smoothstep edge deceleration
        smooth_x = self.smoothstep(mapped_x)
        smooth_y = self.smoothstep(mapped_y)
        
        # Apply One Euro Filter to mapped coordinates
        filtered_x = self.filter_x(smooth_x)
        filtered_y = self.filter_y(smooth_y)
        
        # Add a pixel overshoot margin to guarantee we can trigger screen-edge UI elements like taskbars.
        # This forces the filter to quickly smash into the physical screen bounds instead of slowly asymptoting.
        margin = 15
        
        # Map normalized coordinate directly to pixel dimensions, expanded by margin
        screen_x = int(filtered_x * (self.screen_width + margin * 2) - margin)
        screen_y = int(filtered_y * (self.screen_height + margin * 2) - margin)

        # Update History
        self.xy_history.append((screen_x, screen_y))
        if len(self.xy_history) > max(10, config.ANTI_DRIFT_FRAMES):
            self.xy_history.pop(0)
            
        self.y_history.append(norm_y)
        if len(self.y_history) > 3:
            self.y_history.pop(0)
            
        # Y-Axis Tap Detection
        self.is_clicking = False
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
            # Maintain frozen coordinates during cooldown to prevent post-click drift
            if len(self.xy_history) >= config.ANTI_DRIFT_FRAMES:
                screen_x, screen_y = self.xy_history[-config.ANTI_DRIFT_FRAMES]
        elif len(self.y_history) >= 2:
            # Calculate Y velocity
            y_vel = self.y_history[-1] - self.y_history[-2]
            
            # Check for a sharp Y-tap (up or down)
            if abs(y_vel) > config.Y_TAP_THRESHOLD:
                # Trigger Click!
                self.mouse.click()
                self.click_cooldown = config.CLICK_COOLDOWN_FRAMES
                self.is_clicking = True
                
                # Time-Travel Anti-Drift: Revert to older coordinates
                if len(self.xy_history) >= config.ANTI_DRIFT_FRAMES:
                    screen_x, screen_y = self.xy_history[-config.ANTI_DRIFT_FRAMES]

        # Move physical cursor (mouse.py handles the strict clamping)
        self.mouse.move(screen_x, screen_y)
        self.last_cursor_x = screen_x
        self.last_cursor_y = screen_y
        
        return screen_x, screen_y
