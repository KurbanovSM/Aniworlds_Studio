"""Regression checks for the four large Studio-authored anime worlds."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORLD_SECTIONS = {
    "solo-leveling-v1": "SoloLeveling",
    "attack-on-titan-v1": "AttackOnTitan",
    "one-punch-man-v1": "OnePunchMan",
    "jujutsu-kaisen-v1": "JujutsuKaisen",
}


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_large_anime_worlds_keep_the_promised_content_volume() -> None:
    catalog = _read(ROOT / "content" / "global-catalogs.studio.json")
    equipment = catalog["equipment"]

    for world_id, section_id in WORLD_SECTIONS.items():
        universe = _read(ROOT / "content" / "worlds" / f"{world_id}.draft.json")[
            "universe"
        ]
        section_items = [item for item in equipment if item["section_id"] == section_id]
        items_by_id = {item["id"]: item for item in section_items}
        clothing_slots = {"underwear", "head", "torso", "hands", "legs", "feet"}

        assert len(universe["characters"]) == 50
        assert len(universe["locations"]) == 30
        assert len(universe["periods"]) == 3
        assert all(len(period["starting_kits"]) == 8 for period in universe["periods"])
        assert len(universe["npc_biographies"]) == (
            21 if world_id == "attack-on-titan-v1" else 20
        )
        assert len(universe["npc_generation_rules"]) == (
            12 if world_id == "attack-on-titan-v1" else 11
        )
        assert len(universe["npc_name_sets"][0]["male_names"]) == 50
        assert len(universe["npc_name_sets"][0]["female_names"]) == 50
        assert len(universe["npc_name_sets"][0]["surnames"]) == 50
        assert len(section_items) == 95
        assert sum(item["category"] == "weapon" for item in section_items) == 25
        for character in universe["characters"]:
            owned = [items_by_id[item["item_id"]] for item in character["items"]]
            equipped_clothing = {
                item["equipment_slot"] for item in owned if item["category"] == "clothing"
            }
            if character["name"] == "Сайтама":
                assert equipped_clothing == clothing_slots - {"head"}
                assert not any(item["equipment_slot"] == "active_weapon" for item in owned)
                assert all(
                    "Сайтам" in item["name"] or item["equipment_slot"] == "underwear"
                    for item in owned
                )
            else:
                assert equipped_clothing == clothing_slots
                assert sum(item["equipment_slot"] == "active_weapon" for item in owned) == 1
        for kit in universe["periods"][0]["starting_kits"]:
            owned = [items_by_id[item["item_id"]] for item in kit["items"]]
            equipped_clothing = {
                item["equipment_slot"] for item in owned if item["category"] == "clothing"
            }
            assert equipped_clothing == clothing_slots


def test_every_location_is_visible_on_each_period_map() -> None:
    for world_id in WORLD_SECTIONS:
        universe = _read(ROOT / "content" / "worlds" / f"{world_id}.draft.json")[
            "universe"
        ]
        location_ids = {location["id"] for location in universe["locations"]}

        assert all(set(period["location_ids"]) == location_ids for period in universe["periods"])
        assert all(len(period["location_connections"]) == 30 for period in universe["periods"])


def test_character_abilities_describe_effects_instead_of_placeholders() -> None:
    for world_id in WORLD_SECTIONS:
        universe = _read(ROOT / "content" / "worlds" / f"{world_id}.draft.json")[
            "universe"
        ]
        for character in universe["characters"]:
            for ability in character["abilities"]:
                assert "Каноническая способность персонажа" not in ability["description"]
                assert "Фирменный навык:" not in ability["short_description"]
                assert len(ability["description"]) >= 80


def test_attack_on_titan_has_non_sapient_titan_generation_profile() -> None:
    catalog = _read(ROOT / "content" / "global-catalogs.studio.json")
    titan_kind = next(item for item in catalog["creature_kinds"] if item["id"] == "aot-kind-01")
    universe = _read(ROOT / "content" / "worlds" / "attack-on-titan-v1.draft.json")[
        "universe"
    ]
    rule = next(
        item
        for item in universe["npc_generation_rules"]
        if item["id"] == "aot-npc-mindless-titan"
    )

    assert titan_kind["cognition"] == "animal"
    assert titan_kind["communication_modes"] == ["signals"]
    assert rule["creature_kind_id"] == "aot-kind-01"
