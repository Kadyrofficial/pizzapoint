# Generated by Django 5.1.4 on 2025-01-03 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('Completed', 'Completed'), ('Canceled', 'Canceled')], default='Active', max_length=50),
        ),
    ]
