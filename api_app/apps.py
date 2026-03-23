from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings
from django.db import OperationalError, ProgrammingError
from django.contrib.auth import get_user_model


def create_default_superuser(sender, **kwargs):
    User = get_user_model()

    # Load defaults from settings / env
    first_name = getattr(settings, "DEFAULT_SUPERADMIN_FIRSTNAME", "Super")
    last_name = getattr(settings, "DEFAULT_SUPERADMIN_LASTNAME", "Admin")
    phone_number = getattr(settings, "DEFAULT_SUPERADMIN_PHONE", "0000000000")
    username = getattr(settings, "DEFAULT_SUPERADMIN_USERNAME", "superadmin")
    email = getattr(settings, "DEFAULT_SUPERADMIN_EMAIL", "admin@example.com")
    password = getattr(settings, "DEFAULT_SUPERADMIN_PASSWORD", "admin12345")

    try:
        # Create ONLY if no superuser exists
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                is_user=True,
                is_staff=True,
                is_superuser=True,
            )
            print("✅ Default Super Admin created")
    except (OperationalError, ProgrammingError):
        pass


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api_app"

    def ready(self):
        post_migrate.connect(create_default_superuser, sender=self)
