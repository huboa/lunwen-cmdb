
from django.shortcuts import render,HttpResponse,redirect
from rbac.service.init_permissions import user_state
from django.template import Library
register = Library()

####根据用户登录状态生成 登录或退出url
@register.inclusion_tag('head_layout.html')
def head_layout(request):
    request_host = (request.get_host())
    # request_host = "127.0.0.1:8000"
    home_url= "http://" + str(request_host)+"/index/"
    if  user_state(request):
        print("已经登陆",user_state(request))
        head_url = "http://" + str(request_host)+"/logout/"
        url_name = "logout"
    else:
        print("没有登录",user_state(request))
        head_url = "http://" + str(request_host)+"/login/"
        url_name = "login"
    return {"log_url": head_url,"url_name":url_name,"home_url":home_url}