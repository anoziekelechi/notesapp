# Generated by Django 4.0.4 on 2022-04-29 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='note',
            options={'ordering': ['created']},
        ),
    ]
