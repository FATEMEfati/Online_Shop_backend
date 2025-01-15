# Generated by Django 5.1.3 on 2024-12-07 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0008_rename_delete_orderitem_is_delete_and_more'),
        ('User', '0005_alter_gift_cart_code_alter_user_email_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='comments',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='delete',
            new_name='is_delete',
        ),
        migrations.AddField(
            model_name='address',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='comments',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Gift_cart',
        ),
    ]
