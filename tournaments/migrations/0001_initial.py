# Generated by Django 4.1 on 2022-08-29 03:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Game",
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
                ("datetime", models.DateTimeField(blank=True, null=True)),
                ("played", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="GameType",
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
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("BB", "Baseball"),
                            ("501", "501"),
                            ("Cricket", "Cricket"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "scoring",
                    models.CharField(
                        choices=[("Ranks", "Ranks"), ("Points", "Points and ranks")],
                        max_length=16,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tournament",
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
                ("name", models.CharField(max_length=255)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("Continual", "Going on, without any interruptions"),
                            ("Determined", "Fixed number of tables"),
                        ],
                        default="Continual",
                        max_length=16,
                    ),
                ),
                (
                    "matching",
                    models.CharField(
                        choices=[
                            ("all", "All participants play every games"),
                            ("pairs", "Head to head games"),
                        ],
                        default="all",
                        max_length=16,
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("active", models.BooleanField(default=True)),
                ("editable", models.BooleanField(default=True)),
                ("city", models.CharField(blank=True, max_length=120, null=True)),
                ("country", models.CharField(blank=True, max_length=120, null=True)),
                (
                    "darts",
                    models.ManyToManyField(related_name="darts", to="accounts.darts"),
                ),
                (
                    "gametype",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gametype",
                        to="tournaments.gametype",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Participant",
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
                ("score", models.IntegerField(blank=True, null=True)),
                ("rank", models.IntegerField(blank=True, null=True)),
                (
                    "darts",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="accounts.darts"
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tournaments.game"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="game",
            name="tournament",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="tournaments.tournament"
            ),
        ),
    ]
