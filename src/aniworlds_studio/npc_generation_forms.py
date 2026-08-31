"""Cards reuse the catalog editor instead of exposing package JSON."""

from aniworlds_studio.catalog_form_specs import FieldSpec

NPC_FORM_SPECS = {
    "npc_name_sets": (
        FieldSpec("id", "ID набора"),
        FieldSpec("name", "Название"),
        FieldSpec("male_names", "Мужские имена · по одному на строке", "lines"),
        FieldSpec("female_names", "Женские имена · по одному на строке", "lines"),
        FieldSpec("surnames", "Фамилии · по одной на строке", "lines"),
    ),
    "npc_biographies": (
        FieldSpec("id", "ID биографии"),
        FieldSpec("name", "Название"),
        FieldSpec("text", "Биография · до 250 символов", "long_text"),
    ),
    "npc_generation_rules": (
        FieldSpec("id", "ID правила"),
        FieldSpec("name", "Название"),
        FieldSpec("role", "Роль", help_text="Пустая роль — обычный NPC этой локации."),
        FieldSpec("period_ids", "Периоды", "references", source="periods"),
        FieldSpec("location_ids", "Локации", "references", source="locations"),
        FieldSpec("creature_kind_id", "Вид", "reference", source="kinds"),
        FieldSpec(
            "weight",
            "Частота относительно других подходящих правил",
            "integer",
            minimum=1,
            maximum=100,
        ),
        FieldSpec("age_min", "Минимальный возраст", "integer", minimum=0, maximum=10000),
        FieldSpec("age_max", "Максимальный возраст", "integer", minimum=0, maximum=10000),
        FieldSpec(
            "sexes",
            "Возможный пол",
            "choices",
            (("Мужской", "male"), ("Женский", "female")),
        ),
        FieldSpec("name_set_id", "Имена и фамилии", "reference", source="npc_name_sets"),
        FieldSpec("biography_ids", "Подходящие биографии", "references", source="npc_biographies"),
        FieldSpec("trait_ids", "Возможные черты · выбирается одна", "references", source="traits"),
    ),
}
