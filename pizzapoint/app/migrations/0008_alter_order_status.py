# Generated by Django 5.1.4 on 2025-01-03 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_orderitem_product_alter_orderitem_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('Completed', 'Completed'), ('Canceled', 'Canceled')], max_length=50),
        ),
    ]
