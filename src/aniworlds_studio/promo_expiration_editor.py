"""Reusable Tkinter editor for an optional promo-code activation deadline."""

import tkinter as tk
from tkinter import ttk

from aniworlds_studio.promo_form_values import (
    expiration_from_local_fields,
    quick_expiration_fields,
)


class PromoExpirationEditor(ttk.LabelFrame):
    """Collect an optional local deadline without exposing ISO-8601 syntax."""

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, text="Срок новых активаций", padding=12)
        self._without_deadline = tk.BooleanVar(value=True)
        self._date = tk.StringVar()
        self._time = tk.StringVar()
        ttk.Checkbutton(
            self,
            text="Без срока действия",
            variable=self._without_deadline,
            command=self._sync_state,
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))
        ttk.Label(self, text="Дата").grid(row=1, column=0, sticky="w")
        self._date_entry = ttk.Entry(self, textvariable=self._date, width=14)
        self._date_entry.grid(row=2, column=0, sticky="w", padx=(0, 12))
        ttk.Label(self, text="Время").grid(row=1, column=1, sticky="w")
        self._time_entry = ttk.Entry(self, textvariable=self._time, width=9)
        self._time_entry.grid(row=2, column=1, sticky="w")
        ttk.Label(
            self,
            text="ДД.ММ.ГГГГ   ЧЧ:ММ · время компьютера",  # noqa: RUF001
        ).grid(
            row=3, column=0, columnspan=4, sticky="w", pady=(5, 10)
        )
        for column, days in enumerate((7, 30, 90)):
            ttk.Button(
                self,
                text=f"Через {days} дней",
                command=lambda selected=days: self._set_quick_deadline(selected),
            ).grid(row=4, column=column, sticky="w", padx=(0, 8))
        self._sync_state()

    def value(self) -> str | None:
        """Return the selected timezone-aware deadline or no deadline."""
        if self._without_deadline.get():
            return None
        return expiration_from_local_fields(self._date.get(), self._time.get())

    def _set_quick_deadline(self, days: int) -> None:
        date_value, time_value = quick_expiration_fields(days)
        self._without_deadline.set(False)
        self._date.set(date_value)
        self._time.set(time_value)
        self._sync_state()

    def _sync_state(self) -> None:
        state = "disabled" if self._without_deadline.get() else "normal"
        self._date_entry.configure(state=state)
        self._time_entry.configure(state=state)
