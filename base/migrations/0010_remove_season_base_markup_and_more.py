# Generated by Django 5.0 on 2024-01-03 21:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_season_contacts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='season',
            name='base_markup',
        ),
        migrations.RemoveField(
            model_name='season',
            name='markup_reduction',
        ),
    ]
