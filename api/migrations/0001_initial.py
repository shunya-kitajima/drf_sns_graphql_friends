# Generated by Django 4.1.5 on 2023-01-13 05:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "friend_requests",
                    models.ManyToManyField(
                        blank=True,
                        related_name="profiles_friend_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "friends",
                    models.ManyToManyField(
                        blank=True,
                        related_name="profiles_friends",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user_prof",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]