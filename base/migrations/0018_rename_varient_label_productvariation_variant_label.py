# Generated by Django 5.0.9 on 2024-12-01 22:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_remove_productvariation_description_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productvariation',
            old_name='varient_label',
            new_name='variant_label',
        ),
    ]
