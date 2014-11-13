# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20141023_0408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datapoint',
            name='up_good',
        ),
        migrations.AddField(
            model_name='datapoint',
            name='featured',
            field=models.BooleanField(verbose_name='featured set?', default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='datapoint',
            name='trend_upwards_positive',
            field=models.BooleanField(verbose_name='upward trend positive?', default=False),
            preserve_default=True,
        ),
    ]
