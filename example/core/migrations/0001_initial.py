# Generated by Django 5.1.1 on 2024-10-15 13:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(default='')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.node')),
            ],
        ),
        migrations.CreateModel(
            name='Leaf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.node')),
            ],
        ),
    ]