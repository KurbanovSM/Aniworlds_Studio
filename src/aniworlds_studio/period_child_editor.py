"""Separate card pages for period locations and starting kits."""

from dataclasses import asdict
from tkinter import ttk

from aniworlds_studio.catalog_form_dialog import CardFormDialog
from aniworlds_studio.catalog_form_specs import KIT_FIELDS
from aniworlds_studio.foundation_models import (
    StartingKitDraft,
    StartingKitItemDraft,
)
from aniworlds_studio.nested_value_editor import NestedValueEditor


class PeriodChildEditor(ttk.Frame):
    """Edit one nested period catalog without hiding it in the period card."""

    def __init__(
        self,
        parent: ttk.Widget,
        *,
        child: str,
        get_draft,
        on_changed,
    ) -> None:
        super().__init__(parent, padding=14, style="Surface.TFrame")
        self._child = child
        self._get_draft = get_draft
        self._on_changed = on_changed
        self._selector = ttk.Combobox(self, state="readonly")
        self._selector.pack(fill="x", pady=(0, 12))
        self._selector.bind("<<ComboboxSelected>>", lambda _event: self.refresh())
        self._editor: NestedValueEditor | None = None
        self.refresh()

    def refresh(self) -> None:
        periods = self._get_draft().periods
        selected = max(0, self._selector.current())
        self._selector["values"] = [f"{period.name} ({period.id})" for period in periods]
        if periods:
            self._selector.current(min(selected, len(periods) - 1))
        if self._editor is not None:
            self._editor.destroy()
            self._editor = None
        if not periods:
            return
        period = periods[self._selector.current()]
        fields = KIT_FIELDS
        values = [asdict(item) for item in getattr(period, self._child)]
        self._editor = NestedValueEditor(
            self,
            title="Стартовые наборы",
            fields=fields,
            values=values,
            open_form=self._open_form,
            on_changed=self._save,
            minimum=1,
            maximum=10,
        )
        self._editor.pack(fill="both", expand=True)

    def _open_form(self, fields, initial) -> dict | None:
        dialog = CardFormDialog(
            self,
            title="Стартовый набор",
            fields=fields,
            initial=initial,
            draft=self._get_draft(),
        )
        self.wait_window(dialog)
        return dialog.result

    def _save(self) -> None:
        if self._editor is None:
            return
        period = self._get_draft().periods[self._selector.current()]
        values = self._editor.values()
        period.starting_kits = [
            StartingKitDraft(
                **{key: value for key, value in item.items() if key != "items"},
                items=[StartingKitItemDraft(**entry) for entry in item.get("items", [])],
            )
            for item in values
        ]
        self._on_changed()
