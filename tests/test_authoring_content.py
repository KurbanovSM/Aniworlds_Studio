import json
from datetime import datetime
from pathlib import Path

from aniworlds_studio.foundation_export import load_draft, publication_payload
from aniworlds_studio.global_catalogs import (
    catalog_publication_payload,
    load_global_catalogs,
    validate_world_catalog_references,
)
from aniworlds_studio.global_settings_export import GlobalAbilitySettings
from aniworlds_studio.promo_export import build_turn_promo

ROOT = Path(__file__).parents[1]
CONTENT = ROOT / "content"


def test_every_published_world_matches_an_authoring_draft() -> None:
    catalogs = load_global_catalogs(CONTENT / "global-catalogs.studio.json")
    draft_paths = sorted((CONTENT / "worlds").glob("*.draft.json"))
    drafts = {draft.id: draft for draft in (load_draft(path, catalogs) for path in draft_paths)}
    published_paths = sorted((CONTENT / "upload" / "worlds").glob("*.world.json"))

    assert published_paths
    for published_path in published_paths:
        published = json.loads(published_path.read_text(encoding="utf-8"))
        draft = drafts[published["universe"]["id"]]
        validate_world_catalog_references(draft, catalogs)
        timestamp = datetime.fromisoformat(published["published_at"])

        assert published == publication_payload(draft, catalogs, published_at=timestamp)


def test_shared_catalog_draft_matches_published_catalog() -> None:
    catalogs = load_global_catalogs(CONTENT / "global-catalogs.studio.json")
    path = CONTENT / "upload" / "catalogs" / "global-catalogs.catalog.json"
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


def test_published_global_settings_use_the_current_studio_values() -> None:
    path = CONTENT / "upload" / "settings" / "global-gameplay.settings.json"
    published = json.loads(path.read_text(encoding="utf-8"))
    settings = GlobalAbilitySettings(**published["abilities"])

    settings.validate()
    assert published["schema_version"] == 1
    assert published["artifact_type"] == "aniworlds.global_gameplay_settings"


def test_published_audit_promo_matches_the_studio_exporter() -> None:
    path = CONTENT / "upload" / "promocodes" / "ANI-TEST-AUDT.json"
    published = json.loads(path.read_text(encoding="utf-8"))
    expected = build_turn_promo(
        100,
        10,
        expires_at="2025-01-01T00:00:00Z",
        code="ANI-TEST-AUDT",
    )

    assert published == expected.document


def test_every_published_turn_promo_matches_the_studio_exporter() -> None:
    paths = sorted((CONTENT / "upload" / "promocodes").glob("*.json"))

    assert paths
    for path in paths:
        published = json.loads(path.read_text(encoding="utf-8"))
        expected = build_turn_promo(
            published["turns"],
            published["activation_limit"],
            expires_at=published["expires_at"],
            code=published["code"],
        )
        assert published == expected.document
