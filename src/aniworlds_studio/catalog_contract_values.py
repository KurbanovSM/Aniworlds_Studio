"""Single Studio source for enumerated values emitted to the game contract."""

# ruff: noqa: RUF001 - Russian user-facing labels are intentional.

CATEGORY_OPTIONS = (
    ("Расовая принадлежность", "race"),
    ("Животное", "animal"),
    ("Сверхъестественное существо", "supernatural"),
    ("Другой вид", "other"),
)
COGNITION_OPTIONS = (
    ("Инстинктивный", "instinctive"),
    ("Животный", "animal"),
    ("Разумный", "sapient"),
    ("Высший", "higher"),
)
COMMUNICATION_OPTIONS = (
    ("Сигналы", "signals"),
    ("Речь", "speech"),
    ("Жесты", "sign_language"),
    ("Письмо", "writing"),
    ("Телепатия", "telepathy"),
    ("Особый способ", "other"),
)
GROUP_TYPE_OPTIONS = (
    ("Фракция", "faction"),
    ("Клан", "clan"),
    ("Организация", "organization"),
    ("Гильдия", "guild"),
    ("Государство или поселение", "settlement"),
    ("Отряд", "team"),
    ("Дом", "house"),
    ("Армия", "army"),
    ("Другое", "other"),
)
ITEM_CATEGORY_OPTIONS = (
    ("Оружие", "weapon"),
    ("Броня", "armor"),
    ("Одежда", "clothing"),
    ("Расходуемое", "consumable"),
    ("Обычный предмет", "common"),
    ("Ключевой предмет", "key"),
    ("Артефакт", "artifact"),
)
EQUIPMENT_SLOT_OPTIONS = (
    ("Не экипируется", ""),
    ("Нижнее бельё", "underwear"),
    ("Голова", "head"),
    ("Торс", "torso"),
    ("Руки", "hands"),
    ("Ноги", "legs"),
    ("Ступни", "feet"),
    ("Активное оружие", "active_weapon"),
)
PROTECTION_OPTIONS = (
    ("Без защиты", "none"),
    ("Простая защита", "light"),
    ("Средняя защита", "medium"),
    ("Сильная защита", "heavy"),
)
SHOP_OPTIONS = (
    ("Универсальная лавка", "general_store"),
    ("Оружейная лавка", "weapon_shop"),
    ("Магазин брони", "armor_shop"),
    ("Магазин одежды", "clothing_shop"),
    ("Аптека", "pharmacy"),
    ("Лавка инструментов и свитков", "tool_and_scroll_shop"),
    ("Продовольственная лавка", "food_shop"),
    ("Кузница", "forge"),
)


def option_values(options: tuple[tuple[str, str], ...]) -> frozenset[str]:
    return frozenset(value for _, value in options)
