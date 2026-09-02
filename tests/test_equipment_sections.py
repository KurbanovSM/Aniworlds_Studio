"""Pure behavior behind the two-level equipment section editor."""

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

import aniworlds_studio.equipment_sections_editor as module
from aniworlds_studio.equipment_sections_editor import (
    EquipmentSectionsEditor,
    delete_equipment_section,
    rename_equipment_section,
    replace_section_equipment,
)
from aniworlds_studio.foundation_models import EquipmentDraft, EquipmentSectionDraft
from aniworlds_studio.global_catalogs import GlobalCatalogDraft


def _item(identifier: str, section_id: str) -> EquipmentDraft:
    return EquipmentDraft(
        id=identifier,
        name=identifier,
        description="Описание",
        category="clothing",
        equipment_slot="torso",
        section_id=section_id,
    )


def test_replacing_open_section_does_not_touch_another_world_section() -> None:
    catalogs = GlobalCatalogDraft(equipment=[_item("old", "Narutov4"), _item("robe", "Fantasy")])

    replace_section_equipment(
        catalogs,
        "Narutov4",
        [
            {
                "id": "jacket",
                "name": "Куртка",
                "description": "Описание",
                "category": "clothing",
                "equipment_slot": "torso",
            }
        ],
    )

    assert [(item.id, item.section_id) for item in catalogs.equipment] == [
        ("robe", "Fantasy"),
        ("jacket", "Narutov4"),
    ]


def test_renaming_section_moves_all_of_its_cards() -> None:
    catalogs = GlobalCatalogDraft(
        equipment_sections=[EquipmentSectionDraft("Narutov4", "Наруто")],
        equipment=[_item("kunai", "Narutov4")],
    )

    rename_equipment_section(
        catalogs,
        "Narutov4",
        EquipmentSectionDraft("Naruto", "Мир Наруто"),
    )

    assert catalogs.equipment_sections == [EquipmentSectionDraft("Naruto", "Мир Наруто")]
    assert catalogs.equipment[0].section_id == "Naruto"


def test_confirmed_section_deletion_removes_only_its_cards() -> None:
    catalogs = GlobalCatalogDraft(
        equipment_sections=[
            EquipmentSectionDraft("Narutov4", "Наруто"),
            EquipmentSectionDraft("Fantasy", "Фэнтези"),
        ],
        equipment=[_item("kunai", "Narutov4"), _item("robe", "Fantasy")],
    )

    delete_equipment_section(catalogs, "Narutov4")

    assert catalogs.equipment_sections == [EquipmentSectionDraft("Fantasy", "Фэнтези")]
    assert [(item.id, item.section_id) for item in catalogs.equipment] == [("robe", "Fantasy")]


def _editor(catalogs: GlobalCatalogDraft) -> Any:
    editor = cast(Any, object.__new__(EquipmentSectionsEditor))
    editor._get_catalogs = lambda: catalogs
    editor._on_changed = Mock()
    editor.refresh = Mock()
    editor.wait_window = Mock()
    return editor


def _dialog(monkeypatch, result) -> None:
    monkeypatch.setattr(
        module,
        "CardFormDialog",
        lambda *_args, **_kwargs: SimpleNamespace(result=result),
    )


def test_editor_creates_edits_and_deletes_a_catalog(monkeypatch) -> None:
    catalogs = GlobalCatalogDraft()
    editor = _editor(catalogs)
    _dialog(monkeypatch, {"id": "Narutov4", "name": "Наруто"})

    editor._new()

    assert catalogs.equipment_sections == [EquipmentSectionDraft("Narutov4", "Наруто")]
    editor.refresh.assert_called_once()
    editor._on_changed.assert_called_once()

    editor.refresh.reset_mock()
    editor._on_changed.reset_mock()
    _dialog(monkeypatch, {"id": "Naruto", "name": "Мир Наруто"})
    editor._edit("Narutov4")
    assert catalogs.equipment_sections == [EquipmentSectionDraft("Naruto", "Мир Наруто")]

    catalogs.equipment.append(_item("kunai", "Naruto"))
    monkeypatch.setattr(module.messagebox, "askyesno", Mock(return_value=True))
    editor._delete("Naruto")
    assert catalogs.equipment_sections == []
    assert catalogs.equipment == []


def test_editor_rejects_blank_and_duplicate_catalogs(monkeypatch) -> None:
    catalogs = GlobalCatalogDraft(
        equipment_sections=[EquipmentSectionDraft("Narutov4", "Наруто")]
    )
    editor = _editor(catalogs)
    showerror = Mock()
    monkeypatch.setattr(module.messagebox, "showerror", showerror)

    _dialog(monkeypatch, {"id": " ", "name": " "})
    editor._new()
    _dialog(monkeypatch, {"id": "Narutov4", "name": "Дубликат"})
    editor._new()

    assert showerror.call_count == 2
    assert catalogs.equipment_sections == [EquipmentSectionDraft("Narutov4", "Наруто")]
    editor.refresh.assert_not_called()


def test_editor_cancellation_and_delete_decline_do_not_change_catalog(monkeypatch) -> None:
    catalogs = GlobalCatalogDraft(
        equipment_sections=[EquipmentSectionDraft("Narutov4", "Наруто")]
    )
    editor = _editor(catalogs)
    _dialog(monkeypatch, None)
    editor._new()
    editor._edit("Narutov4")
    monkeypatch.setattr(module.messagebox, "askyesno", Mock(return_value=False))
    editor._delete("Narutov4")

    assert catalogs.equipment_sections == [EquipmentSectionDraft("Narutov4", "Наруто")]
    editor._on_changed.assert_not_called()


def test_editor_reports_blank_or_duplicate_rename(monkeypatch) -> None:
    catalogs = GlobalCatalogDraft(
        equipment_sections=[
            EquipmentSectionDraft("Narutov4", "Наруто"),
            EquipmentSectionDraft("Fantasy", "Фэнтези"),
        ]
    )
    editor = _editor(catalogs)
    showerror = Mock()
    monkeypatch.setattr(module.messagebox, "showerror", showerror)

    _dialog(monkeypatch, {"id": "", "name": ""})
    editor._edit("Narutov4")
    _dialog(monkeypatch, {"id": "Fantasy", "name": "Конфликт"})
    editor._edit("Narutov4")

    assert showerror.call_count == 2
    editor._on_changed.assert_not_called()


class _Widget:
    def __init__(self, *_args, **_kwargs) -> None:
        self.destroyed = False
        self.packed = []

    def pack(self, *args, **kwargs) -> None:
        self.packed.append((args, kwargs))

    def pack_forget(self) -> None:
        self.packed.append(("forgotten", {}))

    def destroy(self) -> None:
        self.destroyed = True

    def bind(self, *_args, **_kwargs) -> None:
        return None


def test_open_section_scopes_catalog_editor_and_close_restores_list(monkeypatch) -> None:
    catalogs = GlobalCatalogDraft(
        equipment_sections=[EquipmentSectionDraft("Narutov4", "Наруто")],
        equipment=[_item("kunai", "Narutov4"), _item("robe", "Fantasy")],
    )
    editor = _editor(catalogs)
    editor._list_view = _Widget()
    editor._detail = _Widget()
    captured = {}

    monkeypatch.setattr(module.ttk, "Frame", _Widget)
    monkeypatch.setattr(module.ttk, "Button", _Widget)
    monkeypatch.setattr(module.ttk, "Label", _Widget)

    class FakeCatalogEditor(_Widget):
        def __init__(self, *_args, **kwargs) -> None:
            super().__init__()
            captured.update(kwargs)

    monkeypatch.setattr(module, "CatalogEditor", FakeCatalogEditor)

    editor._open_section("Narutov4")
    assert [item.id for item in captured["get_draft"]().equipment] == ["kunai"]
    captured["replace_entries"](
        None,
        "equipment",
        [
            {
                "id": "jacket",
                "name": "Куртка",
                "description": "Описание",
                "category": "clothing",
                "equipment_slot": "torso",
            }
        ],
    )
    assert [(item.id, item.section_id) for item in catalogs.equipment] == [
        ("robe", "Fantasy"),
        ("jacket", "Narutov4"),
    ]
    captured["on_changed"]()
    editor._close_section()
    assert editor._detail is None
    editor.refresh.assert_called()


def test_refresh_handles_empty_and_populated_catalogs(monkeypatch) -> None:
    catalogs = GlobalCatalogDraft()
    editor = _editor(catalogs)
    child = _Widget()
    editor._cards = SimpleNamespace(winfo_children=lambda: [child])
    monkeypatch.setattr(module.ttk, "Label", _Widget)
    editor.refresh = EquipmentSectionsEditor.refresh.__get__(editor)

    editor.refresh()
    assert child.destroyed

    catalogs.equipment_sections.append(EquipmentSectionDraft("Narutov4", "Наруто"))
    editor._card = Mock()
    editor.refresh()
    editor._card.assert_called_once_with(catalogs.equipment_sections[0])


def test_section_card_renders_name_count_and_controls(monkeypatch) -> None:
    catalogs = GlobalCatalogDraft(
        equipment_sections=[EquipmentSectionDraft("Narutov4", "Наруто")],
        equipment=[_item("kunai", "Narutov4")],
    )
    editor = _editor(catalogs)
    editor._cards = _Widget()
    created_buttons = []

    class FakeButton(_Widget):
        def __init__(self, *_args, **kwargs) -> None:
            super().__init__()
            created_buttons.append(kwargs)

    monkeypatch.setattr(module.tk, "Frame", _Widget)
    monkeypatch.setattr(module.tk, "Label", _Widget)
    monkeypatch.setattr(module.ttk, "Button", FakeButton)

    editor._card(catalogs.equipment_sections[0])

    assert [button["text"] for button in created_buttons] == ["Удалить", "Изменить", "Открыть"]


def test_editor_builds_two_level_catalog_list(monkeypatch) -> None:
    catalogs = GlobalCatalogDraft()
    editor = _editor(catalogs)

    class FakeCanvas(_Widget):
        def create_window(self, *_args, **_kwargs) -> int:
            return 1

        def configure(self, **_kwargs) -> None:
            return None

        def bbox(self, *_args):
            return (0, 0, 1, 1)

        def yview(self, *_args) -> None:
            return None

        def itemconfigure(self, *_args, **_kwargs) -> None:
            return None

    class FakeScrollbar(_Widget):
        def set(self, *_args) -> None:
            return None

    monkeypatch.setattr(module.ttk, "Frame", _Widget)
    monkeypatch.setattr(module.ttk, "Label", _Widget)
    monkeypatch.setattr(module.ttk, "Button", _Widget)
    monkeypatch.setattr(module.ttk, "Scrollbar", FakeScrollbar)
    monkeypatch.setattr(module.tk, "Canvas", FakeCanvas)

    editor._build()

    assert isinstance(editor._list_view, _Widget)
    assert isinstance(editor._canvas, FakeCanvas)
    assert isinstance(editor._cards, _Widget)
