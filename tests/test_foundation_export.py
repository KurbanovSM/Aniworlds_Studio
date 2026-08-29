# ruff: noqa: RUF001

import json
from datetime import UTC, datetime

import pytest

from aniworlds_studio.foundation_export import (
    load_draft,
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
    GroupDraft,
    ItemDraft,
    PeriodDraft,
    ShopPolicyDraft,
    StartingKitItemDraft,
    StartingLocationDraft,
    UniverseDraft,
)
from aniworlds_studio.foundation_validation import InvalidFoundation, validate_foundation


def test_default_foundation_is_minimally_publishable() -> None:
    draft = UniverseDraft()

    validate_foundation(draft)

    payload = publication_payload(draft, published_at=datetime(2026, 8, 29, tzinfo=UTC))
    assert payload["schema_version"] == 2
    assert payload["artifact_type"] == "aniworlds.world_foundation"
    assert payload["published_at"] == "2026-08-29T00:00:00+00:00"
    assert len(payload["universe"]["periods"][0]["starting_kits"]) == 3


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda draft: setattr(draft, "id", "Bad ID"), "ID вселенной"),
        (lambda draft: draft.periods.clear(), "хотя бы один период"),
        (lambda draft: draft.creature_kinds.clear(), "вид или расу"),
        (lambda draft: draft.languages.clear(), "один язык"),
        (lambda draft: draft.periods[0].starting_locations.clear(), "стартовой локации"),
        (lambda draft: draft.periods[0].starting_kits.pop(), "ровно три"),
    ],
)
def test_incomplete_foundation_cannot_be_published(change, message) -> None:
    draft = UniverseDraft()
    change(draft)

    with pytest.raises(InvalidFoundation, match=message):
        validate_foundation(draft)


def test_duplicate_period_ids_are_rejected() -> None:
    draft = UniverseDraft(periods=[PeriodDraft(id="same"), PeriodDraft(id="same")])

    with pytest.raises(InvalidFoundation, match="не должны повторяться"):
        validate_foundation(draft)


def test_draft_round_trip_preserves_nested_values(tmp_path) -> None:
    draft = UniverseDraft()
    draft.periods[0].starting_kits[0].starting_currency_amount = 25
    path = save_draft(draft, tmp_path / "world.draft.json")

    loaded = load_draft(path)

    assert loaded.to_mapping() == draft.to_mapping()


def test_publication_is_local_immutable_json(tmp_path) -> None:
    draft = UniverseDraft(id="naruto")
    path = publish_foundation(draft, tmp_path)

    assert path.name == "naruto.world.json"
    assert json.loads(path.read_text(encoding="utf-8"))["universe"]["id"] == "naruto"
    with pytest.raises(FileExistsError):
        publish_foundation(draft, tmp_path)


def test_preview_is_readable_json() -> None:
    preview = preview_foundation(UniverseDraft())

    assert '"artifact_type": "aniworlds.world_foundation"' in preview


def test_invalid_draft_file_is_rejected(tmp_path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"draft_version": 2}', encoding="utf-8")

    with pytest.raises(ValueError, match="черновиком"):
        load_draft(path)


def _complete_foundation() -> UniverseDraft:
    draft = UniverseDraft(id="complete")
    period = draft.periods[0]
    period.starting_locations = [
        StartingLocationDraft(
            id="village",
            name="Деревня",
            description="Старт",
            connected_location_ids=["forest"],
        ),
        StartingLocationDraft(
            id="forest",
            name="Лес",
            description="Окрестности",
            is_starting=False,
            connected_location_ids=["village"],
        ),
    ]
    draft.languages[0].id = "common"
    draft.creature_kinds[0] = CreatureKindDraft(
        id="human",
        default_languages=[{"language_id": "common", "progress_units": 40}],
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
    draft.items = [
        ItemDraft(id="bandage", name="Бинт", allowed_shop_kinds=["general_store"])
    ]
    draft.shop_policies = [ShopPolicyDraft()]
    period.starting_kits[0].items = [StartingKitItemDraft("bandage", 2)]
    draft.characters = [
        CharacterDraft(
            id="guard",
            origin_location_id="village",
            group_ids=["guards"],
            leader_group_ids=["guards"],
            language_knowledge=[{"language_id": "common", "progress_units": 40}],
            abilities=[AbilityDraft(id="watch")],
        )
    ]
    return draft


def test_complete_catalog_validates_and_round_trips() -> None:
    draft = _complete_foundation()

    validate_foundation(draft)
    restored = universe_from_mapping(draft.to_mapping())

    assert restored.to_mapping() == draft.to_mapping()


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda draft: draft.items[0].__setattr__("name", "[Бинт]"), "запрещённый"),
        (lambda draft: draft.items[0].__setattr__("base_price", -1), "Цена"),
        (
            lambda draft: draft.shop_policies[0].__setattr__(
                "maximum_assortment_size", 11
            ),
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
            lambda draft: draft.periods[0].starting_kits[0].items[0].__setattr__(
                "quantity", 0
            ),
            "Количество",
        ),
    ],
)
def test_complete_catalog_rejects_invalid_relations(mutation, message) -> None:
    draft = _complete_foundation()
    mutation(draft)

    with pytest.raises(InvalidFoundation, match=message):
        validate_foundation(draft)
