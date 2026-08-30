from datetime import UTC, datetime, timedelta, timezone

import pytest

from aniworlds_studio.promo_export import InvalidPromoExport
from aniworlds_studio.promo_form_values import (
    bounded_integer_candidate,
    expiration_from_local_fields,
    quick_expiration_fields,
)


@pytest.mark.parametrize(("value", "expected"), [("", True), ("100", True), ("101", False)])
def test_bounded_integer_candidate_enforces_visible_maximum(
    value: str,
    expected: bool,
) -> None:
    assert bounded_integer_candidate(value, 100) is expected


@pytest.mark.parametrize("value", ["-1", "1.5", "abc", "\uff11\uff10\uff10"])
def test_bounded_integer_candidate_rejects_non_ascii_integer(value: str) -> None:
    assert bounded_integer_candidate(value, 100) is False


def test_local_expiration_fields_include_selected_timezone() -> None:
    result = expiration_from_local_fields(
        "01.01.2027",
        "03:15",
        timezone=timezone(timedelta(hours=3)),
    )

    assert result == "2027-01-01T03:15:00+03:00"
    assert expiration_from_local_fields("", "", timezone=UTC) is None


def test_local_expiration_fields_use_computer_timezone_by_default() -> None:
    result = expiration_from_local_fields("01.01.2027", "03:15")

    assert result is not None
    assert datetime.fromisoformat(result).utcoffset() is not None


@pytest.mark.parametrize(
    ("date_value", "time_value"),
    [("01.01.2027", ""), ("", "03:15"), ("2027-01-01", "03:15"), ("01.01.2027", "25:00")],
)
def test_local_expiration_fields_reject_incomplete_or_invalid_values(
    date_value: str,
    time_value: str,
) -> None:
    with pytest.raises(InvalidPromoExport):
        expiration_from_local_fields(date_value, time_value, timezone=UTC)


def test_quick_expiration_fields_add_selected_number_of_days() -> None:
    now = datetime(2027, 1, 1, 12, 34, tzinfo=UTC)

    assert quick_expiration_fields(30, now=now) == ("31.01.2027", "12:34")


def test_quick_expiration_requires_timezone_aware_clock() -> None:
    with pytest.raises(ValueError):
        quick_expiration_fields(7, now=datetime(2027, 1, 1))
