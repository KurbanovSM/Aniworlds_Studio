"""Assign independent locations to periods and edit period-only transitions."""

# ruff: noqa: RUF001

import tkinter as tk
from tkinter import messagebox, ttk

from aniworlds_studio.foundation_models import PeriodConnectionDraft


class PeriodLocationEditor(ttk.Frame):
    """Prevent references to locations that do not exist in the selected period."""

    def __init__(self, parent: ttk.Widget, *, get_draft, on_changed) -> None:
        super().__init__(parent, padding=14, style="Surface.TFrame")
        self._get_draft = get_draft
        self._on_changed = on_changed
        self._period = ttk.Combobox(self, state="readonly")
        self._period.pack(fill="x", pady=(0, 10))
        self._period.bind("<<ComboboxSelected>>", lambda _event: self.refresh())
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)
        selection = ttk.LabelFrame(body, text="Локации периода", padding=10)
        transitions = ttk.LabelFrame(body, text="Старт и переходы", padding=10)
        selection.pack(side="left", fill="both", expand=True, padx=(0, 6))
        transitions.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self._locations = tk.Listbox(selection, selectmode="multiple", exportselection=False)
        self._locations.pack(fill="both", expand=True)
        ttk.Button(selection, text="Сохранить состав периода", command=self._save_locations).pack(
            anchor="w", pady=(8, 0)
        )
        ttk.Label(transitions, text="Исходная локация").pack(anchor="w")
        self._source = ttk.Combobox(transitions, state="readonly")
        self._source.pack(fill="x", pady=(4, 8))
        self._source.bind("<<ComboboxSelected>>", lambda _event: self._refresh_transition())
        self._starting = tk.StringVar(value="")
        ttk.Label(transitions, textvariable=self._starting, style="Muted.TLabel").pack(anchor="w")
        ttk.Button(
            transitions,
            text="Переключить доступность как стартовой",
            command=self._toggle_starting,
        ).pack(anchor="w", pady=(6, 10))
        ttk.Label(transitions, text="Прямые переходы в этом периоде").pack(anchor="w")
        self._targets = tk.Listbox(transitions, selectmode="multiple", exportselection=False)
        self._targets.pack(fill="both", expand=True, pady=(4, 0))
        ttk.Button(transitions, text="Сохранить переходы", command=self._save_transitions).pack(
            anchor="w", pady=(8, 0)
        )
        self.refresh()

    def refresh(self) -> None:
        periods = self._get_draft().periods
        selected_period = max(0, self._period.current())
        self._period["values"] = [f"{item.name} ({item.id})" for item in periods]
        if not periods:
            self._clear()
            return
        self._period.current(min(selected_period, len(periods) - 1))
        period = self._current_period()
        self._locations.delete(0, "end")
        for index, location in enumerate(self._get_draft().locations):
            self._locations.insert("end", f"{location.name} ({location.id})")
            if location.id in period.location_ids:
                self._locations.selection_set(index)
        self._refresh_sources()

    def _save_locations(self) -> None:
        period = self._current_period()
        selected = [
            self._get_draft().locations[index].id for index in self._locations.curselection()
        ]
        if not selected:
            messagebox.showerror("Период без локаций", "Добавьте в период хотя бы одну локацию.")
            return
        allowed = set(selected)
        period.location_ids = selected
        period.starting_location_ids = [
            item for item in period.starting_location_ids if item in allowed
        ]
        period.location_connections = [
            PeriodConnectionDraft(
                connection.location_id,
                [target for target in connection.connected_location_ids if target in allowed],
            )
            for connection in period.location_connections
            if connection.location_id in allowed
        ]
        self._refresh_sources()
        self._on_changed()

    def _toggle_starting(self) -> None:
        period = self._current_period()
        source = self._source_id()
        if source is None:
            return
        if source in period.starting_location_ids:
            if len(period.starting_location_ids) == 1:
                messagebox.showerror(
                    "Нужна стартовая локация",
                    "В периоде должна остаться хотя бы одна стартовая локация.",
                )
                return
            period.starting_location_ids.remove(source)
        else:
            period.starting_location_ids.append(source)
        self._refresh_transition()
        self._on_changed()

    def _save_transitions(self) -> None:
        period = self._current_period()
        source = self._source_id()
        if source is None:
            return
        target_ids = [
            location_id
            for index, location_id in enumerate(self._target_ids)
            if index in self._targets.curselection()
        ]
        existing = next(
            (item for item in period.location_connections if item.location_id == source),
            None,
        )
        if existing is None and target_ids:
            period.location_connections.append(PeriodConnectionDraft(source, target_ids))
        elif existing is not None:
            existing.connected_location_ids = target_ids
            if not target_ids:
                period.location_connections.remove(existing)
        self._on_changed()

    def _refresh_sources(self) -> None:
        period = self._current_period()
        locations = {item.id: item for item in self._get_draft().locations}
        previous = self._source.current()
        self._source_ids = [item for item in period.location_ids if item in locations]
        self._source["values"] = [f"{locations[item].name} ({item})" for item in self._source_ids]
        if self._source_ids:
            self._source.current(min(max(previous, 0), len(self._source_ids) - 1))
        self._refresh_transition()

    def _refresh_transition(self) -> None:
        self._targets.delete(0, "end")
        source = self._source_id()
        if source is None:
            self._starting.set("В периоде пока нет локаций")
            self._target_ids = []
            return
        period = self._current_period()
        locations = {item.id: item for item in self._get_draft().locations}
        self._starting.set(
            "Стартовая локация: да"
            if source in period.starting_location_ids
            else "Стартовая локация: нет"
        )
        self._target_ids = [item for item in period.location_ids if item != source]
        connected = next(
            (
                set(item.connected_location_ids)
                for item in period.location_connections
                if item.location_id == source
            ),
            set(),
        )
        for index, target in enumerate(self._target_ids):
            self._targets.insert("end", f"{locations[target].name} ({target})")
            if target in connected:
                self._targets.selection_set(index)

    def _current_period(self):
        return self._get_draft().periods[self._period.current()]

    def _source_id(self) -> str | None:
        index = self._source.current()
        return self._source_ids[index] if 0 <= index < len(self._source_ids) else None

    def _clear(self) -> None:
        self._locations.delete(0, "end")
        self._source["values"] = ()
        self._targets.delete(0, "end")
        self._source_ids = []
        self._target_ids = []
