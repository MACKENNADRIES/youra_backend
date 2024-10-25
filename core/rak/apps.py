# rak/apps.py

from django.apps import AppConfig


class RakConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rak"

    def ready(self):
        import rak.signals  # Import signals to ensure they are registered
