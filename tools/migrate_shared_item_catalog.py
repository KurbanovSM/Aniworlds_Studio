"""Move Naruto v4 item authoring into the shared catalog and republish artifacts."""

from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from aniworlds_studio.foundation_export import load_draft, publish_foundation, save_draft
from aniworlds_studio.foundation_models import EquipmentDraft
from aniworlds_studio.global_catalogs import (
    load_global_catalogs,
    publish_global_catalogs,
    save_global_catalogs,
)

ROOT = Path(__file__).resolve().parents[1]
SECTION_ID = "Narutov4"


def main() -> None:
    catalog_path = ROOT / "content/global-catalogs.studio.json"
    world_path = ROOT / "content/worlds/naruto-v4.draft.json"
    catalogs = load_global_catalogs(catalog_path)
    draft = load_draft(world_path, catalogs)

    by_id = {item.id: item for item in catalogs.equipment}
    for item in (*draft.items, *draft.equipment):
        data = asdict(item)
        data["section_id"] = SECTION_ID
        shared = EquipmentDraft(**data)
        previous = by_id.get(shared.id)
        if previous is not None and asdict(previous) != asdict(shared):
            raise ValueError(f"shared item conflicts with Naruto v4: {shared.id}")
        by_id[shared.id] = shared
    catalogs.equipment[:] = sorted(by_id.values(), key=lambda item: (item.section_id, item.id))
    draft.item_catalog_section_id = SECTION_ID
    draft.items.clear()
    draft.equipment.clear()

    with TemporaryDirectory(dir=ROOT) as temporary_name:
        temporary = Path(temporary_name)
        saved_catalog = save_global_catalogs(catalogs, temporary)
        published_catalog = publish_global_catalogs(catalogs, temporary)
        saved_world = save_draft(draft, temporary / "naruto-v4.draft.json")
        published_world = publish_foundation(draft, catalogs, temporary)
        saved_catalog.replace(catalog_path)
        published_catalog.replace(ROOT / "content/upload/catalogs/global-catalogs.catalog.json")
        saved_world.replace(world_path)
        published_world.replace(ROOT / "content/upload/worlds/naruto-shinobi-world-v4.world.json")


if __name__ == "__main__":
    main()
