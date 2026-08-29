import pytest

from aniworlds_studio.clipboard_shortcuts import clipboard_event_for_keycode


@pytest.mark.parametrize(
    ("keycode", "expected"),
    [
        (65, "<<SelectAll>>"),
        (67, "<<Copy>>"),
        (86, "<<Paste>>"),
        (88, "<<Cut>>"),
        (66, None),
    ],
)
def test_physical_clipboard_keys_do_not_depend_on_keyboard_layout(
    keycode: int, expected: str | None
) -> None:
    assert clipboard_event_for_keycode(keycode) == expected
