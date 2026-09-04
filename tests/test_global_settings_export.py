import json

import pytest

from aniworlds_studio.global_settings_export import (
    DEFAULT_NARRATOR_SYSTEM_PROMPT,
    GLOBAL_SETTINGS_FILE_NAME,
    GlobalAbilitySettings,
    GlobalNarratorSettings,
    InvalidGlobalSettings,
    export_global_settings,
)


def test_exports_strict_global_settings_file(tmp_path) -> None:
    path = export_global_settings(
        GlobalAbilitySettings(5, 10, 4),
        GlobalNarratorSettings(DEFAULT_NARRATOR_SYSTEM_PROMPT),
        tmp_path,
    )

    assert path.name == GLOBAL_SETTINGS_FILE_NAME
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "schema_version": 2,
        "artifact_type": "aniworlds.global_gameplay_settings",
        "abilities": {
            "initial_ability_limit": 5,
            "learned_ability_limit": 10,
            "ability_lesson_count": 4,
        },
        "narrator": {"system_prompt_template": DEFAULT_NARRATOR_SYSTEM_PROMPT},
    }


def test_rejects_invalid_values_and_silent_replacement(tmp_path) -> None:
    with pytest.raises(InvalidGlobalSettings):
        export_global_settings(
            GlobalAbilitySettings(0, 10, 4),
            GlobalNarratorSettings(DEFAULT_NARRATOR_SYSTEM_PROMPT),
            tmp_path,
        )

    narrator = GlobalNarratorSettings(DEFAULT_NARRATOR_SYSTEM_PROMPT)
    export_global_settings(GlobalAbilitySettings(), narrator, tmp_path)
    with pytest.raises(InvalidGlobalSettings, match="уже существует"):
        export_global_settings(GlobalAbilitySettings(7, 10, 4), narrator, tmp_path)

    path = export_global_settings(
        GlobalAbilitySettings(7, 10, 4),
        narrator,
        tmp_path,
        replace_existing=True,
    )
    assert json.loads(path.read_text(encoding="utf-8"))["abilities"]["initial_ability_limit"] == 7


def test_rejects_a_narrator_prompt_with_missing_or_unknown_placeholders(tmp_path) -> None:
    with pytest.raises(InvalidGlobalSettings, match="переменные"):
        export_global_settings(
            GlobalAbilitySettings(),
            GlobalNarratorSettings("Только {current_scene} и {unknown}"),
            tmp_path,
        )


@pytest.mark.parametrize("prompt", ("{period_lore", "{period_lore!r}"))
def test_rejects_malformed_or_formatted_narrator_placeholders(tmp_path, prompt) -> None:
    with pytest.raises(InvalidGlobalSettings):
        GlobalNarratorSettings(prompt).validate()
