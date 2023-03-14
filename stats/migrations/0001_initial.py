# Generated by Django 3.1.4 on 2022-08-03 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=45, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='Imports')),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImportSheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=45)),
                ('rows_count', models.FloatField(default=-1)),
                ('imported_rows_count', models.FloatField(default=-1)),
                ('import_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sheets', to='stats.importfile')),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Export',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=45, null=True)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('status', models.CharField(choices=[('Q', 'Queued'), ('E', 'Exporting...'), ('P', 'Preparing Download...'), ('F', 'Failed'), ('D', 'Click To Download')], default='Q', max_length=3)),
                ('rows_count', models.IntegerField(default=0, editable=False)),
                ('exported_rows_count', models.IntegerField(default=0, editable=False)),
                ('args', models.TextField(blank=True, max_length=1000, null=True)),
                ('type', models.CharField(choices=[('C', 'CSV'), ('P', 'PDF')], default='C', max_length=3)),
                ('file', models.FileField(blank=True, null=True, upload_to='Exports')),
                ('start_time', models.DateTimeField(blank=True, editable=False, null=True)),
                ('end_time', models.DateTimeField(blank=True, editable=False, null=True)),
                ('errors', models.TextField(blank=True, max_length=2000, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
    ]
