# Generated by Django 4.2.7 on 2023-12-06 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommandLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('status', models.TextField(choices=[('pending', 'pending'), ('skipped', 'skipped'), ('finished', 'finished')], default='pending')),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
            ],
            options={
                'indexes': [models.Index(fields=['status', 'name'], name='django_comm_status_c6d84b_idx')],
            },
        ),
    ]
