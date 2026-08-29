"""Labels for the compact basic-world form."""

UNIVERSE_FIELDS = (
    ("id", "ID вселенной"),
    ("name", "Название"),
    ("description", "Описание", "long_text"),
)

WORLD_RULE_FIELDS = (
    ("world_rules", "Правила мира", "long_text"),
    ("power_systems", "Системы сил", "long_text"),
)

ECONOMY_FIELDS = (
    ("currency_id", "ID валюты"),
    ("currency_name", "Название валюты"),
    ("currency_symbol", "Символ валюты"),
)

STRENGTH_FIELDS = (("strength_name", "Название запаса сил"),)
