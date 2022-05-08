# Generated by Django 4.0.4 on 2022-04-17 02:33

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import phonenumber_field.modelfields
import registration.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('email', models.EmailField(error_messages={'unique': 'sorry this email is no longer available'}, max_length=70, unique=True, validators=[django.core.validators.EmailValidator(message='please enter a valid email')], verbose_name='email address')),
                ('first_name', models.CharField(max_length=30, validators=[django.core.validators.RegexValidator('^[a-zA-Z]+$', 'Must not contain numbers or special characters')], verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, validators=[django.core.validators.RegexValidator('^[a-zA-Z]+$', 'Must not contain numbers or special characters')], verbose_name='last name')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False, help_text='make this user a staff of this org')),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('account_confirm_status', models.BooleanField(default=False)),
                ('contact', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, verbose_name='Mobile Number')),
                ('date_confirmed', models.DateTimeField(blank=True, null=True)),
                ('avatar_hash', models.CharField(max_length=300, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', registration.models.UserManager()),
            ],
        ),
    ]
