import json
from pathlib import Path

import pytest

from aniworlds_studio.promo_export import (
    InvalidPromoExport,
    build_subscription_promo,
    build_turn_promo,
    export_promo,
    generate_promo_code,
)


def test_generated_code_uses_unambiguous_canonical_format() -> None:
    symbols = iter("A2B3C4D5")

    assert generate_promo_code(lambda _: next(symbols)) == "ANI-A2B3-C4D5"


def test_subscription_promo_exports_activation_limit_and_optional_expiration() -> None:
    promo = build_subscription_promo(
        20,
        expires_at="2027-01-01T03:00:00+03:00",
        code="ANI-A2B3-C4D5",
    )

    assert promo.document == {
        "schema_version": 3,
        "code": "ANI-A2B3-C4D5",
        "reward": "multiplayer_subscription",
        "activation_limit": 20,
        "expires_at": "2027-01-01T00:00:00Z",
    }
    assert promo.filename == "ANI-A2B3-C4D5.json"


@pytest.mark.parametrize("activation_limit", [0, 101, 10_000, True])
def test_subscription_promo_rejects_invalid_activation_limit(activation_limit: int) -> None:
    with pytest.raises(InvalidPromoExport):
        build_subscription_promo(activation_limit, code="ANI-A2B3-C4D5")


@pytest.mark.parametrize("expiration", ["not-a-date", "2027-01-01T00:00:00"])
def test_subscription_promo_requires_timezone_aware_expiration(expiration: str) -> None:
    with pytest.raises(InvalidPromoExport):
        build_subscription_promo(
            1,
            expires_at=expiration,
            code="ANI-A2B3-C4D5",
        )


def test_turn_promo_normalizes_expiration_to_utc() -> None:
    promo = build_turn_promo(
        25,
        10,
        expires_at="2027-01-01T03:00:00+03:00",
        code="ANI-A2B3-C4D5",
    )

    assert promo.document == {
        "schema_version": 1,
        "code": "ANI-A2B3-C4D5",
        "turns": 25,
        "activation_limit": 10,
        "expires_at": "2027-01-01T00:00:00Z",
    }


@pytest.mark.parametrize(
    ("turns", "activations", "expiration"),
    [(0, 1, None), (101, 1, None), (1, 0, None), (1, 101, None), (1, 1, "2027-01-01")],
)
def test_turn_promo_rejects_values_outside_the_contract(
    turns: int,
    activations: int,
    expiration: str | None,
) -> None:
    with pytest.raises(InvalidPromoExport):
        build_turn_promo(
            turns,
            activations,
            expires_at=expiration,
            code="ANI-A2B3-C4D5",
        )


def test_export_creates_one_json_file_without_overwrite(tmp_path: Path) -> None:
    promo = build_subscription_promo(5, code="ANI-A2B3-C4D5")

    path = export_promo(promo, tmp_path / "promocodes")

    assert json.loads(path.read_text(encoding="utf-8")) == promo.document
    with pytest.raises(FileExistsError):
        export_promo(promo, path.parent)


def test_invalid_generated_code_is_rejected() -> None:
    with pytest.raises(InvalidPromoExport):
        build_subscription_promo(5, code="ANI-0000-0000")


@pytest.mark.parametrize("expiration", ["not-a-date", "2027-01-01T00:00:00"])
def test_turn_promo_requires_valid_timezone_aware_expiration(expiration: str) -> None:
    with pytest.raises(InvalidPromoExport):
        build_turn_promo(
            1,
            1,
            expires_at=expiration,
            code="ANI-A2B3-C4D5",
        )
