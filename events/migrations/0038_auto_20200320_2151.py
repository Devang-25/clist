# Generated by Django 2.2.10 on 2020-03-20 21:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0037_auto_20190908_2341'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='login',
            unique_together={('stage', 'username'), ('team', 'stage')},
        ),
    ]
