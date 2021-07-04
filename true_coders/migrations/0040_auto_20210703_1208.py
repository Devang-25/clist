# Generated by Django 3.1.12 on 2021-07-03 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('true_coders', '0039_listvalue'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='listvalue',
            constraint=models.UniqueConstraint(condition=models.Q(coder__isnull=False), fields=('coder_list', 'coder'), name='unique_coder'),
        ),
        migrations.AddConstraint(
            model_name='listvalue',
            constraint=models.UniqueConstraint(condition=models.Q(account__isnull=False), fields=('coder_list', 'account', 'group_id'), name='unique_account'),
        ),
    ]
