# Generated by Django 5.0 on 2023-12-25 02:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('size', models.CharField(max_length=50)),
                ('sort', models.CharField(max_length=50)),
                ('search', models.TextField()),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.season')),
            ],
        ),
    ]
