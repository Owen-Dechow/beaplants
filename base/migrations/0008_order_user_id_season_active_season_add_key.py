# Generated by Django 5.0 on 2024-01-02 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_product_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='user_id',
            field=models.CharField(default='98qhsadkjf23', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='season',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='season',
            name='add_key',
            field=models.CharField(default='Hello world', max_length=20),
            preserve_default=False,
        ),
    ]
