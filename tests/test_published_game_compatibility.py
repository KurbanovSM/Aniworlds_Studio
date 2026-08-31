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
DEFAULT_GAME_ROOT = STUDIO_ROOT.parent / "Aniworlds_AI"


def _game_root() -> Path:
    return Path(os.environ.get("ANIWORLDS_AI_ROOT", DEFAULT_GAME_ROOT)).resolve()


def test_published_files_pass_the_game_import_path() -> None:
    game_root = _game_root()
    if not (game_root / "src" / "aniworlds").is_dir():
        pytest.skip("Aniworlds_AI is supplied by the dedicated compatibility CI job")
    if importlib.util.find_spec("sqlalchemy") is None:
        pytest.skip("game dependencies are installed by the dedicated compatibility CI job")
    sys.path.insert(0, str(game_root / "src"))

    catalog_import = importlib.import_module("aniworlds.global_catalog_import")
    world_import = importlib.import_module("aniworlds.world_foundation_import")
    shared_models = importlib.import_module(
        "aniworlds.modules.worlds.shared_catalog_models"
    )

    catalog_path = (
        STUDIO_ROOT / "content" / "upload" / "catalogs" / "global-catalogs.catalog.json"
    )
    world_paths = sorted((STUDIO_ROOT / "content" / "upload" / "worlds").glob("*.world.json"))
    catalog = catalog_import.load_global_catalog_package(catalog_path)
    release = world_import.load_world_foundation_package(
        STUDIO_ROOT / "content/releases/npc-generation/naruto-shinobi-world-v2.world.json"
    )

    assert world_paths, "Studio must publish at least one world contract fixture"
    assert len(release.universe.npc_generation_rules) == 8
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
                [item.id for item in catalog.catalogs.languages],
                [item.id for item in catalog.catalogs.groups],
            ]
        )

        asyncio.run(catalog_import.import_global_catalog(session, catalog))
        asyncio.run(world_import.import_world_foundation(session, package))

        assert session.merge.await_count > 0
        assert session.flush.await_count > 0
