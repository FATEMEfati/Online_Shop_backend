# Generated by Django 5.1.3 on 2025-01-07 10:29

import User.validator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0020_remove_user_created_at_remove_user_deleted_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=300, validators=[User.validator.is_valid_password]),
        ),
    ]
