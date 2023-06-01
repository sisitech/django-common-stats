# Generated by Django 3.1.4 on 2023-06-01 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0005_auto_20230601_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='export',
            name='page_size',
            field=models.IntegerField(choices=[(20, '20'), (50, '50'), (100, '100'), (300, '300'), (500, '500'), (800, '800'), (1000, '1000'), (10000, '10000')], default=20),
        ),
    ]