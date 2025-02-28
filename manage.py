#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import django
from django.contrib.auth import get_user_model
from decouple import config

django.setup()
User = get_user_model()

SUPERUSER_EMAIL = config("SUPERUSER_EMAIL", default="admin@example.com")
SUPERUSER_PASSWORD = config("SUPERUSER_PASSWORD", default="admin123")

if not User.objects.filter(email=SUPERUSER_EMAIL).exists():
    User.objects.create_superuser(username="admin", email=SUPERUSER_EMAIL, password=SUPERUSER_PASSWORD)
    print("Superusuario creado exitosamente")
else:
    print("El superusuario ya existe")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
