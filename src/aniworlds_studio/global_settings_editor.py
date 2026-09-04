"""Global gameplay and narrator settings shared by every world."""

# ruff: noqa: RUF001

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from aniworlds_studio.global_settings_export import (
    DEFAULT_NARRATOR_SYSTEM_PROMPT,
    GLOBAL_SETTINGS_FILE_NAME,
    GlobalAbilitySettings,
    GlobalNarratorSettings,
    InvalidGlobalSettings,
    export_global_settings,
)
from aniworlds_studio.world_editor_shell import configure_native_editor


class GlobalSettingsFrame(ttk.Frame):
    """Edit only server-consumed global settings."""

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
                "Эти настройки одинаковы для всех миров. Расы, виды и "
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
        narrator = ttk.LabelFrame(self, text="Рассказчик", padding=18)
        narrator.pack(fill="both", expand=True, pady=(16, 0))
        ttk.Label(
            narrator,
            text="Системный промпт. Переменные в фигурных скобках обязательны.",
            style="Surface.TLabel",
        ).pack(anchor="w", pady=(0, 8))
        self._narrator_prompt = tk.Text(narrator, height=15, wrap="word", undo=True)
        configure_native_editor(self._narrator_prompt)
        self._narrator_prompt.insert("1.0", DEFAULT_NARRATOR_SYSTEM_PROMPT)
        self._narrator_prompt.pack(fill="both", expand=True)
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
            abilities = GlobalAbilitySettings(
                initial_ability_limit=int(self._initial.get()),
                learned_ability_limit=int(self._learned.get()),
                ability_lesson_count=int(self._lessons.get()),
            )
            narrator = GlobalNarratorSettings(
                system_prompt_template=self._narrator_prompt.get("1.0", "end-1c")
            )
            path = export_global_settings(
                abilities,
                narrator,
                Path(selected),
                replace_existing=replace,
            )
        except (InvalidGlobalSettings, ValueError, OSError) as error:
            messagebox.showerror("Не удалось сохранить", str(error))
            return
        self._status.set(f"Сохранено: {path}")
