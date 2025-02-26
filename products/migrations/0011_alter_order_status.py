# Generated by Django 5.1.2 on 2025-02-25 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_coupon_is_active_alter_payment_payment_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('PROCESSING', 'PROCESSING'), ('SHIPPED', 'SHIPPED'), ('OUT_FOR_DELIVERY', 'OUT_FOR_DELIVERY'), ('DELIVERED', 'DELIVERED'), ('CANCELLED', 'CANCELLED'), ('RETURNED', 'RETURNED'), ('FAILED', 'FAILED'), ('ON_HOLD', 'ON_HOLD')], default=('PENDING', 'PENDING'), max_length=20),
        ),
    ]
