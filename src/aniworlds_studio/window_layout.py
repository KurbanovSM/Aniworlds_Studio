"""DPI-aware window sizing shared by the desktop adapter and its tests."""

from typing import Final

DEFAULT_WINDOW_WIDTH: Final = 760
DEFAULT_WINDOW_HEIGHT: Final = 620
MINIMUM_WINDOW_WIDTH: Final = 680
MINIMUM_WINDOW_HEIGHT: Final = 560
CONTENT_MARGIN: Final = 24


def fitted_window_size(
    current_width: int,
    current_height: int,
    required_width: int,
    required_height: int,
) -> tuple[int, int, int, int]:
    """Return visible and minimum dimensions for the scaled content."""
    minimum_width = max(MINIMUM_WINDOW_WIDTH, required_width + CONTENT_MARGIN)
    minimum_height = max(MINIMUM_WINDOW_HEIGHT, required_height + CONTENT_MARGIN)
    return (
        max(current_width, minimum_width),
        max(current_height, minimum_height),
        minimum_width,
        minimum_height,
    )
