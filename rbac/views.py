from django.shortcuts import render
from django.shortcuts import render,HttpResponse,redirect
from django.shortcuts import redirect
from  rbac.models import UserInfo,Role
from django.conf import settings
from utils.md5 import  md5
import re

from rbac.forms import UserModelForm,RoleModelForm

from utils.pager import Pagination


####生成菜单
def left_menu(request):
    current_url = request.path_info
    # 获取session中菜单信息，自动生成二级菜单【默认选中，默认展开】
    permission_menu_list = request.session.get(settings.PERMISSION_MENU_SESSION_KEY)

    per_dict = {}
    for item in permission_menu_list:
        if item['id'] == item['gmid']:
            per_dict[item['id']] = item

    for item in permission_menu_list:
        reg = settings.REX_FORMAT % (item['url'])
        if not re.match(reg, current_url):
            continue
        # 匹配成功
        if item['id']:
            per_dict[item['gid']]['active'] = True
        else:
            item['active'] = True

    """
    获取数据
    [
        {'mid': 1, 'url': '/user/', 'menu_id': 1, 'pid': 1, 'menu_name': '菜单组', 'title': '用户列表'},
        {'mid': 1, 'url': '/user/add/', 'menu_id': 1, 'pid': 2, 'menu_name': '菜单组', 'title': '添加用户'},
        {'mid': 1, 'url': '/user/del/(\\d+)', 'menu_id': 1, 'pid': 3, 'menu_name': '菜单组', 'title': '删除用户'},
        {'mid': 1, 'url': '/user/edit/(d+)', 'menu_id': 1, 'pid': 4, 'menu_name': '菜单组', 'title': '编辑用户'},
        {'mid': 1, 'url': '/user/', 'menu_id': 1, 'pid': 1, 'menu_name': '菜单组', 'title': '用户列表'},
        {'mid': 1, 'url': '/user/add/', 'menu_id': 1, 'pid': 2, 'menu_name': '菜单组', 'title': '添加用户'},
        {'mid': 1, 'url': '/user/del/(\\d+)', 'menu_id': 1, 'pid': 3, 'menu_name': '菜单组', 'title': '删除用户'},
        {'mid': 1, 'url': '/user/edit/(d+)', 'menu_id': 1, 'pid': 4, 'menu_name': '菜单组', 'title': '编辑用户'}
    ]


    {
        1: {'id': 1, 'title': '用户列表', 'url': '/users/', 'pid': None, 'menu_id': 1, 'menu__name': '菜单1', 'active': True},
        5: {'id': 5, 'title': '主机列表', 'url': '/hosts/', 'pid': None, 'menu_id': 1, 'menu__name': '菜单1'}
        10: {'id': 10, 'title': 'xx列表', 'url': '/hosts/', 'pid': None, 'menu_id': 2, 'menu__name': '菜单2'}
    }

    {
        1:{
            'menu__name': '菜单1',
            'active': True,
            'children':[
                {'id': 1, 'title': '用户列表', 'url': '/users/','active': True}
                {'id': 5, 'title': '主机列表', 'url': '/users/'}
            ]
        },
        2:{
             'menu__name': '菜单1',
              'children':[
                {'id': 10, 'title': 'xx列表', 'url': '/hosts/'}
            ]

        }
    }
    """

    menu_result = {}
    for item in per_dict.values():
        menu_id = item['menu_id']

        print(menu_id,item['menu_id'])
        if menu_id in menu_result:
            temp = {'id': item['id'], 'title': item['title'], 'url': item['url'], 'active': item.get('active', False)}
            menu_result[menu_id]['children'].append(temp)
            if item.get('active', False):
                menu_result[menu_id]['active'] = item.get('active', False)
        else:
            menu_result[menu_id] = {
                'menu__name': item['menu_name'],
                'active': item.get('active', False),
                'children': [
                    {'id': item['id'], 'title': item['title'], 'url': item['url'], 'active': item.get('active', False)}
                ]
            }
    print(menu_result)
    return menu_result


def user(request):

    page_obj = Pagination(request,UserInfo)

    return render(request, 'user.html', {'user_list': page_obj.obj_list_html,'page_html': page_obj.page_html})


def add_user(request):
    if request.method == "GET":
        form = UserModelForm()
        # return render(request,"add_host.html",{'form':form})
        return render(request,"add_user.html", {'form': form})
    else:
        form = UserModelForm(request.POST)

        if form.is_valid():
            form.cleaned_data['password'] = md5(form.cleaned_data['password'])
            # print(form.cleaned_data)

            form.save()
            username=form.cleaned_data['username']
            pwd = md5(form.cleaned_data['password'])
            UserInfo.objects.filter(username=username).update(password=pwd)
            return redirect("/user/")
        return render(request, "add_user.html", {'form': form})

def edit_user(request,nid):
    obj = UserInfo.objects.filter(id=nid).first()
    if not obj:
        return HttpResponse('数据不存在')
    if request.method == "GET":
        form = UserModelForm(instance=obj)
        return  render(request,'edit_host.html',{"form":form})
    else:
        form = UserModelForm(data=request.POST, instance=obj)
        if form.is_valid():
            pwd = md5(form.cleaned_data['password'])

            form.save()
            print(form.cleaned_data)
            UserInfo.objects.filter(id=nid).update(password=pwd)
            return redirect('/user/')
        return render(request, 'edit_user.html', {'form': form})

def del_user(request,nid):
    obj = UserInfo.objects.filter(id=nid).first()
    if not obj:
        return HttpResponse('数据不存在')
    else:
        UserInfo.objects.filter(id=nid).delete()
        return redirect('/user/')

import re
from django.template import Library
from django.conf import settings
register = Library()


"""
{% menu request %}
"""





def role(request):
    all_count = Role.objects.all().order_by('-id').count()
    per_page_count = request.GET.get('items')
    if not per_page_count:
        per_page_count = 20
        # print("check per_page_count ", per_page_count)
    else:
        per_page_count = int(per_page_count)
        # print(per_page_count,type(per_page_count))

    page_obj = Pagination(all_count,per_page_count,request.GET.get('page'),request_url=request.path_info)
    role_list = Role.objects.all().order_by('-id')[page_obj.current_page_start_item:page_obj.current_page_end_item]

    return render(request, 'role.html', {'role_list': role_list, 'menu_result':left_menu(request),'page_html': page_obj.page_html})

def add_role(request):
    if request.method == "GET":
        add_role_form = RoleModelForm()
        return render(request,"add_role.html", {'add_role_form': add_role_form})
    else:
        add_role_form = RoleModelForm(request.POST)
        if add_role_form.is_valid():
            add_role_form.save()
            return redirect("/role/")
        return render(request, "add_role.html", {'add_role_form': add_role_form})

def edit_role(request,nid):
    obj = Role.objects.filter(id=nid).first()
    if not obj:
        return HttpResponse('数据不存在')
    if request.method == "GET":
        form = RoleModelForm(instance=obj)
        return  render(request,'edit_role.html',{"form":form})
    else:
        form = RoleModelForm(data=request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('/role/')
        return render(request, 'edit_role.html', {'form': form})

def del_role(request,nid):
    obj = Role.objects.filter(id=nid).first()
    if not obj:
        return HttpResponse('数据不存在')
    else:
        Role.objects.filter(id=nid).delete()
        return redirect('/user/')
