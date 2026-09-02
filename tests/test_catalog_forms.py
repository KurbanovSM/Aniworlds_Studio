# ruff: noqa: RUF001

from types import SimpleNamespace

import pytest

from aniworlds_studio.catalog_form_specs import (
    CATALOG_FORM_SPECS,
    CATEGORY_OPTIONS,
    COGNITION_OPTIONS,
    COMMUNICATION_OPTIONS,
)
from aniworlds_studio.catalog_form_values import FormControl, read_control, write_control
from aniworlds_studio.catalog_references import entry_title, reference_options
from aniworlds_studio.foundation_models import (
    CreatureKindDraft,
    GroupDraft,
    ItemDraft,
    UniverseDraft,
)
from aniworlds_studio.global_catalogs import CharacterTraitDraft, GlobalCatalogDraft


class _Variable:
    def __init__(self, value=None) -> None:
        self.value = value

    def get(self):
        return self.value

    def set(self, value) -> None:
        self.value = value


class _Text:
    def __init__(self, text="") -> None:
        self.text = text

    def get(self, *_args):
        return self.text

    def insert(self, _position, text) -> None:
        self.text = text


class _Listbox:
    def __init__(self, selected=()) -> None:
        self.selected = set(selected)

    def curselection(self):
        return tuple(sorted(self.selected))

    def selection_set(self, index) -> None:
        self.selected.add(index)


def test_specs_cover_every_root_catalog_without_json_fields() -> None:
    assert set(CATALOG_FORM_SPECS) == {
        "periods",
        "locations",
        "groups",
        "creature_kinds",
        "items",
        "shop_policies",
        "characters",
    }
    assert all(field.kind != "json" for fields in CATALOG_FORM_SPECS.values() for field in fields)
    frequency = next(
        field for field in CATALOG_FORM_SPECS["items"] if field.key == "appearance_weight"
    )
    assert (frequency.minimum, frequency.maximum) == (1, 100)
    instance_limit = next(
        field for field in CATALOG_FORM_SPECS["items"] if field.key == "maximum_created_instances"
    )
    assert instance_limit.kind == "instance_limit"
    profession = next(
        field for field in CATALOG_FORM_SPECS["characters"] if field.key == "profession"
    )
    assert profession.maximum == 30


def test_creature_reference_options_match_game_contract_labels() -> None:
    assert CATEGORY_OPTIONS == (
        ("Расовая принадлежность", "race"),
        ("Животное", "animal"),
        ("Сверхъестественное существо", "supernatural"),
        ("Другой вид", "other"),
    )
    assert COGNITION_OPTIONS == (
        ("Инстинктивный", "instinctive"),
        ("Животный", "animal"),
        ("Разумный", "sapient"),
        ("Высший", "higher"),
    )
    assert COMMUNICATION_OPTIONS == (
        ("Сигналы", "signals"),
        ("Речь", "speech"),
        ("Жесты", "sign_language"),
        ("Письмо", "writing"),
        ("Телепатия", "telepathy"),
        ("Особый способ", "other"),
    )


@pytest.mark.parametrize(
    ("kind", "raw", "expected"),
    [
        ("boolean", True, True),
        ("text", " value ", "value"),
        ("integer", "7", 7),
        ("decimal", "1,5", 1.5),
        ("optional_integer", "", None),
        ("optional_integer", "3", 3),
    ],
)
def test_reads_scalar_controls(kind, raw, expected) -> None:
    assert read_control(FormControl(kind, object(), _Variable(raw))) == expected


def test_reads_and_writes_text_choices_and_lists() -> None:
    options = (("Первый", "one"), ("Второй", "two"))
    assert read_control(FormControl("choice", object(), _Variable("Второй"), options)) == "two"
    assert (
        read_control(FormControl("reference", object(), _Variable("custom"), options)) == "custom"
    )
    assert read_control(FormControl("long_text", _Text("  Текст  "))) == "Текст"
    assert read_control(FormControl("lines", _Text(" один\n\n два "))) == ["один", "два"]
    assert read_control(FormControl("choices", _Listbox((1,)), options=options)) == ["two"]

    variable = _Variable()
    write_control(FormControl("choice", object(), variable, options), "one")
    assert variable.value == "Первый"
    write_control(FormControl("boolean", object(), variable), 1)
    assert variable.value is True
    write_control(FormControl("text", object(), variable), None)
    assert variable.value == ""
    text = _Text()
    write_control(FormControl("lines", text), ["один", "два"])
    assert text.text == "один\nдва"
    listing = _Listbox()
    write_control(FormControl("references", listing, options=options), ["two"])
    assert listing.selected == {1}
    write_control(FormControl("references", object()), [])

    with pytest.raises(ValueError, match="Unsupported"):
        read_control(FormControl("unknown", object()))


def test_instance_limit_never_depends_on_an_ambiguous_blank_number() -> None:
    mode = _Variable("Без ограничений")
    amount = _Variable("1")
    control = FormControl("instance_limit", object(), (mode, amount))

    assert read_control(control) is None
    write_control(control, 3)
    assert mode.value == "Ограниченное количество"
    assert amount.value == "3"
    assert read_control(control) == 3


def test_reference_options_and_titles_use_authored_cards() -> None:
    draft = UniverseDraft()
    draft.groups = [GroupDraft(id="guards", name="Стража")]
    draft.items = [ItemDraft(id="bandage", name="Бинт")]
    draft.creature_kinds = [CreatureKindDraft(id="human", name="Человек")]

    assert reference_options(draft, "periods")[0][1] == "period"
    assert reference_options(draft, "locations")[0][1] == "start"
    assert reference_options(draft, "groups") == (("Стража (guards)", "guards"),)
    assert reference_options(draft, "items") == (("Бинт (bandage)", "bandage"),)
    assert reference_options(draft, "kinds") == (("Человек (human)", "human"),)
    catalogs = GlobalCatalogDraft(traits=[CharacterTraitDraft(id="brave", name="Смелый")])
    assert reference_options(catalogs, "traits") == (("Смелый (brave)", "brave"),)
    assert reference_options(draft, "missing") == ()
    assert entry_title(SimpleNamespace(id="x", name="Имя"), "id") == ("Имя", "x")
