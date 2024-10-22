# Generated by Django 5.1.2 on 2024-10-22 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('DELIVERED', 'DELIVERED'), ('CANCELLED', 'CANCELLED'), ('PENDING', 'PENDING')], max_length=12),
        ),
    ]