# Generated by Django 3.1.4 on 2023-06-01 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_auto_20230530_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='export',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='export',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
