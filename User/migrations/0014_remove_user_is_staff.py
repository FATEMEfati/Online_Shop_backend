# Generated by Django 5.1.3 on 2024-12-19 07:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0013_rename_customuser_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
    ]
