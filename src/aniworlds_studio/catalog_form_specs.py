"""Declarative fields for user-facing catalog cards and forms."""

# ruff: noqa: RUF001

from dataclasses import dataclass

from aniworlds_studio.catalog_contract_values import (
    CATEGORY_OPTIONS,
    COGNITION_OPTIONS,
    COMMUNICATION_OPTIONS,
    GROUP_TYPE_OPTIONS,
    ITEM_CATEGORY_OPTIONS,
    SHOP_OPTIONS,
)


@dataclass(frozen=True, slots=True)
class FieldSpec:
    key: str
    label: str
    kind: str = "text"
    options: tuple[tuple[str, str], ...] = ()
    source: str = ""
    help_text: str = ""
    nested: tuple["FieldSpec", ...] = ()
    minimum: int | None = None
    maximum: int | None = None


LOCATION_FIELDS = (
    FieldSpec("id", "ID локации"),
    FieldSpec("name", "Название"),
    FieldSpec("description", "Описание", "long_text"),
    FieldSpec(
        "price_coefficient",
        "Коэффициент цен",
        "decimal",
        help_text=(
            "Входит в пакет мира версии 4 и сохраняется сервером у локации. "
            "Применение коэффициента при покупке принадлежит игровой механике."
        ),
        minimum=0,
    ),
    FieldSpec("map_x", "Карта: X (0–1000)", "optional_integer", minimum=0, maximum=1000),
    FieldSpec("map_y", "Карта: Y (0–1000)", "optional_integer", minimum=0, maximum=1000),
)
KIT_ITEM_FIELDS = (
    FieldSpec("item_id", "Предмет", "reference", source="items"),
    FieldSpec("quantity", "Количество", "integer", minimum=1),
)
KIT_FIELDS = (
    FieldSpec("id", "ID набора"),
    FieldSpec("name", "Название"),
    FieldSpec("description", "Описание", "long_text"),
    FieldSpec("starting_currency_amount", "Стартовая валюта", "integer", minimum=0),
    FieldSpec("items", "Предметы набора", "nested", nested=KIT_ITEM_FIELDS, maximum=10),
)
ABILITY_FIELDS = (
    FieldSpec("id", "ID способности"),
    FieldSpec("name", "Название · до 30 символов"),
    FieldSpec("short_description", "Краткое описание · до 50 символов"),
    FieldSpec("description", "Полное описание", "long_text"),
    FieldSpec(
        "kind",
        "Тип способности",
        "choice",
        (("Обычная", "ordinary"), ("Поддерживаемая", "sustained")),
    ),
)

CATALOG_FORM_SPECS: dict[str, tuple[FieldSpec, ...]] = {
    "periods": (
        FieldSpec("id", "ID периода"),
        FieldSpec("name", "Название"),
        FieldSpec("description", "Краткое описание", "long_text"),
        FieldSpec("lore", "Лор периода", "long_text"),
        FieldSpec("initial_situation", "Начальная ситуация", "long_text"),
    ),
    "locations": LOCATION_FIELDS,
    "groups": (
        FieldSpec("id", "ID объединения"),
        FieldSpec("name", "Название"),
        FieldSpec("group_type", "Тип", "choice", GROUP_TYPE_OPTIONS),
        FieldSpec("description", "Описание", "long_text"),
        FieldSpec("location_ids", "Связанные локации", "references", source="locations"),
        FieldSpec("ally_ids", "Союзники", "references", source="groups"),
        FieldSpec("enemy_ids", "Противники", "references", source="groups"),
        FieldSpec("period_states", "Состояние по периодам", "states", source="periods"),
    ),
    "creature_kinds": (
        FieldSpec("id", "ID вида или расы"),
        FieldSpec("name", "Название"),
        FieldSpec("description", "Описание", "long_text"),
        FieldSpec("category", "Категория", "choice", CATEGORY_OPTIONS),
        FieldSpec("cognition", "Базовый уровень мышления", "choice", COGNITION_OPTIONS),
        FieldSpec("communication_modes", "Способы общения", "choices", COMMUNICATION_OPTIONS),
        FieldSpec(
            "default_languages",
            "Начальные языки этого вида или расы",
            "language_units",
        ),
        FieldSpec("physical_features", "Физические особенности · по одной на строке", "lines"),
        FieldSpec("habitat_location_ids", "Места обитания", "references", source="locations"),
        FieldSpec("period_ids", "Доступность по периодам", "references", source="periods"),
        FieldSpec("parent_kind_id", "Родительский вид", "reference_optional", source="kinds"),
    ),
    "languages": (
        FieldSpec("id", "Стабильный ID языка"),
        FieldSpec("name", "Название"),
        FieldSpec("has_spoken_form", "Есть устная форма", "boolean"),
        FieldSpec("has_written_form", "Есть письменная форма", "boolean"),
    ),
    "items": (
        FieldSpec("id", "ID предмета"),
        FieldSpec("name", "Название"),
        FieldSpec("description", "Описание", "long_text"),
        FieldSpec("category", "Категория", "choice", ITEM_CATEGORY_OPTIONS),
        FieldSpec(
            "uniqueness",
            "Редкость",
            "choice",
            (("Обычный", "ordinary"), ("Уникальный", "unique")),
        ),
        FieldSpec("properties", "Свойства · по одному на строке", "lines"),
        FieldSpec("limitations", "Ограничения · по одному на строке", "lines"),
        FieldSpec("allowed_shop_kinds", "Где продаётся", "choices", SHOP_OPTIONS),
        FieldSpec("base_price", "Базовая цена", "integer", minimum=0),
        FieldSpec(
            "appearance_weight",
            "Частота случайного появления",
            "integer",
            help_text="От 1 до 100: 1 — очень редко, 100 — максимально часто.",
            minimum=1,
            maximum=100,
        ),
        FieldSpec(
            "maximum_created_instances",
            "Количество экземпляров в одном мире",
            "instance_limit",
            help_text=(
                "Выберите «Без ограничений» либо укажите точное максимальное количество. "
                "Пустое значение не используется."
            ),
            minimum=1,
        ),
    ),
    "shop_policies": (
        FieldSpec("shop_kind", "Вид торгового места", "choice", SHOP_OPTIONS),
        FieldSpec("minimum_assortment_size", "Минимум товаров", "integer", minimum=1),
        FieldSpec("maximum_assortment_size", "Максимум товаров", "integer", minimum=1),
    ),
    "characters": (
        FieldSpec("id", "ID персонажа"),
        FieldSpec("name", "Имя"),
        FieldSpec("sex", "Пол", "choice", (("Мужской", "male"), ("Женский", "female"))),
        FieldSpec("age", "Возраст", "integer", minimum=18),
        FieldSpec("biography", "Биография", "long_text"),
        FieldSpec("origin_location_id", "Исходная локация", "reference", source="locations"),
        FieldSpec("creature_kind_id", "Вид или раса", "reference", source="kinds"),
        FieldSpec(
            "cognition_override",
            "Исключение мышления",
            "choice_optional",
            COGNITION_OPTIONS,
        ),
        FieldSpec("trait_ids", "Черты характера", "references", source="traits"),
        FieldSpec("abilities", "Способности", "nested", nested=ABILITY_FIELDS, maximum=8),
        FieldSpec("group_ids", "Состоит в объединениях", "references", source="groups"),
        FieldSpec("leader_group_ids", "Возглавляет объединения", "references", source="groups"),
        FieldSpec("period_ids", "Доступен в периодах", "references", source="periods"),
        FieldSpec("language_knowledge", "Знание языков", "language_units"),
    ),
}

GLOBAL_CATALOG_FORM_SPECS: dict[str, tuple[FieldSpec, ...]] = {
    "creature_kinds": (
        FieldSpec("id", "ID вида или расы"),
        FieldSpec("name", "Название"),
        FieldSpec("description", "Описание", "long_text"),
        FieldSpec("category", "Категория", "choice", CATEGORY_OPTIONS),
        FieldSpec("cognition", "Базовый уровень мышления", "choice", COGNITION_OPTIONS),
        FieldSpec("communication_modes", "Способы общения", "choices", COMMUNICATION_OPTIONS),
        FieldSpec("physical_features", "Физические особенности · по одной на строке", "lines"),
        FieldSpec("parent_kind_id", "Родительский вид", "reference_optional", source="kinds"),
    ),
    "languages": CATALOG_FORM_SPECS["languages"],
    "groups": CATALOG_FORM_SPECS["groups"][:4],
    "traits": (
        FieldSpec("id", "ID черты"),
        FieldSpec("name", "Название · до 30 символов"),
        FieldSpec("description", "Описание проявления · до 200 символов", "long_text"),
        FieldSpec(
            "incompatible_trait_ids",
            "Несовместимые черты",
            "references",
            source="traits",
            help_text="Связь должна быть указана у обеих несовместимых черт.",
        ),
    ),
}

WORLD_KIND_FIELDS = (
    CATALOG_FORM_SPECS["creature_kinds"][6],
    CATALOG_FORM_SPECS["creature_kinds"][8],
    CATALOG_FORM_SPECS["creature_kinds"][9],
)
WORLD_GROUP_FIELDS = CATALOG_FORM_SPECS["groups"][4:]
