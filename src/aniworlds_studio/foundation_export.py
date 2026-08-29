"""Local draft storage and immutable publication of world foundations."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aniworlds_studio.foundation_models import (
    FOUNDATION_ARTIFACT_TYPE,
    FOUNDATION_SCHEMA_VERSION,
    AbilityDraft,
    CharacterDraft,
    CreatureKindDraft,
    GameplayConfig,
    GroupDraft,
    ItemDraft,
    LanguageDraft,
    PeriodDraft,
    ShopPolicyDraft,
    StartingKitDraft,
    StartingKitItemDraft,
    StartingLocationDraft,
    UniverseDraft,
)
from aniworlds_studio.foundation_validation import validate_foundation


def save_draft(draft: UniverseDraft, path: Path) -> Path:
    payload = {"draft_version": 1, "universe": draft.to_mapping()}
    return _write_new_json(path, payload)


def load_draft(path: Path) -> UniverseDraft:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("draft_version") != 1 or not isinstance(payload.get("universe"), dict):
        raise ValueError("Файл не является черновиком Aniworlds Studio версии 1.")
    return universe_from_mapping(payload["universe"])


def publication_payload(draft: UniverseDraft, *, published_at: datetime | None = None) -> dict:
    validate_foundation(draft)
    timestamp = published_at or datetime.now(UTC)
    return {
        "schema_version": FOUNDATION_SCHEMA_VERSION,
        "artifact_type": FOUNDATION_ARTIFACT_TYPE,
        "published_at": timestamp.isoformat(),
        "universe": draft.to_mapping(),
    }


def publish_foundation(draft: UniverseDraft, directory: Path) -> Path:
    payload = publication_payload(draft)
    return _write_new_json(directory / f"{draft.id}.world.json", payload)


def preview_foundation(draft: UniverseDraft) -> str:
    return json.dumps(publication_payload(draft), ensure_ascii=False, indent=2)


def _write_new_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return path


def universe_from_mapping(data: dict[str, Any]) -> UniverseDraft:
    gameplay = GameplayConfig(**data.get("gameplay", {}))
    periods = [_period_from_mapping(item) for item in data.get("periods", [])]
    kinds = [CreatureKindDraft(**item) for item in data.get("creature_kinds", [])]
    languages = [LanguageDraft(**item) for item in data.get("languages", [])]
    groups = [GroupDraft(**item) for item in data.get("groups", [])]
    items = [ItemDraft(**item) for item in data.get("items", [])]
    policies = [ShopPolicyDraft(**item) for item in data.get("shop_policies", [])]
    characters = [_character_from_mapping(item) for item in data.get("characters", [])]
    scalar = {
        key: value
        for key, value in data.items()
        if key
        not in {
            "gameplay",
            "periods",
            "creature_kinds",
            "languages",
            "groups",
            "items",
            "shop_policies",
            "characters",
        }
    }
    return UniverseDraft(
        **scalar,
        gameplay=gameplay,
        periods=periods,
        creature_kinds=kinds,
        languages=languages,
        groups=groups,
        items=items,
        shop_policies=policies,
        characters=characters,
    )


def _period_from_mapping(data: dict[str, Any]) -> PeriodDraft:
    locations = [StartingLocationDraft(**item) for item in data.get("starting_locations", [])]
    kits = [_kit_from_mapping(item) for item in data.get("starting_kits", [])]
    scalar = {
        key: value
        for key, value in data.items()
        if key not in {"starting_locations", "starting_kits"}
    }
    return PeriodDraft(**scalar, starting_locations=locations, starting_kits=kits)


def _kit_from_mapping(data: dict[str, Any]) -> StartingKitDraft:
    items = [StartingKitItemDraft(**item) for item in data.get("items", [])]
    scalar = {key: value for key, value in data.items() if key != "items"}
    return StartingKitDraft(**scalar, items=items)


def _character_from_mapping(data: dict[str, Any]) -> CharacterDraft:
    abilities = [AbilityDraft(**item) for item in data.get("abilities", [])]
    scalar = {key: value for key, value in data.items() if key != "abilities"}
    return CharacterDraft(**scalar, abilities=abilities)


def replace_catalog_entries(
    draft: UniverseDraft,
    field_name: str,
    entries: list[dict[str, Any]],
) -> None:
    builders = {
        "periods": _period_from_mapping,
        "creature_kinds": lambda item: CreatureKindDraft(**item),
        "languages": lambda item: LanguageDraft(**item),
        "groups": lambda item: GroupDraft(**item),
        "items": lambda item: ItemDraft(**item),
        "shop_policies": lambda item: ShopPolicyDraft(**item),
        "characters": _character_from_mapping,
    }
    try:
        builder = builders[field_name]
    except KeyError as error:
        raise ValueError(f"Неизвестный раздел каталога: {field_name}") from error
    setattr(draft, field_name, [builder(item) for item in entries])
