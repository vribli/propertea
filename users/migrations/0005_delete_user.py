# Generated by Django 3.0.4 on 2020-03-20 15:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
