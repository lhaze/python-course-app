# Generated by Django 2.0.2 on 2018-03-06 23:43

import django.core.validators
from django.db import migrations, models
import pca.users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='display_name',
            field=models.CharField(default='', max_length=32, unique=True, validators=[pca.users.validators.NameBlacklistValidator()], verbose_name='display name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, validators=[django.core.validators.EmailValidator(), pca.users.validators.EmailDomainBlacklistValidator()], verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
    ]
