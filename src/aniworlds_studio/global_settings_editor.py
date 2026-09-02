"""Global numeric gameplay settings shared by every world."""

# ruff: noqa: RUF001

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from aniworlds_studio.global_settings_export import (
    GLOBAL_SETTINGS_FILE_NAME,
    GlobalAbilitySettings,
    InvalidGlobalSettings,
    export_global_settings,
)


class GlobalSettingsFrame(ttk.Frame):
    """Edit only server-consumed global numeric rules."""

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=28)
        self._initial = tk.StringVar(value="5")
        self._learned = tk.StringVar(value="10")
        self._lessons = tk.StringVar(value="4")
        self._status = tk.StringVar(value="Файл ещё не сохранён")
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="ГЛОБАЛЬНЫЕ НАСТРОЙКИ", style="Accent.TLabel").pack(anchor="w")
        ttk.Label(self, text="Общие правила игры", font=("Segoe UI Semibold", 24)).pack(
            anchor="w", pady=(4, 4)
        )
        ttk.Label(
            self,
            text=(
                "Эти числовые правила одинаковы для всех миров. Расы, виды и "
                "объединения находятся в отдельной вкладке «Общие каталоги»."
            ),
            style="Muted.TLabel",
            wraplength=800,
        ).pack(anchor="w", pady=(0, 20))
        abilities = ttk.LabelFrame(self, text="Способности", padding=18)
        abilities.pack(fill="x")
        for label, variable in (
            ("Максимум способностей при создании персонажа", self._initial),
            ("Максимум способностей, изученных в игре", self._learned),
            ("Подтверждённых уроков для изучения способности", self._lessons),
        ):
            row = ttk.Frame(abilities, style="Surface.TFrame")
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label, style="Surface.TLabel").pack(
                side="left", expand=True, fill="x"
            )
            ttk.Spinbox(row, from_=1, to=100, textvariable=variable, width=8).pack(side="right")
        ttk.Button(
            self,
            text="Сохранить глобальные настройки",
            style="Primary.TButton",
            command=self._save,
        ).pack(anchor="w", pady=(18, 8))
        ttk.Label(self, textvariable=self._status, style="Muted.TLabel").pack(anchor="w")

    def _save(self) -> None:
        selected = filedialog.askdirectory(title="Выберите папку settings")
        if not selected:
            return
        target = Path(selected) / GLOBAL_SETTINGS_FILE_NAME
        replace = target.exists() and messagebox.askyesno(
            "Заменить глобальные настройки?",
            "В выбранной папке уже есть файл глобальных настроек. Заменить его?",
        )
        if target.exists() and not replace:
            return
        try:
            settings = GlobalAbilitySettings(
                initial_ability_limit=int(self._initial.get()),
                learned_ability_limit=int(self._learned.get()),
                ability_lesson_count=int(self._lessons.get()),
            )
            path = export_global_settings(settings, Path(selected), replace_existing=replace)
        except (InvalidGlobalSettings, ValueError, OSError) as error:
            messagebox.showerror("Не удалось сохранить", str(error))
            return
        self._status.set(f"Сохранено: {path}")
