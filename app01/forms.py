from django.forms import Form
from django.forms import ModelForm
from django.forms import fields
from django.forms import widgets

class LoginForm(Form):
    username = fields.CharField(
        label='用户名',
        required=True,
        error_messages={
            'required':'用户名不能为空'
        },
        widget=widgets.TextInput(attrs={'class':'form-control'})
    )
    password = fields.CharField(
        label='密码',
        required=True,
        error_messages={
            'required': '密码不能为空'
        },
        widget=widgets.PasswordInput(attrs={'class':'form-control'})
    )

from app01 import models
class HostModelForm(ModelForm):
    class Meta:
        model = models.Host
        fields = "__all__"
        labels = {
            "sn": "主机SN号",
            "remoteip": "带外管理IP",
            'hostname':'主机名',
            'ip':'主机IP',
            "user":"用户",
            'dp':'部门',
        }
        error_messages ={
            "idc": {
                "required": "不能为空"
            },
            "sn":{
                "required":"不能为空"
            },
            "remoteip": {
                "required": "不能为空"
            }
        }

from rbac import models
class UserModelForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = "__all__"
        labels = {
            'id':"ID",
            'usernanme':'用户',

        },
        error_messages ={
            "usernanme": {
                "required": "不能为空"
            },
        },



