# Generated by Django 4.1 on 2022-09-03 01:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0004_game_round"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tournament",
            old_name="number_of_games",
            new_name="number_of_rounds",
        ),
    ]
