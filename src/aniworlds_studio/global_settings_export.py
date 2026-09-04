"""Offline export of global gameplay settings consumed by the server."""

# ruff: noqa: RUF001

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from string import Formatter
from typing import Final

GLOBAL_SETTINGS_SCHEMA_VERSION = 2
GLOBAL_SETTINGS_ARTIFACT_TYPE = "aniworlds.global_gameplay_settings"
GLOBAL_SETTINGS_FILE_NAME = "global-gameplay.settings.json"
NARRATOR_PROMPT_FIELDS: Final = frozenset(
    {
        "period_lore",
        "world_rules",
        "power_systems",
        "current_scene",
        "character_name",
        "character_biography",
        "character_profession",
    }
)
DEFAULT_NARRATOR_SYSTEM_PROMPT: Final = "\n".join(
    (
        "Ты рассказчик интерактивной истории. Отвечай художественным текстом на русском языке.",
        "Не упоминай приложение, модель, промпт или технические инструкции.",
        "Не выбирай действия за персонажа игрока.",
        "Продолжай сцену последовательно, используя только переданный контекст.",
        "Сервер пока не применяет игровые последствия автоматически; не выводи JSON-команды.",
        "Лор периода: {period_lore}",
        "Правила мира от автора: {world_rules}",
        "Системы сил мира: {power_systems}",
        "Текущая сцена: {current_scene}",
        "Персонаж игрока: {character_name}.",
        "Биография: {character_biography}",
        "Профессия: {character_profession}",
    )
)


class InvalidGlobalSettings(ValueError):
    """One or more editable values cannot be published."""


@dataclass(frozen=True, slots=True)
class GlobalAbilitySettings:
    initial_ability_limit: int = 5
    learned_ability_limit: int = 10
    ability_lesson_count: int = 4

    def validate(self) -> None:
        if (
            min(
                self.initial_ability_limit,
                self.learned_ability_limit,
                self.ability_lesson_count,
            )
            <= 0
        ):
            raise InvalidGlobalSettings("Все значения должны быть больше нуля.")


@dataclass(frozen=True, slots=True)
class GlobalNarratorSettings:
    system_prompt_template: str

    def validate(self) -> None:
        normalized = self.system_prompt_template.strip()
        if not normalized:
            raise InvalidGlobalSettings("Системный промпт рассказчика не может быть пустым.")
        try:
            parsed = tuple(Formatter().parse(normalized))
        except ValueError as error:
            raise InvalidGlobalSettings("Шаблон системного промпта повреждён.") from error
        if any(format_spec or conversion for _, _, format_spec, conversion in parsed):
            raise InvalidGlobalSettings("Форматирование переменных промпта не поддерживается.")
        fields = {field_name for _, field_name, _, _ in parsed if field_name is not None}
        if fields != NARRATOR_PROMPT_FIELDS:
            raise InvalidGlobalSettings(
                "Промпт должен содержать все разрешённые переменные контекста."
            )


def export_global_settings(
    abilities: GlobalAbilitySettings,
    narrator: GlobalNarratorSettings,
    directory: Path,
    *,
    replace_existing: bool = False,
) -> Path:
    """Replace the one canonical local settings file after strict validation."""
    abilities.validate()
    narrator.validate()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / GLOBAL_SETTINGS_FILE_NAME
    if path.exists() and not replace_existing:
        raise InvalidGlobalSettings("Файл глобальных настроек уже существует.")
    payload = {
        "schema_version": GLOBAL_SETTINGS_SCHEMA_VERSION,
        "artifact_type": GLOBAL_SETTINGS_ARTIFACT_TYPE,
        "abilities": asdict(abilities),
        "narrator": {
            "system_prompt_template": narrator.system_prompt_template.strip(),
        },
    }
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path
