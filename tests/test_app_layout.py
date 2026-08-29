from aniworlds_studio.window_layout import fitted_window_size


def test_window_expands_to_scaled_content_size() -> None:
    assert fitted_window_size(760, 620, 780, 640) == (804, 664, 804, 664)


def test_window_keeps_larger_user_size() -> None:
    assert fitted_window_size(900, 720, 600, 500) == (900, 720, 680, 560)
