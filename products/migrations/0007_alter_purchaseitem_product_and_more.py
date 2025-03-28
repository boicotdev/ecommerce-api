# Generated by Django 5.1.2 on 2025-03-29 02:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_discount_price_product_has_discount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseitem',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product'),
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='unit_measure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.unitofmeasure'),
        ),
    ]
