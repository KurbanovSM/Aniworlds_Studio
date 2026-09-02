import json
from datetime import datetime
from pathlib import Path

from aniworlds_studio.foundation_export import load_draft, publication_payload, publish_foundation
from aniworlds_studio.global_catalogs import (
    catalog_publication_payload,
    load_global_catalogs,
    publish_global_catalogs,
    validate_world_catalog_references,
)
from aniworlds_studio.global_settings_export import GlobalAbilitySettings, export_global_settings
from aniworlds_studio.promo_export import build_turn_promo, export_promo

ROOT = Path(__file__).parents[1]
CONTENT = ROOT / "content"


def test_every_authoring_draft_publishes_deterministically(tmp_path: Path) -> None:
    catalogs = load_global_catalogs(CONTENT / "global-catalogs.studio.json")
    draft_paths = sorted((CONTENT / "worlds").glob("*.draft.json"))
    assert draft_paths
    for draft_path in draft_paths:
        draft = load_draft(draft_path, catalogs)
        validate_world_catalog_references(draft, catalogs)
        published_path = publish_foundation(draft, catalogs, tmp_path)
        published = json.loads(published_path.read_text(encoding="utf-8"))
        timestamp = datetime.fromisoformat(published["published_at"])
        assert published == publication_payload(draft, catalogs, published_at=timestamp)


def test_shared_catalog_draft_publishes_deterministically(tmp_path: Path) -> None:
    catalogs = load_global_catalogs(CONTENT / "global-catalogs.studio.json")
    path = publish_global_catalogs(catalogs, tmp_path)
    published = json.loads(path.read_text(encoding="utf-8"))
    timestamp = datetime.fromisoformat(published["published_at"])

    assert published == catalog_publication_payload(catalogs, published_at=timestamp)
    assert len(catalogs.traits) >= 36
    assert all(trait.description.strip() for trait in catalogs.traits)


def test_every_authored_character_trait_exists_in_the_shared_catalog() -> None:
    catalogs = load_global_catalogs(CONTENT / "global-catalogs.studio.json")
    available = {trait.id for trait in catalogs.traits}

    for path in sorted((CONTENT / "worlds").glob("*.draft.json")):
        draft = load_draft(path, catalogs)
        used = {trait_id for character in draft.characters for trait_id in character.trait_ids}
        assert used <= available


def test_naruto_v4_contains_the_expanded_map_and_character_catalog() -> None:
    catalogs = load_global_catalogs(CONTENT / "global-catalogs.studio.json")
    draft = load_draft(CONTENT / "worlds" / "naruto-v4.draft.json", catalogs)

    assert len(draft.locations) == 30
    assert len(draft.characters) == 50
    assert all(
        location.map_x is not None and location.map_y is not None for location in draft.locations
    )
    assert draft.gameplay.npc_starting_currency_min == 0
    assert draft.gameplay.npc_starting_currency_max == 10_000


def test_naruto_v4_catalog_and_prepared_character_loadouts_are_complete() -> None:
    catalogs = load_global_catalogs(CONTENT / "global-catalogs.studio.json")
    draft = load_draft(CONTENT / "worlds" / "naruto-v4.draft.json", catalogs)
    items = [item for item in catalogs.equipment if item.section_id == "Narutov4"]
    items_by_id = {item.id: item for item in items}

    assert sum(item.category in {"clothing", "armor"} for item in items) == 52
    assert sum(item.category == "weapon" for item in items) == 25
    assert sum(item.category not in {"clothing", "armor", "weapon"} for item in items) == 20

    for character in draft.characters:
        item_ids = [entry.item_id for entry in character.items]
        equipped_slots = [
            items_by_id[item_id].equipment_slot
            for item_id in item_ids
            if items_by_id[item_id].equipment_slot is not None
        ]

        assert 1 <= len(item_ids) <= 10
        assert len(item_ids) == len(set(item_ids))
        assert set(item_ids) <= items_by_id.keys()
        assert set(equipped_slots) == {
            "underwear",
            "head",
            "torso",
            "hands",
            "legs",
            "feet",
            "active_weapon",
        }
        assert len(equipped_slots) == len(set(equipped_slots))
        assert 1 <= character.starting_currency_amount <= 10_000


def test_naruto_v4_uses_all_specialized_shop_kinds() -> None:
    catalogs = load_global_catalogs(CONTENT / "global-catalogs.studio.json")
    draft = load_draft(CONTENT / "worlds" / "naruto-v4.draft.json", catalogs)
    items = [item for item in catalogs.equipment if item.section_id == "Narutov4"]
    policies = {policy.shop_kind: policy for policy in draft.shop_policies}

    assert set(policies) == {
        "general_store",
        "weapon_shop",
        "armor_shop",
        "clothing_shop",
        "pharmacy",
        "tool_and_scroll_shop",
        "food_shop",
        "forge",
    }
    for kind, policy in policies.items():
        eligible = [item for item in items if kind in item.allowed_shop_kinds]
        assert len(eligible) >= policy.minimum_assortment_size
        assert policy.maximum_assortment_size <= 10


def test_global_settings_publish_the_current_studio_values(tmp_path: Path) -> None:
    path = export_global_settings(GlobalAbilitySettings(), tmp_path)
    published = json.loads(path.read_text(encoding="utf-8"))
    settings = GlobalAbilitySettings(**published["abilities"])

    settings.validate()
    assert published["schema_version"] == 1
    assert published["artifact_type"] == "aniworlds.global_gameplay_settings"


def test_audit_promo_is_written_by_the_studio_exporter(tmp_path: Path) -> None:
    expected = build_turn_promo(
        100,
        10,
        expires_at="2025-01-01T00:00:00Z",
        code="ANI-TEST-AUDT",
    )
    path = export_promo(expected, tmp_path)
    published = json.loads(path.read_text(encoding="utf-8"))

    assert published == expected.document


def test_turn_promo_round_trips_without_a_committed_publication(tmp_path: Path) -> None:
    expected = build_turn_promo(25, 3, code="ANI-TEST-RNDT")
    path = export_promo(expected, tmp_path)

    assert json.loads(path.read_text(encoding="utf-8")) == expected.document
