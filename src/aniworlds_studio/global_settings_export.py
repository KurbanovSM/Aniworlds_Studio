"""Offline export of global gameplay settings consumed by the server."""

# ruff: noqa: RUF001

import json
from dataclasses import asdict, dataclass
from pathlib import Path

GLOBAL_SETTINGS_SCHEMA_VERSION = 1
GLOBAL_SETTINGS_ARTIFACT_TYPE = "aniworlds.global_gameplay_settings"
GLOBAL_SETTINGS_FILE_NAME = "global-gameplay.settings.json"


class InvalidGlobalSettings(ValueError):
    """One or more editable values cannot be published."""


@dataclass(frozen=True, slots=True)
class GlobalAbilitySettings:
    initial_ability_limit: int = 5
    learned_ability_limit: int = 10
    ability_lesson_count: int = 4

    def validate(self) -> None:
        if min(
            self.initial_ability_limit,
            self.learned_ability_limit,
            self.ability_lesson_count,
        ) <= 0:
            raise InvalidGlobalSettings("Все значения должны быть больше нуля.")


def export_global_settings(
    settings: GlobalAbilitySettings,
    directory: Path,
    *,
    replace_existing: bool = False,
) -> Path:
    """Replace the one canonical local settings file after strict validation."""
    settings.validate()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / GLOBAL_SETTINGS_FILE_NAME
    if path.exists() and not replace_existing:
        raise InvalidGlobalSettings("Файл глобальных настроек уже существует.")
    payload = {
        "schema_version": GLOBAL_SETTINGS_SCHEMA_VERSION,
        "artifact_type": GLOBAL_SETTINGS_ARTIFACT_TYPE,
        "abilities": asdict(settings),
    }
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path
