# Generated by Django 3.1.14 on 2022-01-09 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('true_coders', '0046_filter_party'),
    ]

    operations = [
        migrations.AddField(
            model_name='coder',
            name='is_virtual',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
