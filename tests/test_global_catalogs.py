"""Shared-catalog serialization and reference checks."""

# ruff: noqa: RUF001

import json
from datetime import UTC, datetime

import pytest

from aniworlds_studio.foundation_models import (
    CreatureKindDraft,
    GroupDraft,
    LanguageDraft,
    UniverseDraft,
)
from aniworlds_studio.global_catalogs import (
    GLOBAL_CATALOG_FILE_NAME,
    PUBLISHED_CATALOG_FILE_NAME,
    GlobalCatalogDraft,
    catalog_publication_payload,
    load_global_catalogs,
    preview_global_catalogs,
    publish_global_catalogs,
    replace_global_catalog_entries,
    save_global_catalogs,
    synchronize_shared_catalogs,
    validate_world_catalog_references,
)


def test_new_shared_catalog_is_empty() -> None:
    catalogs = GlobalCatalogDraft()

    assert catalogs.creature_kinds == []
    assert catalogs.languages == []
    assert catalogs.groups == []


def test_shared_catalogs_round_trip_and_require_explicit_replacement(tmp_path) -> None:
    catalogs = GlobalCatalogDraft(
        creature_kinds=[CreatureKindDraft(id="human", name="Человек")],
        groups=[GroupDraft(id="guards", name="Стража")],
    )
    path = save_global_catalogs(catalogs, tmp_path)

    assert path.name == GLOBAL_CATALOG_FILE_NAME
    assert load_global_catalogs(path) == catalogs
    with pytest.raises(FileExistsError):
        save_global_catalogs(catalogs, tmp_path)
    save_global_catalogs(catalogs, tmp_path, replace_existing=True)
    assert json.loads(path.read_text(encoding="utf-8"))["studio_catalog_version"] == 1


def test_world_relations_survive_shared_base_refresh() -> None:
    shared = CreatureKindDraft(id="human", name="Обновлённый человек")
    catalogs = GlobalCatalogDraft(creature_kinds=[shared], languages=[], groups=[])
    draft = UniverseDraft()
    draft.creature_kinds = [
        CreatureKindDraft(
            id="human",
            name="Старое имя",
            habitat_location_ids=["start"],
            period_ids=["period"],
        )
    ]

    synchronize_shared_catalogs(draft, catalogs)

    assert draft.creature_kinds[0].name == "Обновлённый человек"
    assert draft.creature_kinds[0].habitat_location_ids == ["start"]


def test_server_catalog_contains_base_fields_without_world_relationships() -> None:
    catalogs = GlobalCatalogDraft(
        creature_kinds=[
            CreatureKindDraft(
                id="human",
                name="Человек",
                description="Разумный человек",
                habitat_location_ids=["village"],
                period_ids=["period"],
            )
        ],
        groups=[
            GroupDraft(
                id="guards",
                name="Стража",
                description="Охрана",
                location_ids=["village"],
                period_states={"period": "На посту"},
            )
        ],
    )

    payload = catalog_publication_payload(
        catalogs,
        published_at=datetime(2026, 8, 29, tzinfo=UTC),
    )

    assert payload["schema_version"] == 1
    assert payload["artifact_type"] == "aniworlds.global_catalogs"
    assert payload["published_at"] == "2026-08-29T00:00:00+00:00"
    kind = payload["catalogs"]["creature_kinds"][0]
    group = payload["catalogs"]["groups"][0]
    assert "period_ids" not in kind
    assert "habitat_location_ids" not in kind
    assert "location_ids" not in group
    assert "period_states" not in group


def test_server_catalog_publication_is_immutable(tmp_path) -> None:
    catalogs = GlobalCatalogDraft(
        creature_kinds=[
            CreatureKindDraft(id="human", name="Человек", description="Описание")
        ]
    )

    path = publish_global_catalogs(catalogs, tmp_path)

    assert path.name == PUBLISHED_CATALOG_FILE_NAME
    assert json.loads(path.read_text(encoding="utf-8"))["catalogs"]["languages"] == []
    with pytest.raises(FileExistsError):
        publish_global_catalogs(catalogs, tmp_path)


def test_server_catalog_rejects_missing_parent_kind() -> None:
    catalogs = GlobalCatalogDraft(
        creature_kinds=[
            CreatureKindDraft(
                id="elf",
                name="Эльф",
                description="Описание",
                parent_kind_id="missing",
            )
        ]
    )

    with pytest.raises(ValueError, match="Родительский вид"):
        catalog_publication_payload(catalogs)


def test_world_rejects_reference_missing_from_shared_catalog() -> None:
    draft = UniverseDraft()
    draft.creature_kinds = [CreatureKindDraft(id="human", name="Человек")]
    catalogs = GlobalCatalogDraft(creature_kinds=[], languages=draft.languages, groups=[])

    with pytest.raises(ValueError, match="human"):
        validate_world_catalog_references(draft, catalogs)


def test_catalog_preview_and_entry_replacement_use_public_contract() -> None:
    catalogs = GlobalCatalogDraft()

    replace_global_catalog_entries(
        catalogs,
        "languages",
        [{"id": "common", "name": "Общий", "has_spoken_form": True}],
    )

    assert catalogs.languages == [LanguageDraft(id="common", name="Общий")]
    assert json.loads(preview_global_catalogs(catalogs))["catalogs"]["languages"][0][
        "id"
    ] == "common"


def test_unknown_catalog_field_is_rejected() -> None:
    with pytest.raises(ValueError, match="Неизвестный глобальный каталог"):
        replace_global_catalog_entries(GlobalCatalogDraft(), "unknown", [])


def test_unsupported_studio_catalog_version_is_rejected(tmp_path) -> None:
    path = tmp_path / GLOBAL_CATALOG_FILE_NAME
    path.write_text('{"studio_catalog_version": 999}', encoding="utf-8")

    with pytest.raises(ValueError, match="Неподдерживаемая версия"):
        load_global_catalogs(path)
