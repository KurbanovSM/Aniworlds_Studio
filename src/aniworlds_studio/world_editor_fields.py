"""Labels for the compact basic-world form."""

UNIVERSE_FIELDS = (
    ("id", "ID вселенной"),
    ("name", "Название"),
    ("description", "Описание", "long_text"),
    ("item_catalog_section_id", "ID основного каталога предметов"),
)

WORLD_RULE_FIELDS = (
    ("world_rules", "Правила мира", "long_text"),
    ("power_systems", "Системы сил", "long_text"),
)

ECONOMY_FIELDS = (
    ("currency_id", "ID валюты"),
    ("currency_name", "Название валюты"),
    ("currency_symbol", "Символ валюты"),
    ("npc_starting_currency_min", "Минимальная валюта нового NPC", "integer"),
    ("npc_starting_currency_max", "Максимальная валюта нового NPC", "integer"),
)

STRENGTH_FIELDS = (("strength_name", "Название запаса сил"),)
