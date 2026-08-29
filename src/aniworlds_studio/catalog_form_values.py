"""Read and write values for declarative Studio card forms."""

from dataclasses import dataclass
from typing import Any, Protocol


class VariableControl(Protocol):
    def get(self) -> Any: ...

    def set(self, value: Any) -> None: ...


@dataclass(slots=True)
class FormControl:
    kind: str
    widget: Any
    variable: VariableControl | None = None
    options: tuple[tuple[str, str], ...] = ()


def read_control(control: FormControl) -> Any:
    if control.kind == "boolean":
        return bool(control.variable.get()) if control.variable is not None else False
    if control.kind in {
        "text",
        "integer",
        "decimal",
        "optional_integer",
        "choice",
        "reference",
    }:
        raw = str(control.variable.get()).strip() if control.variable is not None else ""
        if control.kind == "integer":
            return int(raw)
        if control.kind == "decimal":
            return float(raw.replace(",", "."))
        if control.kind == "optional_integer":
            return None if not raw else int(raw)
        if control.kind in {"choice", "reference"}:
            return _value_for_label(raw, control.options)
        return raw
    if control.kind in {"long_text", "lines"}:
        text = control.widget.get("1.0", "end-1c")  # type: ignore[attr-defined]
        return text.strip() if control.kind == "long_text" else _lines(text)
    if control.kind in {"choices", "references"}:
        selections = control.widget.curselection()  # type: ignore[attr-defined]
        return [control.options[index][1] for index in selections]
    raise ValueError(f"Unsupported form control: {control.kind}")


def write_control(control: FormControl, value: Any) -> None:
    if control.kind in {"long_text", "lines"}:
        text = value if isinstance(value, str) else "\n".join(value or ())
        control.widget.insert("1.0", text)  # type: ignore[attr-defined]
        return
    if control.kind in {"choices", "references"}:
        wanted = set(value or ())
        for index, (_, option_value) in enumerate(control.options):
            if option_value in wanted:
                control.widget.selection_set(index)  # type: ignore[attr-defined]
        return
    if control.variable is None:
        return
    if control.kind == "boolean":
        control.variable.set(bool(value))
    elif control.kind in {"choice", "reference"}:
        control.variable.set(_label_for_value(value, control.options))
    else:
        control.variable.set("" if value is None else str(value))


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _label_for_value(value: Any, options: tuple[tuple[str, str], ...]) -> str:
    return next((label for label, option in options if option == value), "")


def _value_for_label(label: str, options: tuple[tuple[str, str], ...]) -> str | None:
    if not label:
        return None
    value = next((value for option_label, value in options if option_label == label), label)
    return value or None
