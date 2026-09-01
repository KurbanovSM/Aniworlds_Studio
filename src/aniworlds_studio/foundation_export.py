"""Local draft storage and compatible publication of world foundations."""

import json
from dataclasses import asdict
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
    LocationDraft,
    PeriodConnectionDraft,
    PeriodDraft,
    ShopPolicyDraft,
    StartingKitDraft,
    StartingKitItemDraft,
    UniverseDraft,
)
from aniworlds_studio.foundation_validation import validate_foundation
from aniworlds_studio.global_catalogs import (
    GlobalCatalogDraft,
    validate_world_catalog_references,
)
from aniworlds_studio.npc_generation_models import NPC_BUILDERS

DRAFT_VERSION = 2


def save_draft(draft: UniverseDraft, path: Path) -> Path:
    return _write_new_json(path, {"draft_version": DRAFT_VERSION, "universe": draft.to_mapping()})


def load_draft(path: Path, catalogs: GlobalCatalogDraft) -> UniverseDraft:
    """Load a draft only when all of its shared catalog references are available."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = payload.get("draft_version")
    if version not in {1, DRAFT_VERSION} or not isinstance(payload.get("universe"), dict):
        raise ValueError("Файл не является поддерживаемым черновиком Aniworlds Studio.")
    data = payload["universe"]
    draft = universe_from_mapping(_migrate_version_one(data) if version == 1 else data)
    validate_world_catalog_references(draft, catalogs)
    return draft


def load_published_foundation(
    path: Path,
    catalogs: GlobalCatalogDraft,
) -> UniverseDraft:
    """Restore an editable world from one published version-4 package."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if (
        payload.get("schema_version") != FOUNDATION_SCHEMA_VERSION
        or payload.get("artifact_type") != FOUNDATION_ARTIFACT_TYPE
        or not isinstance(payload.get("universe"), dict)
    ):
        raise ValueError("Файл не является опубликованным миром Studio версии 4.")
    data = json.loads(json.dumps(payload["universe"]))
    kind_settings = data.pop("creature_kind_settings", [])
    language_ids = data.pop("language_ids", [])
    group_settings = data.pop("group_settings", [])
    data["creature_kinds"] = _restore_shared_entries(
        kind_settings,
        catalogs.creature_kinds,
        "creature_kind_id",
    )
    data["languages"] = _restore_shared_ids(language_ids, catalogs.languages)
    data["groups"] = _restore_shared_entries(group_settings, catalogs.groups, "group_id")
    draft = universe_from_mapping(data)
    validate_world_catalog_references(draft, catalogs)
    return draft


def publication_payload(
    draft: UniverseDraft,
    catalogs: GlobalCatalogDraft,
    *,
    published_at: datetime | None = None,
) -> dict:
    validate_foundation(draft)
    validate_world_catalog_references(draft, catalogs)
    timestamp = published_at or datetime.now(UTC)
    return {
        "schema_version": FOUNDATION_SCHEMA_VERSION,
        "artifact_type": FOUNDATION_ARTIFACT_TYPE,
        "published_at": timestamp.isoformat(),
        "universe": _publication_universe(draft),
    }


def publish_foundation(
    draft: UniverseDraft,
    catalogs: GlobalCatalogDraft,
    directory: Path,
) -> Path:
    return _write_new_json(
        directory / f"{draft.id}.world.json",
        publication_payload(draft, catalogs),
    )


def preview_foundation(draft: UniverseDraft, catalogs: GlobalCatalogDraft) -> str:
    return json.dumps(publication_payload(draft, catalogs), ensure_ascii=False, indent=2)


def _write_new_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return path


def universe_from_mapping(data: dict[str, Any]) -> UniverseDraft:
    gameplay_keys = {
        "currency_id", "currency_name", "currency_symbol", "strength_name",
        "npc_starting_currency_min", "npc_starting_currency_max",
    }
    gameplay = GameplayConfig(**_only(data.get("gameplay", {}), gameplay_keys))
    periods = [_period_from_mapping(item) for item in data.get("periods", [])]
    locations = [LocationDraft(**item) for item in data.get("locations", [])]
    scalar = _without(
        data,
        {
            "gameplay",
            "periods",
            "locations",
            "creature_kinds",
            "languages",
            "groups",
            "items",
            "shop_policies",
            "characters",
            *NPC_BUILDERS,
        },
    )
    npc_fields: dict[str, Any] = {
        key: [builder(**item) for item in data.get(key, [])]
        for key, builder in NPC_BUILDERS.items()
    }
    return UniverseDraft(
        **scalar,
        gameplay=gameplay,
        periods=periods,
        locations=locations,
        creature_kinds=[CreatureKindDraft(**item) for item in data.get("creature_kinds", [])],
        languages=[LanguageDraft(**item) for item in data.get("languages", [])],
        groups=[GroupDraft(**item) for item in data.get("groups", [])],
        items=[ItemDraft(**item) for item in data.get("items", [])],
        shop_policies=[ShopPolicyDraft(**item) for item in data.get("shop_policies", [])],
        characters=[_character_from_mapping(item) for item in data.get("characters", [])],
        **npc_fields,
    )


def _period_from_mapping(data: dict[str, Any]) -> PeriodDraft:
    return PeriodDraft(
        **_without(data, {"location_connections", "starting_kits"}),
        location_connections=[
            PeriodConnectionDraft(**item) for item in data.get("location_connections", [])
        ],
        starting_kits=[_kit_from_mapping(item) for item in data.get("starting_kits", [])],
    )


def _kit_from_mapping(data: dict[str, Any]) -> StartingKitDraft:
    return StartingKitDraft(
        **_without(data, {"items"}),
        items=[StartingKitItemDraft(**item) for item in data.get("items", [])],
    )


def _character_from_mapping(data: dict[str, Any]) -> CharacterDraft:
    return CharacterDraft(
        **_without(data, {"abilities"}),
        abilities=[AbilityDraft(**item) for item in data.get("abilities", [])],
    )


def replace_catalog_entries(
    draft: UniverseDraft,
    field_name: str,
    entries: list[dict[str, Any]],
) -> None:
    builders = {
        **{
            key: (lambda item, factory=factory: factory(**item))
            for key, factory in NPC_BUILDERS.items()
        },
        "periods": _period_from_mapping,
        "locations": lambda item: LocationDraft(**item),
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


def _publication_universe(draft: UniverseDraft) -> dict[str, Any]:
    data = draft.to_mapping()
    for location in data["locations"]:
        if location.get("map_x") is None:
            location.pop("map_x", None)
            location.pop("map_y", None)
    if not any(data[key] for key in NPC_BUILDERS):
        for key in NPC_BUILDERS:
            data.pop(key)
    data.pop("creature_kinds", None)
    data.pop("languages", None)
    data.pop("groups", None)
    data["creature_kind_settings"] = [
        {
            "creature_kind_id": kind.id,
            "default_languages": kind.default_languages,
            "habitat_location_ids": kind.habitat_location_ids,
            "period_ids": kind.period_ids,
        }
        for kind in draft.creature_kinds
    ]
    data["language_ids"] = [language.id for language in draft.languages]
    data["group_settings"] = [
        {
            "group_id": group.id,
            "location_ids": group.location_ids,
            "ally_ids": group.ally_ids,
            "enemy_ids": group.enemy_ids,
            "period_states": group.period_states,
        }
        for group in draft.groups
    ]
    return data


def _restore_shared_entries(settings, shared_entries, id_field: str) -> list[dict[str, Any]]:
    available = {item.id: asdict(item) for item in shared_entries}
    restored: list[dict[str, Any]] = []
    for setting in settings:
        identifier = setting.get(id_field)
        base = available.get(identifier)
        if base is None:
            raise ValueError(f"Общий каталог не содержит запись {identifier!r}.")
        merged = dict(base)
        merged.update({key: value for key, value in setting.items() if key != id_field})
        restored.append(merged)
    return restored


def _restore_shared_ids(identifiers, shared_entries) -> list[dict[str, Any]]:
    available = {item.id: asdict(item) for item in shared_entries}
    missing = [identifier for identifier in identifiers if identifier not in available]
    if missing:
        raise ValueError(f"Общий каталог не содержит записи: {', '.join(missing)}.")
    return [available[identifier] for identifier in identifiers]


def _migrate_version_one(data: dict[str, Any]) -> dict[str, Any]:
    migrated = json.loads(json.dumps(data))
    locations: dict[str, dict] = {}
    for period in migrated.get("periods", []):
        nested = period.pop("starting_locations", [])
        period["location_ids"] = [item["id"] for item in nested]
        period["starting_location_ids"] = [item["id"] for item in nested if item["is_starting"]]
        period["location_connections"] = [
            {
                "location_id": item["id"],
                "connected_location_ids": item.get("connected_location_ids", []),
            }
            for item in nested
            if item.get("connected_location_ids")
        ]
        for item in nested:
            locations.setdefault(
                item["id"],
                {
                    "id": item["id"],
                    "name": item["name"],
                    "description": item["description"],
                    "price_coefficient": 1.0,
                },
            )
    migrated["locations"] = list(locations.values())
    return migrated


def _only(data: dict[str, Any], keys: set[str]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if key in keys}


def _without(data: dict[str, Any], keys: set[str]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if key not in keys}
