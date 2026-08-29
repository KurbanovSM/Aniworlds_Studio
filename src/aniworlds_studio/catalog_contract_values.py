"""Single Studio source for enumerated values emitted to the game contract."""

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
    ("Жестовый язык", "sign_language"),
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
SHOP_OPTIONS = (("Обычный магазин", "general_store"), ("Кузница", "forge"))


def option_values(options: tuple[tuple[str, str], ...]) -> frozenset[str]:
    return frozenset(value for _, value in options)
