# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-18 00:35


from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


def create_third_party_extension(apps, schema_editor):
    schema_editor.execute("CREATE EXTENSION ltree;")
    schema_editor.execute("CREATE EXTENSION pg_trgm;")


def drop_third_party_extension(apps, schema_editor):
    schema_editor.execute("DROP EXTENSION IF EXISTS ltree;")
    schema_editor.execute("DROP EXTENSION IF EXISTS pg_trgm;")


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunPython(create_third_party_extension, reverse_code=drop_third_party_extension, atomic=True),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('template', models.CharField(max_length=255)),
                ('data', jsonfield.fields.JSONField(blank=True, default={})),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('duration_in_secs', models.IntegerField(blank=True, editable=False)),
                ('url', models.CharField(max_length=255)),
                ('key', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=255)),
                ('uid', models.CharField(blank=True, max_length=100, null=True)),
                ('edit', models.CharField(blank=True, max_length=100, null=True)),
                ('invisible', models.BooleanField(default=False)),
                ('standings_url', models.CharField(blank=True, max_length=2048, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('host', models.CharField(max_length=255, unique=True)),
                ('enable', models.BooleanField()),
                ('url', models.CharField(max_length=255)),
                ('regexp', models.CharField(blank=True, max_length=1024, null=True)),
                ('path', models.CharField(blank=True, max_length=255, null=True)),
                ('timezone', models.CharField(blank=True, max_length=30, null=True)),
                ('color', models.CharField(blank=True, max_length=20, null=True)),
                ('uid', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimingContest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('notification', models.DateTimeField(auto_now_add=True)),
                ('statistic', models.DateTimeField(default=None, null=True)),
                ('contest', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='timing', to='clist.Contest')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='contest',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clist.Resource'),
        ),
        migrations.AlterUniqueTogether(
            name='contest',
            unique_together=set([('resource', 'key')]),
        ),
    ]
