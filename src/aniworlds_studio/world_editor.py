"""Tkinter adapter for editing and publishing the full world-foundation contract."""

# ruff: noqa: RUF001
import tkinter as tk
from tkinter import messagebox, ttk

from aniworlds_studio.foundation_models import PeriodDraft, UniverseDraft
from aniworlds_studio.world_editor_catalogs import build_catalog_tabs
from aniworlds_studio.world_editor_files import (
    open_draft_dialog,
    publish_dialog,
    save_draft_dialog,
    show_preview,
)
from aniworlds_studio.world_editor_language import build_language_fields, entry_field
from aniworlds_studio.world_editor_scroll import bind_form_mousewheel


class WorldEditorFrame(ttk.Frame):
    """Scrollable form; domain validation remains outside the UI."""

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent)
        self._draft = UniverseDraft()
        self._period_index = 0
        self._variables: dict[str, tk.StringVar] = {}
        self._period_variables: dict[str, tk.StringVar] = {}
        self._kit_variables: list[dict[str, tk.StringVar]] = []
        self._language_spoken = tk.BooleanVar(value=True)
        self._language_written = tk.BooleanVar(value=True)
        self._status = tk.StringVar(value="Новый черновик")
        self._build()
        self._load_form()

    def _build(self) -> None:
        toolbar = ttk.Frame(self, padding=(14, 10))
        toolbar.pack(fill="x")
        for text, command in (
            ("Новый", self._new),
            ("Открыть черновик", self._open),
            ("Сохранить черновик", self._save_draft),
            ("Предпросмотр", self._preview),
            ("Опубликовать", self._publish),
        ):
            ttk.Button(toolbar, text=text, command=command).pack(side="left", padx=(0, 8))
        ttk.Label(toolbar, textvariable=self._status).pack(side="right")
        workspace = ttk.Notebook(self)
        workspace.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        basics = ttk.Frame(workspace)
        catalogs = ttk.Frame(workspace)
        workspace.add(basics, text="Основные настройки")
        workspace.add(catalogs, text="Полные каталоги")
        canvas = tk.Canvas(basics, highlightthickness=0)
        scrollbar = ttk.Scrollbar(basics, orient="vertical", command=canvas.yview)
        self._form = ttk.Frame(canvas, padding=(10, 10, 22, 24))
        window = canvas.create_window((0, 0), window=self._form, anchor="nw")
        self._form.bind(
            "<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._build_universe_section()
        self._build_period_section()
        self._build_kind_section()
        self._catalog_editors = build_catalog_tabs(
            catalogs, lambda: self._draft, self._catalog_changed
        )
        bind_form_mousewheel(self._form, lambda units: canvas.yview_scroll(units, "units"))

    def _build_universe_section(self) -> None:
        section = ttk.LabelFrame(self._form, text="Вселенная и правила игры", padding=12)
        section.pack(fill="x", pady=(0, 12))
        fields = (
            ("id", "ID вселенной"),
            ("name", "Название"),
            ("description", "Описание"),
            ("world_rules", "Правила мира"),
            ("power_systems", "Системы сил"),
            ("currency_id", "ID валюты"),
            ("currency_name", "Название валюты"),
            ("currency_symbol", "Символ валюты"),
            ("strength_name", "Название запаса сил"),
            ("initial_ability_limit", "Способностей при старте"),
            ("learned_ability_limit", "Можно изучить в мире"),
            ("ability_lesson_count", "Событий обучения способности"),
        )
        for key, label in fields:
            self._variables[key] = entry_field(section, label)

    def _build_period_section(self) -> None:
        section = ttk.LabelFrame(self._form, text="Периоды и старт", padding=12)
        section.pack(fill="x", pady=(0, 12))
        selector = ttk.Frame(section)
        selector.pack(fill="x", pady=(0, 8))
        self._period_selector = ttk.Combobox(selector, state="readonly", width=38)
        self._period_selector.pack(side="left")
        self._period_selector.bind("<<ComboboxSelected>>", self._select_period)
        ttk.Button(selector, text="Добавить период", command=self._add_period).pack(
            side="left", padx=8
        )
        ttk.Button(selector, text="Удалить период", command=self._delete_period).pack(side="left")
        fields = (
            ("id", "ID периода"),
            ("name", "Название периода"),
            ("description", "Описание периода"),
            ("lore", "Лор периода"),
            ("initial_situation", "Начальная ситуация"),
            ("location_id", "ID стартовой локации"),
            ("location_name", "Название стартовой локации"),
            ("location_description", "Описание стартовой локации"),
        )
        for key, label in fields:
            self._period_variables[key] = entry_field(section, label)
        ttk.Label(section, text="Три обязательных стартовых набора").pack(anchor="w", pady=(10, 4))
        for position in range(3):
            row: dict[str, tk.StringVar] = {}
            box = ttk.LabelFrame(section, text=f"Набор {position + 1}", padding=8)
            box.pack(fill="x", pady=4)
            for key, label in (
                ("id", "ID"),
                ("name", "Название"),
                ("description", "Описание"),
                ("starting_currency_amount", "Стартовая валюта"),
            ):
                row[key] = entry_field(box, label)
            self._kit_variables.append(row)

    def _build_kind_section(self) -> None:
        section = ttk.LabelFrame(self._form, text="Базовый вид или раса", padding=12)
        section.pack(fill="x")
        for key, label in (
            ("kind_id", "ID"),
            ("kind_name", "Название"),
            ("kind_description", "Описание"),
        ):
            self._variables[key] = entry_field(section, label)
        ttk.Label(
            section,
            text="Сейчас публикуется базовый разумный вид с речью и письменностью.",
        ).pack(anchor="w", pady=(6, 0))
        build_language_fields(
            section,
            self._variables,
            self._language_spoken,
            self._language_written,
        )

    def _catalog_changed(self) -> None:
        if self._draft.periods and self._draft.creature_kinds and self._draft.languages:
            self._period_index = min(self._period_index, len(self._draft.periods) - 1)
            self._load_form()
        self._status.set("Черновик изменён")

    def _refresh_catalogs(self) -> None:
        for editor in getattr(self, "_catalog_editors", ()):
            editor.refresh()

    def _store_form(self) -> None:
        draft = self._draft
        if not draft.periods or not draft.creature_kinds or not draft.languages:
            raise ValueError(
                "Каталоги периодов, видов и языков должны содержать хотя бы одну запись."
            )
        for key in ("id", "name", "description", "world_rules", "power_systems"):
            setattr(draft, key, self._variables[key].get())
        gameplay = draft.gameplay
        for key in ("currency_id", "currency_name", "currency_symbol", "strength_name"):
            setattr(gameplay, key, self._variables[key].get())
        for key in ("initial_ability_limit", "learned_ability_limit", "ability_lesson_count"):
            setattr(gameplay, key, int(self._variables[key].get()))
        kind = draft.creature_kinds[0]
        kind.id = self._variables["kind_id"].get()
        kind.name = self._variables["kind_name"].get()
        kind.description = self._variables["kind_description"].get()
        language = draft.languages[0]
        language.id = self._variables["language_id"].get()
        language.name = self._variables["language_name"].get()
        language.has_spoken_form = self._language_spoken.get()
        language.has_written_form = self._language_written.get()
        period = draft.periods[self._period_index]
        for key in ("id", "name", "description", "lore", "initial_situation"):
            setattr(period, key, self._period_variables[key].get())
        location = period.starting_locations[0]
        location.id = self._period_variables["location_id"].get()
        location.name = self._period_variables["location_name"].get()
        location.description = self._period_variables["location_description"].get()
        for kit, variables in zip(period.starting_kits, self._kit_variables, strict=True):
            kit.id, kit.name, kit.description = (
                variables[key].get() for key in ("id", "name", "description")
            )
            kit.starting_currency_amount = int(variables["starting_currency_amount"].get())

    def _load_form(self) -> None:
        draft = self._draft
        for key in ("id", "name", "description", "world_rules", "power_systems"):
            self._variables[key].set(getattr(draft, key))
        for key in (
            "currency_id",
            "currency_name",
            "currency_symbol",
            "strength_name",
            "initial_ability_limit",
            "learned_ability_limit",
            "ability_lesson_count",
        ):
            self._variables[key].set(str(getattr(draft.gameplay, key)))
        kind = draft.creature_kinds[0]
        for key, value in (
            ("kind_id", kind.id),
            ("kind_name", kind.name),
            ("kind_description", kind.description),
        ):
            self._variables[key].set(value)
        language = draft.languages[0]
        self._variables["language_id"].set(language.id)
        self._variables["language_name"].set(language.name)
        self._language_spoken.set(language.has_spoken_form)
        self._language_written.set(language.has_written_form)
        self._period_selector["values"] = [f"{item.name} ({item.id})" for item in draft.periods]
        self._period_selector.current(self._period_index)
        period = draft.periods[self._period_index]
        for key in ("id", "name", "description", "lore", "initial_situation"):
            self._period_variables[key].set(getattr(period, key))
        location = period.starting_locations[0]
        for key, value in (
            ("location_id", location.id),
            ("location_name", location.name),
            ("location_description", location.description),
        ):
            self._period_variables[key].set(value)
        for kit, variables in zip(period.starting_kits, self._kit_variables, strict=True):
            for key in ("id", "name", "description", "starting_currency_amount"):
                variables[key].set(str(getattr(kit, key)))

    def _select_period(self, _event: object) -> None:
        self._store_form()
        self._period_index = self._period_selector.current()
        self._load_form()

    def _add_period(self) -> None:
        self._store_form()
        self._draft.periods.append(PeriodDraft(id=f"period-{len(self._draft.periods) + 1}"))
        self._period_index = len(self._draft.periods) - 1
        self._load_form()

    def _delete_period(self) -> None:
        if len(self._draft.periods) == 1:
            messagebox.showerror(
                "Нельзя удалить", "Во вселенной должен остаться хотя бы один период."
            )
            return
        del self._draft.periods[self._period_index]
        self._period_index = min(self._period_index, len(self._draft.periods) - 1)
        self._load_form()

    def _new(self) -> None:
        self._draft, self._period_index = UniverseDraft(), 0
        self._load_form()
        self._refresh_catalogs()
        self._status.set("Новый черновик")

    def _open(self) -> None:
        result = open_draft_dialog()
        if result is None:
            return
        self._draft, selected = result
        self._period_index = 0
        self._load_form()
        self._refresh_catalogs()
        self._status.set(f"Открыт: {selected}")

    def _save_draft(self) -> None:
        try:
            self._store_form()
        except ValueError as error:
            messagebox.showerror("Не удалось сохранить", str(error))
            return
        path = save_draft_dialog(self._draft)
        if path is not None:
            self._status.set(f"Сохранено: {path}")

    def _publish(self) -> None:
        try:
            self._store_form()
        except ValueError as error:
            messagebox.showerror("Публикация невозможна", str(error))
            return
        path = publish_dialog(self._draft)
        if path is not None:
            self._status.set(f"Опубликовано: {path}")

    def _preview(self) -> None:
        try:
            self._store_form()
        except ValueError as error:
            messagebox.showerror("Предпросмотр невозможен", str(error))
            return
        show_preview(self, self._draft)
