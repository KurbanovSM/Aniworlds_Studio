"""Scrollable card form that hides JSON and stable reference plumbing."""

# ruff: noqa: RUF001

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, cast

from aniworlds_studio.catalog_form_controls import (
    bind_after_build,
    bind_text_growth,
    build_control,
)
from aniworlds_studio.catalog_form_specs import FieldSpec
from aniworlds_studio.catalog_form_values import FormControl, read_control
from aniworlds_studio.catalog_references import reference_options
from aniworlds_studio.foundation_models import UniverseDraft
from aniworlds_studio.nested_value_editor import NestedValueEditor
from aniworlds_studio.world_editor_scroll import bind_form_mousewheel


class CardFormDialog(tk.Toplevel):
    """Edit one mapping with explicit controls and nested card lists."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        title: str,
        fields: tuple[FieldSpec, ...],
        initial: dict,
        draft: UniverseDraft,
        reference_draft: object | None = None,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.geometry("860x720")
        self.minsize(680, 480)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.result: dict | None = None
        self._draft = draft
        self._reference_draft = reference_draft or draft
        self._fields = fields
        self._controls: dict[str, FormControl | NestedValueEditor] = {}
        self._build(initial)

    def _build(self, initial: dict) -> None:
        canvas = tk.Canvas(self, highlightthickness=0, background="#090a0e")
        scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        form = ttk.Frame(canvas, padding=18)
        window = canvas.create_window((0, 0), window=form, anchor="nw")
        form.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        for spec in self._fields:
            value = initial.get(spec.key)
            if spec.kind in {"nested", "states"}:
                self._controls[spec.key] = self._nested_control(form, spec, value)
                continue
            source = self._reference_draft if spec.source == "traits" else self._draft
            options = spec.options or reference_options(source, spec.source)
            if spec.kind in {"choice_optional", "reference_optional"}:
                options = (("Не задано", ""), *options)
            self._controls[spec.key] = build_control(
                form,
                spec,
                options=options,
                initial=value,
            )
        actions = ttk.Frame(form)
        actions.pack(fill="x", pady=(18, 8))
        ttk.Button(
            actions,
            text="Сохранить карточку",
            style="Primary.TButton",
            command=self._save,
        ).pack(side="right")
        ttk.Button(actions, text="Отмена", command=self.destroy).pack(side="right", padx=8)
        bind_after_build(form, bind_text_growth)
        bind_form_mousewheel(form, lambda units: canvas.yview_scroll(units, "units"))

    def _nested_control(
        self,
        parent: ttk.Widget,
        spec: FieldSpec,
        value: object,
    ) -> NestedValueEditor:
        fields = spec.nested
        values: list[dict]
        if spec.kind == "states":
            fields = (
                FieldSpec("period_id", "Период", "reference", source="periods"),
                FieldSpec("description", "Состояние", "long_text"),
            )
            values = [
                {"period_id": period_id, "description": description}
                for period_id, description in cast(dict[str, str], value or {}).items()
            ]
        else:
            values = [dict(item) for item in cast(list[dict[str, Any]], value or [])]
        editor = NestedValueEditor(
            parent,
            title=spec.label,
            fields=fields,
            values=values,
            open_form=lambda child_fields, child: self._open_nested(
                spec.label, child_fields, child
            ),
            minimum=spec.minimum,
            maximum=spec.maximum,
        )
        editor.pack(fill="x", pady=8)
        return editor

    def _open_nested(
        self,
        title: str,
        fields: tuple[FieldSpec, ...],
        initial: dict,
    ) -> dict | None:
        dialog = CardFormDialog(
            self,
            title=title,
            fields=fields,
            initial=initial,
            draft=self._draft,
            reference_draft=self._reference_draft,
        )
        self.wait_window(dialog)
        return dialog.result

    def _save(self) -> None:
        try:
            result: dict = {}
            for spec in self._fields:
                control = self._controls[spec.key]
                if isinstance(control, NestedValueEditor):
                    values = control.values()
                    result[spec.key] = (
                        {item["period_id"]: item["description"] for item in values}
                        if spec.kind == "states"
                        else values
                    )
                else:
                    result[spec.key] = read_control(control)
        except (TypeError, ValueError) as error:
            messagebox.showerror("Проверьте поля", str(error), parent=self)
            return
        self.result = result
        self.destroy()
