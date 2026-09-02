# ruff: noqa: RUF001

import json
from datetime import UTC, datetime

import pytest

from aniworlds_studio.foundation_export import (
    load_draft,
    load_published_foundation,
    preview_foundation,
    publication_payload,
    publish_foundation,
    save_draft,
    universe_from_mapping,
)
from aniworlds_studio.foundation_models import (
    AbilityDraft,
    CharacterDraft,
    CreatureKindDraft,
    EquipmentDraft,
    EquipmentSectionDraft,
    GroupDraft,
    ItemDraft,
    PeriodConnectionDraft,
    PeriodDraft,
    ShopPolicyDraft,
    StartingKitItemDraft,
    StartingLocationDraft,
    UniverseDraft,
)
from aniworlds_studio.foundation_validation import InvalidFoundation, validate_foundation
from aniworlds_studio.global_catalogs import GlobalCatalogDraft


def _minimal_foundation() -> UniverseDraft:
    draft = UniverseDraft()
    draft.creature_kinds = [
        CreatureKindDraft(
            id="human",
            name="Человек",
            description="Обычный человек",
        )
    ]
    return draft


def _shared_catalogs(draft: UniverseDraft) -> GlobalCatalogDraft:
    return GlobalCatalogDraft(
        creature_kinds=draft.creature_kinds,
        groups=draft.groups,
    )


def test_default_foundation_requires_explicit_kind_card() -> None:
    draft = UniverseDraft()

    with pytest.raises(InvalidFoundation, match="вид или расу"):
        validate_foundation(draft)


def test_minimal_explicit_foundation_is_publishable() -> None:
    draft = _minimal_foundation()

    payload = publication_payload(
        draft,
        _shared_catalogs(draft),
        published_at=datetime(2026, 8, 29, tzinfo=UTC),
    )
    assert payload["schema_version"] == 4
    assert payload["artifact_type"] == "aniworlds.world_foundation"
    assert payload["published_at"] == "2026-08-29T00:00:00+00:00"
    assert len(payload["universe"]["periods"][0]["starting_kits"]) == 1
    published_location = payload["universe"]["locations"][0]
    assert published_location == {
        "id": "start",
        "name": "Стартовая локация",
        "description": "Описание стартовой локации",
        "price_coefficient": 1.0,
    }
    published_period = payload["universe"]["periods"][0]
    assert published_period["location_ids"] == ["start"]
    assert published_period["starting_location_ids"] == ["start"]
    assert published_period["location_connections"] == []
    assert "creature_kinds" not in payload["universe"]
    assert "languages" not in payload["universe"]
    assert "groups" not in payload["universe"]
    assert payload["universe"]["creature_kind_settings"] == [
        {
            "creature_kind_id": "human",
            "habitat_location_ids": [],
            "period_ids": ["period"],
        }
    ]
    assert "language_ids" not in payload["universe"]
    assert payload["universe"]["group_settings"] == []


def test_shared_equipment_is_expanded_into_the_world_item_snapshot() -> None:
    draft = _minimal_foundation()
    cloak = EquipmentDraft(
        id="cloak",
        name="Плащ",
        description="Дорожный плащ",
        category="clothing",
        equipment_slot="torso",
        section_id="medieval",
    )
    draft.equipment = [cloak]
    catalogs = _shared_catalogs(draft)
    catalogs.equipment = [cloak]

    payload = publication_payload(draft, catalogs)

    assert "equipment" not in payload["universe"]
    assert payload["universe"]["items"][0]["id"] == "cloak"
    assert "section_id" not in payload["universe"]["items"][0]


def test_world_uses_main_catalog_and_keeps_explicit_cross_catalog_loadouts() -> None:
    draft = _minimal_foundation()
    draft.item_catalog_section_id = "Narutov4"
    draft.periods[0].starting_kits[0].items = [StartingKitItemDraft("traveler-map", 1)]
    draft.characters = [
        CharacterDraft(
            id="ino",
            name="Ино",
            creature_kind_id="human",
            starting_currency_amount=345,
            items=[StartingKitItemDraft("shinobi-jacket", 1)],
        )
    ]
    catalogs = _shared_catalogs(draft)
    catalogs.equipment_sections = [
        EquipmentSectionDraft("Narutov4", "Наруто"),
        EquipmentSectionDraft("common", "Общие вещи"),
        EquipmentSectionDraft("unused", "Неиспользуемое"),
    ]
    catalogs.equipment = [
        EquipmentDraft(
            id="shinobi-jacket",
            name="Куртка шиноби",
            description="Повседневная форма.",
            category="clothing",
            equipment_slot="torso",
            section_id="Narutov4",
        ),
        EquipmentDraft(
            id="traveler-map",
            name="Карта путника",
            description="Общая дорожная карта.",
            category="common",
            section_id="common",
        ),
        EquipmentDraft(
            id="laser",
            name="Лазер",
            description="Предмет другого сеттинга.",
            category="weapon",
            equipment_slot="active_weapon",
            section_id="unused",
        ),
    ]

    universe = publication_payload(draft, catalogs)["universe"]

    assert universe["item_catalog_section_id"] == "Narutov4"
    assert {item["id"] for item in universe["items"]} == {
        "shinobi-jacket",
        "traveler-map",
    }
    assert universe["characters"][0]["starting_currency_amount"] == 345
    assert universe["characters"][0]["items"] == [{"item_id": "shinobi-jacket", "quantity": 1}]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda draft: setattr(draft, "id", "Bad ID"), "ID вселенной"),
        (lambda draft: draft.periods.clear(), "хотя бы один период"),
        (lambda draft: draft.creature_kinds.clear(), "вид или расу"),
        (lambda draft: draft.periods[0].starting_location_ids.clear(), "стартовой локации"),
        (lambda draft: draft.periods[0].starting_kits.pop(), "от одного до десяти"),
    ],
)
def test_incomplete_foundation_cannot_be_published(change, message) -> None:
    draft = _minimal_foundation()
    change(draft)

    with pytest.raises(InvalidFoundation, match=message):
        validate_foundation(draft)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("biography", "Б" * 351, "Биография персонажа"),
        ("profession", "П" * 31, "Профессия персонажа"),
    ],
)
def test_character_profile_text_limits_are_enforced(field, value, message) -> None:
    draft = _minimal_foundation()
    character = CharacterDraft(creature_kind_id="human")
    setattr(character, field, value)
    draft.characters = [character]

    with pytest.raises(InvalidFoundation, match=message):
        validate_foundation(draft)


def test_duplicate_period_ids_are_rejected() -> None:
    draft = _minimal_foundation()
    draft.periods = [PeriodDraft(id="same"), PeriodDraft(id="same")]

    with pytest.raises(InvalidFoundation, match="не должны повторяться"):
        validate_foundation(draft)


def test_draft_round_trip_preserves_nested_values(tmp_path) -> None:
    draft = UniverseDraft()
    draft.locations[0].price_coefficient = 1.5
    draft.periods[0].starting_kits[0].starting_currency_amount = 25
    path = save_draft(draft, tmp_path / "world.draft.json")

    loaded = load_draft(path, GlobalCatalogDraft())

    assert loaded.to_mapping() == draft.to_mapping()


def test_legacy_draft_locations_are_migrated_to_independent_catalog(tmp_path) -> None:
    path = tmp_path / "old.draft.json"
    payload = {
        "draft_version": 1,
        "universe": UniverseDraft().to_mapping(),
    }
    period = payload["universe"]["periods"][0]
    period.pop("location_ids")
    period.pop("starting_location_ids")
    period.pop("location_connections")
    period["starting_locations"] = [
        {
            "id": "start",
            "name": "Старая локация",
            "description": "Описание",
            "is_starting": True,
            "connected_location_ids": [],
        }
    ]
    payload["universe"].pop("locations")
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    restored = load_draft(path, GlobalCatalogDraft())

    assert restored.locations[0].name == "Старая локация"
    assert restored.periods[0].starting_location_ids == ["start"]


def test_publication_is_local_immutable_json(tmp_path) -> None:
    draft = _minimal_foundation()
    draft.id = "naruto"
    catalogs = _shared_catalogs(draft)
    path = publish_foundation(draft, catalogs, tmp_path)

    assert path.name == "naruto.world.json"
    assert json.loads(path.read_text(encoding="utf-8"))["universe"]["id"] == "naruto"
    with pytest.raises(FileExistsError):
        publish_foundation(draft, catalogs, tmp_path)


def test_published_world_can_be_reopened_as_editable_copy(tmp_path) -> None:
    draft = _complete_foundation()
    draft.locations[0].price_coefficient = 1.35
    catalogs = _shared_catalogs(draft)
    path = publish_foundation(draft, catalogs, tmp_path)

    reopened = load_published_foundation(path, catalogs)

    assert reopened.to_mapping() == draft.to_mapping()


def test_published_world_requires_current_shared_catalog(tmp_path) -> None:
    draft = _minimal_foundation()
    catalogs = _shared_catalogs(draft)
    path = publish_foundation(draft, catalogs, tmp_path)
    catalogs.creature_kinds.clear()

    with pytest.raises(ValueError, match="human"):
        load_published_foundation(path, catalogs)


def test_draft_requires_current_shared_catalog_when_opened(tmp_path) -> None:
    draft = _minimal_foundation()
    path = save_draft(draft, tmp_path / "world.draft.json")

    with pytest.raises(ValueError, match="human"):
        load_draft(path, GlobalCatalogDraft())

    assert load_draft(path, _shared_catalogs(draft)).to_mapping() == draft.to_mapping()


def test_preview_is_readable_json() -> None:
    draft = _minimal_foundation()
    preview = preview_foundation(draft, _shared_catalogs(draft))

    assert '"artifact_type": "aniworlds.world_foundation"' in preview


def test_invalid_draft_file_is_rejected(tmp_path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"draft_version": 2}', encoding="utf-8")

    with pytest.raises(ValueError, match="черновиком"):
        load_draft(path, GlobalCatalogDraft())


def _complete_foundation() -> UniverseDraft:
    draft = _minimal_foundation()
    draft.id = "complete"
    period = draft.periods[0]
    draft.locations = [
        StartingLocationDraft(
            id="village",
            name="Деревня",
            description="Старт",
        ),
        StartingLocationDraft(
            id="forest",
            name="Лес",
            description="Окрестности",
        ),
    ]
    period.location_ids = ["village", "forest"]
    period.starting_location_ids = ["village"]
    period.location_connections = [
        PeriodConnectionDraft("village", ["forest"]),
        PeriodConnectionDraft("forest", ["village"]),
    ]
    draft.creature_kinds[0] = CreatureKindDraft(
        id="human",
        name="Человек",
        description="Обычный человек",
        physical_features=["Две руки"],
        habitat_location_ids=["village"],
    )
    draft.groups = [
        GroupDraft(
            id="guards",
            location_ids=["village"],
            period_states={"period": "Защищают деревню"},
        )
    ]
    draft.items = [ItemDraft(id="bandage", name="Бинт", allowed_shop_kinds=["general_store"])]
    draft.shop_policies = [ShopPolicyDraft()]
    period.starting_kits[0].items = [StartingKitItemDraft("bandage", 2)]
    draft.characters = [
        CharacterDraft(
            id="guard",
            origin_location_id="village",
            creature_kind_id="human",
            group_ids=["guards"],
            leader_group_ids=["guards"],
            abilities=[AbilityDraft(id="watch")],
        )
    ]
    return draft


def test_complete_catalog_validates_and_round_trips() -> None:
    draft = _complete_foundation()

    validate_foundation(draft)
    restored = universe_from_mapping(draft.to_mapping())

    assert restored.to_mapping() == draft.to_mapping()


def test_ability_name_above_runtime_limit_cannot_be_published() -> None:
    draft = _complete_foundation()
    draft.characters[0].abilities[0].name = "я" * 31

    with pytest.raises(InvalidFoundation, match=r"Название способности.*30"):
        validate_foundation(draft)


def test_character_name_above_database_limit_cannot_be_published() -> None:
    draft = _complete_foundation()
    draft.characters[0].name = "я" * 21

    with pytest.raises(InvalidFoundation, match=r"Имя персонажа.*20"):
        validate_foundation(draft)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda draft: draft.items[0].__setattr__("name", "[Бинт]"), "запрещённый"),
        (lambda draft: draft.items[0].__setattr__("base_price", -1), "Цена"),
        (
            lambda draft: draft.items[0].__setattr__("appearance_weight", 101),
            "частота появления",
        ),
        (
            lambda draft: draft.shop_policies[0].__setattr__("maximum_assortment_size", 11),
            "ассортимента",
        ),
        (lambda draft: draft.characters[0].group_ids.append("missing"), "объединение персонажа"),
        (lambda draft: draft.characters[0].__setattr__("age", 17), "возраст"),
        (lambda draft: draft.groups[0].ally_ids.append("guards"), "противоречат"),
        (
            lambda draft: draft.creature_kinds[0].habitat_location_ids.append("moon"),
            "место обитания",
        ),
        (
            lambda draft: draft.periods[0].starting_kits[0].items[0].__setattr__("quantity", 0),
            "Количество",
        ),
        (
            lambda draft: (
                draft.periods[0].location_connections[0].connected_location_ids.append("moon")
            ),
            "текущего периода",
        ),
    ],
)
def test_complete_catalog_rejects_invalid_relations(mutation, message) -> None:
    draft = _complete_foundation()
    mutation(draft)

    with pytest.raises(InvalidFoundation, match=message):
        validate_foundation(draft)
