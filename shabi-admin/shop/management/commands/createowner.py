import os, getpass
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
class Command(BaseCommand):
    help = "Create the single owner account (refuses if any user exists)."
    def handle(self, *a, **o):
        U = get_user_model()
        if U.objects.exists(): raise CommandError("An account already exists. Only one administrator is allowed.")
        name = os.environ.get("OWNER_USERNAME") or input("Owner username: ")
        pw = os.environ.get("OWNER_PASSWORD") or getpass.getpass("Password (min 12 chars): ")
        validate_password(pw)
        U.objects.create_superuser(name, password=pw); self.stdout.write("Owner created.")
