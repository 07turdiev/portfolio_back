from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Madaniyat portfolio'

    def ready(self):
        # Cache invalidatsiya signallarini ulash
        from . import signals  # noqa: F401
