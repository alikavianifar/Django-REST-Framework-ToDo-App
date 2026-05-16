import os
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from accounts.models import Profile
from todo.models import Task

User = get_user_model()


class Command(BaseCommand):
    help = "Inserts fake data into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of fake tasks to create (default: 10)",
        )

    def handle(self, *args, **kwargs):
        fake = Faker()
        count = kwargs["count"]

        if not User.objects.exists():
            password = os.environ.get("FAKE_USER_PASSWORD", "ChangeMe-FakeData-123!")
            user = User.objects.create_user(
                email=fake.email(),
                password=password,
                username=fake.user_name()[:20],
                is_verified=True,
            )
            user_profile = Profile.objects.get(user=user)
            self.stdout.write(
                self.style.WARNING(
                    f"Created demo user {user.email} (password from FAKE_USER_PASSWORD env)"
                )
            )
        else:
            user_profile = Profile.objects.first()

        for _ in range(count):
            Task.objects.create(
                author=user_profile,
                title=fake.sentence(nb_words=6),
                description=fake.text(),
                priority=random.choice(["high", "medium", "low"]),
                completed=random.choice([True, False]),
            )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully inserted {count} fake tasks")
        )
