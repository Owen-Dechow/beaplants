# Generated by Django 5.0 on 2024-01-06 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0012_remove_season_active_alter_season_sales_date_start"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="open",
            field=models.BooleanField(default=True),
        ),
    ]
