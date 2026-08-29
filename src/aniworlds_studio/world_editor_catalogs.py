"""Composition of the complete catalog tabs inside the world editor."""

from collections.abc import Callable
from tkinter import ttk

from aniworlds_studio.catalog_editor import CatalogEditor
from aniworlds_studio.catalog_templates import CATALOG_SECTIONS
from aniworlds_studio.foundation_models import UniverseDraft


def build_catalog_tabs(
    parent: ttk.Frame,
    get_draft: Callable[[], UniverseDraft],
    on_changed: Callable[[], None],
) -> list[CatalogEditor]:
    section = ttk.LabelFrame(parent, text="Полные каталоги", padding=10)
    section.pack(fill="both", expand=True, pady=(12, 0))
    ttk.Label(
        section,
        text=(
            "Каждая вкладка редактирует полный структурированный объект. "
            "Кнопка «Опубликовать» проверит все ссылки между разделами."
        ),
        wraplength=680,
    ).pack(fill="x", pady=(0, 8))
    tabs = ttk.Notebook(section, width=690, height=520)
    tabs.pack(fill="both", expand=True)
    editors = []
    for field_name, title, _factory, identity_field in CATALOG_SECTIONS:
        editor = CatalogEditor(
            tabs,
            field_name=field_name,
            identity_field=identity_field,
            get_draft=get_draft,
            on_changed=on_changed,
        )
        tabs.add(editor, text=title)
        editors.append(editor)
    return editors
