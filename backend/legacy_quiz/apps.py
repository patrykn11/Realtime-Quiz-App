from django.apps import AppConfig


class LegacyQuizConfig(AppConfig):
    """Keeps the original migration history while models live in domain apps."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "legacy_quiz"
    label = "quiz"
    verbose_name = "Legacy quiz schema"
