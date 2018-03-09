# Generated by Django 2.0.2 on 2018-03-08 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20180306_2343'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='display_name',
        ),
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(default='', max_length=32, unique=True, verbose_name='displayed name'),
            preserve_default=False,
        ),
    ]
