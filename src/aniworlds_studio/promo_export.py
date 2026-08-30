"""Canonical offline creation and export of Aniworlds AI promo files."""

import json
import re
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

PROMO_CODE_PATTERN: Final = re.compile(r"^ANI-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$")
PROMO_CODE_ALPHABET: Final = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
TURN_PROMO_SCHEMA_VERSION: Final = 1
SUBSCRIPTION_PROMO_SCHEMA_VERSION: Final = 3
MIN_TURNS: Final = 1
MAX_TURNS: Final = 100
MIN_ACTIVATIONS: Final = 1
MAX_ACTIVATIONS: Final = 100
SUBSCRIPTION_REWARD: Final = "multiplayer_subscription"


class InvalidPromoExport(ValueError):
    """The requested export does not satisfy the published server contract."""


@dataclass(frozen=True, slots=True)
class PromoExport:
    """One validated JSON document and its generated canonical code."""

    code: str
    document: dict[str, object]

    @property
    def filename(self) -> str:
        return f"{self.code}.json"


def generate_promo_code(
    choose: Callable[[str], str] = secrets.choice,
) -> str:
    """Generate a non-ambiguous code in the server's canonical format."""
    random_part = "".join(choose(PROMO_CODE_ALPHABET) for _ in range(8))
    return f"ANI-{random_part[:4]}-{random_part[4:]}"


def build_subscription_promo(
    activation_limit: int,
    *,
    expires_at: str | None = None,
    code: str | None = None,
) -> PromoExport:
    """Create a subscription promo with an optional redemption deadline."""
    canonical_code = _validated_code(code or generate_promo_code())
    _validate_range("Количество активаций", activation_limit, MIN_ACTIVATIONS, MAX_ACTIVATIONS)
    return PromoExport(
        code=canonical_code,
        document={
            "schema_version": SUBSCRIPTION_PROMO_SCHEMA_VERSION,
            "code": canonical_code,
            "reward": SUBSCRIPTION_REWARD,
            "activation_limit": activation_limit,
            "expires_at": _normalized_expiration(expires_at),
        },
    )


def build_turn_promo(
    turns: int,
    activation_limit: int,
    *,
    expires_at: str | None = None,
    code: str | None = None,
) -> PromoExport:
    """Create a turn promo using the published version-one contract."""
    canonical_code = _validated_code(code or generate_promo_code())
    _validate_range("Количество ходов", turns, MIN_TURNS, MAX_TURNS)
    _validate_range("Количество активаций", activation_limit, MIN_ACTIVATIONS, MAX_ACTIVATIONS)
    return PromoExport(
        code=canonical_code,
        document={
            "schema_version": TURN_PROMO_SCHEMA_VERSION,
            "code": canonical_code,
            "turns": turns,
            "activation_limit": activation_limit,
            "expires_at": _normalized_expiration(expires_at),
        },
    )


def export_promo(promo: PromoExport, directory: Path) -> Path:
    """Write one new file without replacing a previously exported code."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / promo.filename
    serialized = json.dumps(promo.document, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as output:
        output.write(serialized)
    return path


def _validated_code(value: str) -> str:
    canonical = value.strip().upper()
    if not PROMO_CODE_PATTERN.fullmatch(canonical):
        raise InvalidPromoExport("Программа создала промокод неверного формата.")
    return canonical


def _validate_range(label: str, value: int, minimum: int, maximum: int) -> None:
    if type(value) is not int or not minimum <= value <= maximum:
        raise InvalidPromoExport(f"{label}: допустимо значение от {minimum} до {maximum}.")


def _normalized_expiration(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as error:
        raise InvalidPromoExport("Дата окончания должна быть в формате ISO 8601.") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InvalidPromoExport(
            "У даты окончания должен быть указан часовой пояс."  # noqa: RUF001
        )
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")
