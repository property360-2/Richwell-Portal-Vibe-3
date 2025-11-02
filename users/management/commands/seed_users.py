from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = "Seed sample users for each role (Dean, Registrar, Admission, Professor, Student)."

    def handle(self, *args, **options):
        roles = ["DEAN", "REGISTRAR", "ADMISSION", "PROFESSOR", "STUDENT"]
        default_password = "1234"

        for role in roles:
            username = role.lower()
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password=default_password,
                    role=role,
                    first_name=role.capitalize(),
                )
                self.stdout.write(self.style.SUCCESS(f"Created {role} user"))
            else:
                self.stdout.write(self.style.WARNING(f"{role} already exists"))

        self.stdout.write(self.style.SUCCESS(f"\nAll users ready! Default password: {default_password}\n"))
