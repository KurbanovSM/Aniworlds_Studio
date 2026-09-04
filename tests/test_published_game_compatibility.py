"""Run real Studio publications through the game contracts and ORM import path."""

import asyncio
import importlib
import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

STUDIO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME_ROOT = STUDIO_ROOT.parent / "Aniworlds_AI_v3"


def _game_root() -> Path:
    return Path(os.environ.get("ANIWORLDS_AI_ROOT", DEFAULT_GAME_ROOT)).resolve()


def test_published_files_pass_the_game_import_path(tmp_path: Path) -> None:
    game_root = _game_root()
    if not (game_root / "src" / "aniworlds").is_dir():
        pytest.skip("Aniworlds_AI_v3 is supplied by the dedicated compatibility CI job")
    if importlib.util.find_spec("sqlalchemy") is None:
        pytest.skip("game dependencies are installed by the dedicated compatibility CI job")
    sys.path.insert(0, str(game_root / "src"))
    sys.path.insert(0, str(STUDIO_ROOT / "src"))

    catalog_import = importlib.import_module("aniworlds.global_catalog_import")
    world_import = importlib.import_module("aniworlds.world_foundation_import")
    shared_models = importlib.import_module("aniworlds.modules.worlds.shared_catalog_models")
    foundation_export = importlib.import_module("aniworlds_studio.foundation_export")
    global_catalogs = importlib.import_module("aniworlds_studio.global_catalogs")
    global_settings_catalog = importlib.import_module("aniworlds.global_settings_catalog")
    global_settings_export = importlib.import_module(
        "aniworlds_studio.global_settings_export"
    )

    settings_directory = tmp_path / "settings"
    global_settings_export.export_global_settings(
        global_settings_export.GlobalAbilitySettings(),
        global_settings_export.GlobalNarratorSettings(
            global_settings_export.DEFAULT_NARRATOR_SYSTEM_PROMPT
        ),
        settings_directory,
    )
    settings = global_settings_catalog.FileGlobalGameplaySettingsCatalog(settings_directory)
    assert settings.load().initial_ability_limit == 5
    assert (
        settings.load_narrator_system_prompt_template()
        == global_settings_export.DEFAULT_NARRATOR_SYSTEM_PROMPT
    )

    catalogs = global_catalogs.load_global_catalogs(
        STUDIO_ROOT / "content" / "global-catalogs.studio.json"
    )
    catalog_path = global_catalogs.publish_global_catalogs(catalogs, tmp_path / "catalogs")
    world_paths = [
        foundation_export.publish_foundation(
            foundation_export.load_draft(world_path, catalogs),
            catalogs,
            tmp_path / "worlds",
        )
        for world_path in sorted((STUDIO_ROOT / "content" / "worlds").glob("*.draft.json"))
    ]
    catalog = catalog_import.load_global_catalog_package(catalog_path)

    assert world_paths, "Studio must contain at least one publishable world draft"
    for world_path in world_paths:
        package = world_import.load_world_foundation_package(world_path)
        definitions = [
            shared_models.CharacterTraitDefinitionModel(
                id=item.id,
                name=item.name,
                description=item.description,
                display_order=position,
                published_at=catalog.published_at,
            )
            for position, item in enumerate(catalog.catalogs.traits)
        ]
        incompatibilities = [
            shared_models.CharacterTraitIncompatibilityModel(
                trait_id=item.id,
                incompatible_trait_id=other_id,
            )
            for item in catalog.catalogs.traits
            for other_id in item.incompatible_trait_ids
            if item.id < other_id
        ]
        session = MagicMock()
        session.merge = AsyncMock()
        session.flush = AsyncMock()
        session.execute = AsyncMock()
        session.scalars = AsyncMock(
            side_effect=[
                definitions,
                incompatibilities,
                [item.id for item in catalog.catalogs.creature_kinds],
                [item.id for item in catalog.catalogs.groups],
            ]
        )

        asyncio.run(catalog_import.import_global_catalog(session, catalog))
        asyncio.run(world_import.import_world_foundation(session, package))

        assert session.merge.await_count > 0
        assert session.flush.await_count > 0
