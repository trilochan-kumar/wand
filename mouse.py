"""
Hardware Abstraction Layer for OS mouse interactions.
Wraps underlying libraries (PyAutoGUI initially, Win32 SendInput in future milestones).
"""
import pyautogui

class Mouse:
    def __init__(self, failsafe: bool = False):
        # Disable default pause delay for real-time responsiveness
        pyautogui.PAUSE = 0.0
        pyautogui.FAILSAFE = failsafe
        self._screen_width, self._screen_height = pyautogui.size()

    @property
    def screen_size(self) -> tuple[int, int]:
        """Returns total screen (width, height)."""
        return self._screen_width, self._screen_height

    def move(self, x: int, y: int) -> None:
        """
        Moves cursor to specified target screen coordinates.
        Clamps coordinates within valid screen boundaries.
        """
        clamped_x = max(0, min(x, self._screen_width - 1))
        clamped_y = max(0, min(y, self._screen_height - 1))
        pyautogui.moveTo(clamped_x, clamped_y)

    def click(self, button: str = "left") -> None:
        """Placeholder for future click interaction implementations."""
        pass

    def drag(self, x: int, y: int) -> None:
        """Placeholder for future drag interaction implementations."""
        pass

    def scroll(self, clicks: int) -> None:
        """Placeholder for future scroll interaction implementations."""
        pass
