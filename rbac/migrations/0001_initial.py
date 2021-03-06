# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-11-17 07:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DepartMent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Ldap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='PermissionGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='默认', max_length=32, verbose_name='db_table')),
                ('model_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='model注册名')),
                ('menu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.Menu', verbose_name='一级菜单')),
            ],
        ),
        migrations.CreateModel(
            name='Permissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='权限名称')),
                ('url', models.CharField(max_length=255, verbose_name='含正则url')),
                ('code', models.CharField(max_length=32, verbose_name='权限代码')),
                ('gmid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xxx', to='rbac.Permissions', verbose_name='组内菜单')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbac.PermissionGroup', verbose_name='表')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, unique=True, verbose_name='角色名称')),
                ('permissions', models.ManyToManyField(max_length=32, to='rbac.Permissions', verbose_name='权限')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, unique=True, verbose_name='用户名')),
                ('password', models.CharField(max_length=64, verbose_name='密码')),
                ('gender', models.IntegerField(choices=[(1, '男'), (2, '女'), (3, '中')], default=1, verbose_name='性别')),
                ('status', models.IntegerField(choices=[(1, '在线'), (2, '离线')], default=1, verbose_name='状态')),
                ('session_key', models.CharField(blank=True, max_length=40, null=True, verbose_name='当前登录用户的session_key')),
                ('dp', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='rbac.DepartMent')),
                ('roles', models.ManyToManyField(to='rbac.Role', verbose_name='角色名')),
            ],
        ),
    ]
