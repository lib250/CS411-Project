# Generated by Django 3.2.16 on 2022-12-08 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autho', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=100)),
                ('history', models.CharField(max_length=500)),
            ],
        ),
        migrations.DeleteModel(
            name='Player',
        ),
    ]