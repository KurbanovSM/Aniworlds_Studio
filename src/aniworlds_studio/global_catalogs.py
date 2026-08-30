"""Studio-owned global catalogs reused while authoring multiple worlds."""

# ruff: noqa: RUF001

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any

from aniworlds_studio.foundation_models import (
    CreatureKindDraft,
    GroupDraft,
    LanguageDraft,
    UniverseDraft,
)
from aniworlds_studio.foundation_validation import (
    validate_shared_group,
    validate_shared_kind,
    validate_shared_language,
)

GLOBAL_CATALOG_FILE_NAME = "global-catalogs.studio.json"
GLOBAL_CATALOG_VERSION = 2
PUBLISHED_CATALOG_FILE_NAME = "global-catalogs.catalog.json"
PUBLISHED_CATALOG_SCHEMA_VERSION = 2
PUBLISHED_CATALOG_ARTIFACT_TYPE = "aniworlds.global_catalogs"
CHARACTER_TRAIT_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CHARACTER_TRAIT_ID_MAX_LENGTH = 32
CHARACTER_TRAIT_NAME_MAX_LENGTH = 30
CHARACTER_TRAIT_DESCRIPTION_MAX_LENGTH = 200


@dataclass(slots=True)
class CharacterTraitDraft:
    id: str = "trait"
    name: str = "Черта характера"
    description: str = "Описание проявления черты"
    incompatible_trait_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GlobalCatalogDraft:
    creature_kinds: list[CreatureKindDraft] = field(default_factory=list)
    languages: list[LanguageDraft] = field(default_factory=list)
    groups: list[GroupDraft] = field(default_factory=list)
    traits: list[CharacterTraitDraft] = field(default_factory=list)


def catalog_publication_payload(
    catalogs: GlobalCatalogDraft,
    *,
    published_at: datetime | None = None,
) -> dict[str, Any]:
    """Build the future server catalog without world-owned relationships."""
    validate_global_catalogs(catalogs)
    timestamp = published_at or datetime.now(UTC)
    return {
        "schema_version": PUBLISHED_CATALOG_SCHEMA_VERSION,
        "artifact_type": PUBLISHED_CATALOG_ARTIFACT_TYPE,
        "published_at": timestamp.isoformat(),
        "catalogs": {
            "creature_kinds": [
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "category": item.category,
                    "cognition": item.cognition,
                    "communication_modes": item.communication_modes,
                    "physical_features": item.physical_features,
                    "parent_kind_id": item.parent_kind_id,
                }
                for item in catalogs.creature_kinds
            ],
            "languages": [asdict(item) for item in catalogs.languages],
            "groups": [
                {
                    "id": item.id,
                    "name": item.name,
                    "group_type": item.group_type,
                    "description": item.description,
                }
                for item in catalogs.groups
            ],
            "traits": [asdict(item) for item in catalogs.traits],
        },
    }


def validate_global_catalogs(catalogs: GlobalCatalogDraft) -> None:
    """Reject incomplete or ambiguous shared records before publication."""
    for label, entries in (
        ("видов и рас", catalogs.creature_kinds),
        ("языков", catalogs.languages),
        ("объединений", catalogs.groups),
        ("черт характера", catalogs.traits),
    ):
        identifiers = [item.id.strip() for item in entries]
        if any(not identifier for identifier in identifiers):
            raise ValueError(f"В каталоге {label} есть запись без ID.")
        if any(not _valid_shared_id(identifier) for identifier in identifiers):
            raise ValueError(
                f"ID в каталоге {label}: используйте строчные буквы, цифры и одиночный дефис."
            )
        if len(identifiers) != len(set(identifiers)):
            raise ValueError(f"ID в каталоге {label} не должны повторяться.")
        if any(not item.name.strip() for item in entries):
            raise ValueError(f"В каталоге {label} есть запись без названия.")
    kind_ids = {item.id for item in catalogs.creature_kinds}
    for kind in catalogs.creature_kinds:
        validate_shared_kind(kind)
        if kind.parent_kind_id is not None and kind.parent_kind_id not in kind_ids:
            raise ValueError(
                f"Родительский вид {kind.parent_kind_id!r} отсутствует в общем каталоге."
            )
    for language in catalogs.languages:
        validate_shared_language(language)
    for group in catalogs.groups:
        validate_shared_group(group)
    _validate_traits(catalogs.traits)


def _validate_traits(traits: list[CharacterTraitDraft]) -> None:
    trait_ids = {item.id for item in traits}
    by_id = {item.id: item for item in traits}
    for trait in traits:
        if (
            len(trait.id) > CHARACTER_TRAIT_ID_MAX_LENGTH
            or CHARACTER_TRAIT_ID_PATTERN.fullmatch(trait.id) is None
        ):
            raise ValueError(
                "ID черты: не более 32 символов, только строчные латинские "
                "буквы, цифры и одиночный дефис."
            )
        if len(trait.name) > CHARACTER_TRAIT_NAME_MAX_LENGTH:
            raise ValueError("Название черты не должно превышать 30 символов.")
        if not trait.description.strip():
            raise ValueError(f"У черты «{trait.name}» нет описания.")
        if len(trait.description) > CHARACTER_TRAIT_DESCRIPTION_MAX_LENGTH:
            raise ValueError("Описание черты не должно превышать 200 символов.")
        incompatible = set(trait.incompatible_trait_ids)
        if trait.id in incompatible:
            raise ValueError(f"Черта «{trait.name}» несовместима сама с собой.")
        missing = sorted(incompatible - trait_ids)
        if missing:
            raise ValueError(
                f"Черта «{trait.name}» ссылается на отсутствующие черты: "
                f"{', '.join(missing)}."
            )
        if len(incompatible) != len(trait.incompatible_trait_ids):
            raise ValueError(f"Несовместимые черты для «{trait.name}» повторяются.")
        for other_id in incompatible:
            if trait.id not in by_id[other_id].incompatible_trait_ids:
                raise ValueError(
                    f"Несовместимость «{trait.name}» и «{by_id[other_id].name}» "
                    "должна быть взаимной."
                )


def _valid_shared_id(value: str) -> bool:
    return bool(
        value
        and value == value.lower()
        and not value.startswith("-")
        and not value.endswith("-")
        and "--" not in value
        and all(character.isalnum() or character == "-" for character in value)
    )


def validate_world_catalog_references(
    draft: UniverseDraft,
    catalogs: GlobalCatalogDraft,
) -> None:
    """Ensure every shared ID selected by a world still exists."""
    for label, selected, available in (
        (
            "вид или раса",
            {item.id for item in draft.creature_kinds},
            {item.id for item in catalogs.creature_kinds},
        ),
        (
            "язык",
            {item.id for item in draft.languages},
            {item.id for item in catalogs.languages},
        ),
        (
            "объединение",
            {item.id for item in draft.groups},
            {item.id for item in catalogs.groups},
        ),
        (
            "черту характера",
            {trait_id for character in draft.characters for trait_id in character.trait_ids},
            {item.id for item in catalogs.traits},
        ),
    ):
        missing = sorted(selected - available)
        if missing:
            raise ValueError(
                f"Мир ссылается на отсутствующий общий {label}: {', '.join(missing)}."
            )
    incompatible_by_id = {
        trait.id: set(trait.incompatible_trait_ids) for trait in catalogs.traits
    }
    for character in draft.characters:
        selected = set(character.trait_ids)
        if any(incompatible_by_id.get(trait_id, set()) & selected for trait_id in selected):
            raise ValueError(f"У персонажа «{character.name}» выбраны несовместимые черты.")


def preview_global_catalogs(catalogs: GlobalCatalogDraft) -> str:
    return json.dumps(catalog_publication_payload(catalogs), ensure_ascii=False, indent=2)


def publish_global_catalogs(catalogs: GlobalCatalogDraft, directory: Path) -> Path:
    """Create one immutable server catalog for manual Cyberduck delivery."""
    return _write_new_json(
        directory / PUBLISHED_CATALOG_FILE_NAME,
        catalog_publication_payload(catalogs),
    )


def synchronize_shared_catalogs(draft: UniverseDraft, catalogs: GlobalCatalogDraft) -> None:
    """Refresh shared fields while preserving every world's own relationships."""
    kinds = {item.id: item for item in catalogs.creature_kinds}
    for world in draft.creature_kinds:
        shared = kinds.get(world.id)
        if shared is None:
            continue
        for key in (
            "name",
            "description",
            "category",
            "cognition",
            "communication_modes",
            "physical_features",
            "parent_kind_id",
        ):
            setattr(world, key, getattr(shared, key))
    languages = {item.id: item for item in catalogs.languages}
    for world in draft.languages:
        shared = languages.get(world.id)
        if shared is not None:
            world.name = shared.name
            world.has_spoken_form = shared.has_spoken_form
            world.has_written_form = shared.has_written_form
    groups = {item.id: item for item in catalogs.groups}
    for world in draft.groups:
        shared = groups.get(world.id)
        if shared is not None:
            world.name = shared.name
            world.group_type = shared.group_type
            world.description = shared.description


def save_global_catalogs(
    catalogs: GlobalCatalogDraft,
    directory: Path,
    *,
    replace_existing: bool = False,
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / GLOBAL_CATALOG_FILE_NAME
    if path.exists() and not replace_existing:
        raise FileExistsError("Файл глобальных каталогов уже существует.")
    payload = {
        "studio_catalog_version": GLOBAL_CATALOG_VERSION,
        "creature_kinds": [asdict(item) for item in catalogs.creature_kinds],
        "languages": [asdict(item) for item in catalogs.languages],
        "groups": [asdict(item) for item in catalogs.groups],
        "traits": [asdict(item) for item in catalogs.traits],
    }
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path


def _write_new_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return path


def load_global_catalogs(path: Path) -> GlobalCatalogDraft:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Файл общих каталогов должен содержать JSON-объект.")
    if payload.get("studio_catalog_version") in {1, GLOBAL_CATALOG_VERSION}:
        catalog_values = payload
        published = False
    elif (
        payload.get("schema_version") in {1, PUBLISHED_CATALOG_SCHEMA_VERSION}
        and payload.get("artifact_type") == PUBLISHED_CATALOG_ARTIFACT_TYPE
    ):
        catalog_values = payload.get("catalogs")
        published = True
    else:
        raise ValueError("Неподдерживаемая версия глобальных каталогов Studio.")
    if not isinstance(catalog_values, dict):
        raise ValueError("Файл общих каталогов не содержит раздел catalogs.")
    try:
        catalogs = GlobalCatalogDraft(
            creature_kinds=[
                CreatureKindDraft(**item) for item in catalog_values.get("creature_kinds", [])
            ],
            languages=[LanguageDraft(**item) for item in catalog_values.get("languages", [])],
            groups=[GroupDraft(**item) for item in catalog_values.get("groups", [])],
            traits=[CharacterTraitDraft(**item) for item in catalog_values.get("traits", [])],
        )
    except (TypeError, AttributeError) as error:
        raise ValueError("Структура общих каталогов повреждена.") from error
    if published:
        validate_global_catalogs(catalogs)
    return catalogs


def load_initial_global_catalogs() -> GlobalCatalogDraft:
    """Load the editable authored default without embedding content in Python."""
    repository_copy = Path(__file__).resolve().parents[2] / "content" / GLOBAL_CATALOG_FILE_NAME
    if repository_copy.is_file():
        return load_global_catalogs(repository_copy)
    packaged = files("aniworlds_studio").joinpath("defaults", GLOBAL_CATALOG_FILE_NAME)
    with as_file(packaged) as packaged_path:
        return load_global_catalogs(packaged_path)


def replace_global_catalog_entries(
    catalogs: GlobalCatalogDraft,
    field_name: str,
    entries: list[dict[str, Any]],
) -> None:
    builders = {
        "creature_kinds": lambda item: CreatureKindDraft(**item),
        "languages": lambda item: LanguageDraft(**item),
        "groups": lambda item: GroupDraft(**item),
        "traits": lambda item: CharacterTraitDraft(**item),
    }
    try:
        builder = builders[field_name]
    except KeyError as error:
        raise ValueError(f"Неизвестный глобальный каталог: {field_name}") from error
    setattr(catalogs, field_name, [builder(item) for item in entries])
