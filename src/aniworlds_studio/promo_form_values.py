"""Pure validation and conversion for promo-code form controls."""

from datetime import datetime, timedelta, tzinfo

from aniworlds_studio.promo_export import InvalidPromoExport


def bounded_integer_candidate(candidate: str, maximum: int) -> bool:
    """Allow an empty edit or an ASCII integer no greater than the UI maximum."""
    return candidate == "" or (
        candidate.isascii() and candidate.isdecimal() and int(candidate) <= maximum
    )


def expiration_from_local_fields(
    date_text: str,
    time_text: str,
    *,
    timezone: tzinfo | None = None,
) -> str | None:
    """Convert friendly local date and time fields to a timezone-aware value."""
    date_value = date_text.strip()
    time_value = time_text.strip()
    if not date_value and not time_value:
        return None
    if not date_value or not time_value:
        raise InvalidPromoExport("Укажите и дату, и время окончания промокода.")
    try:
        parsed = datetime.strptime(f"{date_value} {time_value}", "%d.%m.%Y %H:%M")
    except ValueError as error:
        raise InvalidPromoExport(
            "Дата и время должны иметь формат ДД.ММ.ГГГГ и ЧЧ:ММ."  # noqa: RUF001
        ) from error
    aware = parsed.astimezone() if timezone is None else parsed.replace(tzinfo=timezone)
    return aware.isoformat()


def quick_expiration_fields(
    days: int,
    *,
    now: datetime | None = None,
) -> tuple[str, str]:
    """Return friendly local date and time values for a quick deadline button."""
    current = now or datetime.now().astimezone()
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("Current time must include a timezone.")
    expiration = current + timedelta(days=days)
    return expiration.strftime("%d.%m.%Y"), expiration.strftime("%H:%M")
