# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100, verbose_name='category')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100, verbose_name='data point')),
                ('resource', models.URLField()),
                ('date_field', models.CharField(max_length=100, verbose_name='date field')),
                ('data_field', models.CharField(max_length=100, verbose_name='data field')),
                ('up_good', models.BooleanField(default=False)),
                ('category', models.ForeignKey(verbose_name='category', to='dashboard.Category')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
