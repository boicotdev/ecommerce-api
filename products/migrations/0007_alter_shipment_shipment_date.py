# Generated by Django 5.1.2 on 2024-11-22 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_payment_shipment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='shipment_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
