# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-06 10:29
from __future__ import unicode_literals

from django.db import migrations


def add_semicolons(apps, schema_editor):
    Certificate = apps.get_model('django_ca', 'Certificate')
    for cert in Certificate.objects.all():
        if ':' not in cert.serial:
            cert.serial = ':'.join(a+b for a,b in zip(cert.serial[::2], cert.serial[1::2]))
            cert.save()


class Migration(migrations.Migration):

    dependencies = [
        ('django_ca', '0002_auto_20160106_1028'),
    ]

    operations = [
        migrations.RunPython(add_semicolons),
    ]
