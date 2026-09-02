import json

import pytest

from aniworlds_studio.global_settings_export import (
    GLOBAL_SETTINGS_FILE_NAME,
    GlobalAbilitySettings,
    InvalidGlobalSettings,
    export_global_settings,
)


def test_exports_strict_global_settings_file(tmp_path) -> None:
    path = export_global_settings(GlobalAbilitySettings(5, 10, 4), tmp_path)

    assert path.name == GLOBAL_SETTINGS_FILE_NAME
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "schema_version": 1,
        "artifact_type": "aniworlds.global_gameplay_settings",
        "abilities": {
            "initial_ability_limit": 5,
            "learned_ability_limit": 10,
            "ability_lesson_count": 4,
        },
    }


def test_rejects_invalid_values_and_silent_replacement(tmp_path) -> None:
    with pytest.raises(InvalidGlobalSettings):
        export_global_settings(GlobalAbilitySettings(0, 10, 4), tmp_path)

    export_global_settings(GlobalAbilitySettings(), tmp_path)
    with pytest.raises(InvalidGlobalSettings, match="уже существует"):
        export_global_settings(GlobalAbilitySettings(7, 10, 4), tmp_path)

    path = export_global_settings(
        GlobalAbilitySettings(7, 10, 4),
        tmp_path,
        replace_existing=True,
    )
    assert json.loads(path.read_text(encoding="utf-8"))["abilities"]["initial_ability_limit"] == 7
