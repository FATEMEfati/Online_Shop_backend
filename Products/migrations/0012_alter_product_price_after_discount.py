# Generated by Django 5.1.3 on 2025-01-10 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0011_product_is_discount_product_price_after_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price_after_discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
