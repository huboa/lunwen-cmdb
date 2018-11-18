
from django.forms import Form
from django.forms import ModelForm
from django.forms import fields
from django.forms import widgets

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
        widgets = {
            'password': widgets.PasswordInput(attrs={'class':'form-control'}),
        }
class RoleModelForm(ModelForm):
    class Meta:
        model = models.Role
        fields = "__all__"
        labels = {
            'id':"ID",
            'title':'角色',
        },
        error_messages ={
            "title": {
                "required": "不能为空"
            },
        },






# class UserInfo(Form):
#     username = fields.CharField(
#         label='用户名',
#         required=True,
#         error_messages={
#             'required':'用户名不能为空'
#         },
#         widget=widgets.TextInput(attrs={'class':'form-control'})
#     )
#     password = fields.CharField(
#         label='密码',
#         required=True,
#         error_messages={
#             'required': '密码不能为空'
#         },
#         widget=widgets.PasswordInput(attrs={'class':'form-control'})
#     )