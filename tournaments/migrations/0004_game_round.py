# Generated by Django 4.1 on 2022-09-02 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0003_remove_tournament_scheduling_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="round",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
