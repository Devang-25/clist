# Generated by Django 3.1.14 on 2022-07-31 16:20

from django.db import migrations, models
from django.contrib.contenttypes.models import ContentType
import django.db.models.deletion
from notification.models import Notification


def set_object_ids(apps, schema_editor):
    Task = apps.get_model('notification', 'Task')
    qs = Task.objects.all()
    for task in qs:
        task.notification_object_id = task.notification.pk
        task.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('notification', '0030_auto_20220703_2257'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='notification_content_type',
            field=models.ForeignKey(default=ContentType.objects.get_for_model(Notification).pk, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='task',
            name='notification_object_id',
            field=models.PositiveIntegerField(default=0),
        ),

        migrations.RunPython(set_object_ids),
    ]
