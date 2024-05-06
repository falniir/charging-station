from django.apps import AppConfig


class ChargingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.charging"

    def ready(self):
        from app.charging.mqtt import client
        client.loop_start()
