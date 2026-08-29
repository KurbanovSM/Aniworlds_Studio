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

ROOT = Path(__file__).parents[1]
CONTENT = ROOT / "content"


def test_every_authoring_draft_matches_its_published_server_package() -> None:
    catalogs = load_global_catalogs(CONTENT / "global-catalogs.studio.json")
    draft_paths = sorted((CONTENT / "worlds").glob("*.draft.json"))

    assert draft_paths
    for path in draft_paths:
        draft = load_draft(path)
        validate_world_catalog_references(draft, catalogs)
        published_path = CONTENT / "upload" / "worlds" / f"{draft.id}.world.json"
        published = json.loads(published_path.read_text(encoding="utf-8"))
        timestamp = datetime.fromisoformat(published["published_at"])

        assert published == publication_payload(draft, catalogs, published_at=timestamp)


def test_shared_catalog_draft_matches_published_catalog() -> None:
    catalogs = load_global_catalogs(CONTENT / "global-catalogs.studio.json")
    path = CONTENT / "upload" / "catalogs" / "global-catalogs.catalog.json"
    published = json.loads(path.read_text(encoding="utf-8"))
    timestamp = datetime.fromisoformat(published["published_at"])

    assert published == catalog_publication_payload(catalogs, published_at=timestamp)


def test_published_global_settings_use_the_current_studio_values() -> None:
    path = CONTENT / "upload" / "settings" / "global-gameplay.settings.json"
    published = json.loads(path.read_text(encoding="utf-8"))
    settings = GlobalAbilitySettings(**published["abilities"])

    settings.validate()
    assert published["schema_version"] == 1
    assert published["artifact_type"] == "aniworlds.global_gameplay_settings"
