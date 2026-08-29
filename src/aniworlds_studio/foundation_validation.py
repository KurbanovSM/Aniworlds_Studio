"""Single validation source for Studio world-foundation drafts."""

# ruff: noqa: RUF001
import re
from collections.abc import Iterable

from aniworlds_studio.catalog_contract_values import (
    CATEGORY_OPTIONS,
    COGNITION_OPTIONS,
    COMMUNICATION_OPTIONS,
    GROUP_TYPE_OPTIONS,
    ITEM_CATEGORY_OPTIONS,
    SHOP_OPTIONS,
    option_values,
)
from aniworlds_studio.foundation_models import (
    MAX_APPEARANCE_FREQUENCY,
    MAX_STARTING_KIT_COUNT,
    MIN_APPEARANCE_FREQUENCY,
    MIN_STARTING_KIT_COUNT,
    PeriodDraft,
    UniverseDraft,
)

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class InvalidFoundation(ValueError):
    """A draft cannot be published through the server contract."""


def validate_foundation(draft: UniverseDraft) -> None:
    _require_id(draft.id, "ID вселенной")
    _require_text(draft.name, "Название вселенной")
    _require_text(draft.description, "Описание вселенной")
    _require_text(draft.world_rules, "Правила мира")
    _require_text(draft.power_systems, "Системы сил")
    _validate_gameplay(draft)
    if not draft.periods:
        raise InvalidFoundation("Добавьте хотя бы один период.")
    if not draft.creature_kinds:
        raise InvalidFoundation("Добавьте хотя бы один вид или расу.")
    if not draft.languages:
        raise InvalidFoundation("Добавьте хотя бы один язык.")
    _require_unique((period.id for period in draft.periods), "ID периодов")
    _validate_locations(draft)
    for period in draft.periods:
        _validate_period(period, {location.id for location in draft.locations})
    _require_unique((kind.id for kind in draft.creature_kinds), "ID видов и рас")
    for kind in draft.creature_kinds:
        validate_shared_kind(kind)
    _require_unique((language.id for language in draft.languages), "ID языков")
    for language in draft.languages:
        validate_shared_language(language)
    _validate_catalog_references(draft)


def _validate_catalog_references(draft: UniverseDraft) -> None:
    period_ids = {item.id for item in draft.periods}
    locations = {location.id for location in draft.locations}
    language_ids = {item.id for item in draft.languages}
    kind_ids = {item.id for item in draft.creature_kinds}
    group_ids = {item.id for item in draft.groups}
    item_ids = {item.id for item in draft.items}
    _require_unique((item.id for item in draft.items), "ID предметов")
    _require_unique((item.id for item in draft.groups), "ID объединений")
    _require_unique((item.id for item in draft.characters), "ID персонажей")
    _require_unique((item.shop_kind for item in draft.shop_policies), "Виды магазинов")
    for kind in draft.creature_kinds:
        _require_references(kind.period_ids, period_ids, "период вида")
        _require_references(kind.habitat_location_ids, locations, "место обитания")
        if kind.parent_kind_id is not None and kind.parent_kind_id not in kind_ids:
            raise InvalidFoundation(f"Не найден родительский вид: {kind.parent_kind_id}.")
        _validate_language_knowledge(kind.default_languages, language_ids)
    for group in draft.groups:
        _validate_group(group, period_ids, locations, group_ids)
    for item in draft.items:
        _validate_item(item)
    for policy in draft.shop_policies:
        if not 0 < policy.minimum_assortment_size <= policy.maximum_assortment_size <= 10:
            raise InvalidFoundation("Размер ассортимента магазина должен быть от 1 до 10.")
    for period in draft.periods:
        for kit in period.starting_kits:
            _require_references((entry.item_id for entry in kit.items), item_ids, "предмет набора")
            if any(entry.quantity <= 0 for entry in kit.items):
                raise InvalidFoundation("Количество предмета в наборе должно быть больше нуля.")
    for character in draft.characters:
        _validate_character(character, period_ids, locations, kind_ids, group_ids, language_ids)


def _validate_locations(draft: UniverseDraft) -> None:
    if not draft.locations:
        raise InvalidFoundation("Добавьте хотя бы одну локацию.")
    _require_unique((location.id for location in draft.locations), "ID локаций")
    for location in draft.locations:
        _require_id(location.id, "ID локации")
        _require_text(location.name, "Название локации")
        _require_text(location.description, "Описание локации")
        if location.price_coefficient <= 0:
            raise InvalidFoundation("Коэффициент цен локации должен быть больше нуля.")


def _validate_group(group, period_ids, location_ids, group_ids) -> None:
    validate_shared_group(group)
    _require_references(group.location_ids, location_ids, "локацию объединения")
    _require_references(group.ally_ids, group_ids, "союзное объединение")
    _require_references(group.enemy_ids, group_ids, "враждебное объединение")
    _require_references(group.period_states, period_ids, "период состояния объединения")
    if group.id in {*group.ally_ids, *group.enemy_ids} or set(group.ally_ids) & set(
        group.enemy_ids
    ):
        raise InvalidFoundation("Союзники и противники объединения противоречат друг другу.")
    if any(not state.strip() for state in group.period_states.values()):
        raise InvalidFoundation("Состояние объединения в периоде не может быть пустым.")


def validate_shared_kind(kind) -> None:
    _require_shared_id(kind.id, "ID вида или расы")
    _require_text(kind.name, "Название вида или расы")
    _require_text(kind.description, "Описание вида или расы")
    if kind.category not in option_values(CATEGORY_OPTIONS):
        raise InvalidFoundation("Неизвестная категория вида или расы.")
    if kind.cognition not in option_values(COGNITION_OPTIONS):
        raise InvalidFoundation("Неизвестный уровень мышления вида или расы.")
    modes = kind.communication_modes
    if not modes or not set(modes) <= option_values(COMMUNICATION_OPTIONS):
        raise InvalidFoundation(f"У вида «{kind.name}» нет допустимого способа общения.")
    _require_unique(modes, "Способы общения вида или расы")
    if any(not feature.strip() for feature in kind.physical_features):
        raise InvalidFoundation("Физическая особенность вида или расы не может быть пустой.")


def validate_shared_language(language) -> None:
    _require_shared_id(language.id, "ID языка")
    _require_text(language.name, "Название языка")
    if not language.has_spoken_form and not language.has_written_form:
        raise InvalidFoundation("Язык должен иметь устную или письменную форму.")


def validate_shared_group(group) -> None:
    _require_shared_id(group.id, "ID объединения")
    _require_text(group.name, "Название объединения")
    _require_text(group.description, "Описание объединения")
    if group.group_type not in option_values(GROUP_TYPE_OPTIONS):
        raise InvalidFoundation("Неизвестный тип объединения.")


def _validate_item(item) -> None:
    _require_id(item.id, "ID предмета")
    _require_text(item.name, "Название предмета")
    _require_text(item.description, "Описание предмета")
    if any(mark in item.name for mark in ('"', "[", "]", "*")):
        raise InvalidFoundation("Название предмета содержит запрещённый технический знак.")
    if item.category not in option_values(ITEM_CATEGORY_OPTIONS):
        raise InvalidFoundation("Неизвестная категория предмета.")
    if item.uniqueness not in {"ordinary", "unique"}:
        raise InvalidFoundation("Неизвестный тип уникальности предмета.")
    if item.base_price < 0 or not (
        MIN_APPEARANCE_FREQUENCY
        <= item.appearance_weight
        <= MAX_APPEARANCE_FREQUENCY
    ):
        raise InvalidFoundation(
            "Цена не может быть отрицательной, а частота появления должна быть от 1 до 100."
        )
    if item.maximum_created_instances is not None and item.maximum_created_instances <= 0:
        raise InvalidFoundation("Лимит экземпляров должен быть положительным.")
    if any(not value.strip() for value in (*item.properties, *item.limitations)):
        raise InvalidFoundation("Свойства и ограничения предмета не могут быть пустыми.")
    if not set(item.allowed_shop_kinds) <= option_values(SHOP_OPTIONS):
        raise InvalidFoundation("Предмет ссылается на неизвестный вид магазина.")


def _validate_character(
    character, period_ids, location_ids, kind_ids, group_ids, language_ids
) -> None:
    _require_id(character.id, "ID персонажа")
    _require_text(character.name, "Имя персонажа")
    _require_text(character.biography, "Биография персонажа")
    if character.sex not in {"male", "female"} or not 18 <= character.age <= 10_000:
        raise InvalidFoundation("Пол или возраст подготовленного персонажа недопустим.")
    _require_references(character.period_ids, period_ids, "период персонажа")
    _require_references((character.origin_location_id,), location_ids, "исходную локацию")
    _require_references((character.creature_kind_id,), kind_ids, "вид персонажа")
    _require_references(character.group_ids, group_ids, "объединение персонажа")
    _require_references(character.leader_group_ids, set(character.group_ids), "лидерство персонажа")
    _validate_language_knowledge(character.language_knowledge, language_ids)
    if len(character.trait_ids) > 8 or len(character.abilities) > 8:
        raise InvalidFoundation("У персонажа может быть не больше восьми черт и способностей.")
    _require_unique(character.trait_ids, "Черты персонажа")
    _require_unique((ability.id for ability in character.abilities), "ID способностей")
    for ability in character.abilities:
        _require_id(ability.id, "ID способности")
        _require_text(ability.name, "Название способности")
        _require_text(ability.short_description, "Краткое описание способности")
        _require_text(ability.description, "Описание способности")
        if ability.kind not in {"ordinary", "sustained"}:
            raise InvalidFoundation("Неизвестный тип способности.")


def _validate_language_knowledge(entries, language_ids) -> None:
    ids = [entry.get("language_id") for entry in entries]
    if any(not isinstance(item, str) for item in ids):
        raise InvalidFoundation("Знание языка должно содержать language_id.")
    _require_unique(ids, "ID знаний языков")
    _require_references(ids, language_ids, "язык")
    if any(
        not isinstance(entry.get("progress_units"), int) or entry["progress_units"] < 0
        for entry in entries
    ):
        raise InvalidFoundation("Прогресс языка должен быть неотрицательным целым числом.")


def _require_references(values, available: set[str], label: str) -> None:
    missing = sorted(set(values) - available)
    if missing:
        raise InvalidFoundation(f"Не найдена ссылка на {label}: {', '.join(missing)}.")


def _validate_gameplay(draft: UniverseDraft) -> None:
    gameplay = draft.gameplay
    _require_id(gameplay.currency_id, "ID валюты")
    _require_text(gameplay.currency_name, "Название валюты")
    _require_text(gameplay.strength_name, "Название запаса сил")


def _validate_period(period: PeriodDraft, location_ids: set[str]) -> None:
    _require_id(period.id, "ID периода")
    for value, label in (
        (period.name, "Название периода"),
        (period.description, "Описание периода"),
        (period.lore, "Лор периода"),
        (period.initial_situation, "Начальная ситуация"),
    ):
        _require_text(value, label)
    if not period.location_ids:
        raise InvalidFoundation(f"В период «{period.name}» не добавлены локации.")
    _require_unique(period.location_ids, "Локации периода")
    _require_references(period.location_ids, location_ids, "локацию периода")
    if not period.starting_location_ids:
        raise InvalidFoundation(f"У периода «{period.name}» нет стартовой локации.")
    _require_unique(period.starting_location_ids, "Стартовые локации периода")
    selected = set(period.location_ids)
    _require_references(period.starting_location_ids, selected, "стартовую локацию периода")
    _require_unique(
        (connection.location_id for connection in period.location_connections),
        "Исходные локации переходов",
    )
    for connection in period.location_connections:
        _require_references((connection.location_id,), selected, "исходную локацию перехода")
        _require_unique(connection.connected_location_ids, "Переходы из одной локации")
        _require_references(
            connection.connected_location_ids,
            selected,
            "локацию перехода текущего периода",
        )
    if not MIN_STARTING_KIT_COUNT <= len(period.starting_kits) <= MAX_STARTING_KIT_COUNT:
        raise InvalidFoundation(
            "У каждого периода должно быть от одного до десяти стартовых наборов."
        )
    _require_unique((kit.id for kit in period.starting_kits), "ID стартовых наборов")
    for kit in period.starting_kits:
        _require_id(kit.id, "ID стартового набора")
        _require_text(kit.name, "Название стартового набора")
        _require_text(kit.description, "Описание стартового набора")
        if kit.starting_currency_amount < 0:
            raise InvalidFoundation("Стартовая валюта не может быть отрицательной.")
        if len(kit.items) > 10:
            raise InvalidFoundation("В стартовом наборе может быть не больше 10 предметов.")


def _require_id(value: str, label: str) -> None:
    if not ID_PATTERN.fullmatch(value.strip()):
        raise InvalidFoundation(f"{label}: используйте строчные латинские буквы, цифры и дефис.")


def _require_shared_id(value: str, label: str) -> None:
    normalized = value.strip()
    if (
        not normalized
        or normalized != normalized.lower()
        or normalized.startswith("-")
        or normalized.endswith("-")
        or "--" in normalized
        or any(not (character.isalnum() or character == "-") for character in normalized)
    ):
        raise InvalidFoundation(
            f"{label}: используйте строчные буквы, цифры и одиночный дефис."
        )


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise InvalidFoundation(f"Поле «{label}» не заполнено.")


def _require_unique(values: Iterable[str], label: str) -> None:
    entries = list(values)
    if len(entries) != len(set(entries)):
        raise InvalidFoundation(f"{label} не должны повторяться.")
