# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-11-17 07:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sn', models.CharField(max_length=32, verbose_name='sn号')),
                ('remoteip', models.GenericIPAddressField(default='0.0.0.0', verbose_name='带外ip')),
                ('hostname', models.CharField(default='', max_length=32, verbose_name='主机名')),
                ('host_ip', models.CharField(default='0.0.0.0', max_length=32, verbose_name='主机ip')),
                ('manufacturer', models.CharField(default='', max_length=32, verbose_name='品牌')),
                ('product_name', models.CharField(default='', max_length=32, verbose_name='型号')),
                ('Hosys', models.CharField(max_length=32, null=True, verbose_name='操作系统')),
                ('Hcore', models.CharField(max_length=32, null=True, verbose_name='内核架构')),
                ('Hcpu', models.CharField(default='', max_length=64, verbose_name='cpu')),
                ('Hmemory', models.CharField(default='', max_length=32, verbose_name='内存')),
                ('Hdisk', models.CharField(default='', max_length=64, verbose_name='磁盘')),
                ('HotherIp', models.CharField(default='', max_length=128, verbose_name='其它ip')),
                ('Hother', models.CharField(default='', max_length=128, verbose_name='备注')),
            ],
        ),
        migrations.CreateModel(
            name='IDC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Iname', models.CharField(max_length=32, unique=True, verbose_name='机房名称')),
                ('Icity', models.CharField(max_length=32, verbose_name='城市')),
                ('Iaddr', models.CharField(max_length=32, verbose_name='地址')),
                ('Itel', models.CharField(max_length=32, verbose_name='电话')),
                ('Icontact', models.CharField(max_length=32, verbose_name='联系人')),
            ],
        ),
        migrations.AddField(
            model_name='host',
            name='idc',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app01.IDC', verbose_name='机房'),
        ),
    ]
