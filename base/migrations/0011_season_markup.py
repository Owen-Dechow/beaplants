# Generated by Django 5.0 on 2024-01-03 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_remove_season_base_markup_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='season',
            name='markup',
            field=models.JSONField(default={'0': 0.4}),
            preserve_default=False,
        ),
    ]
