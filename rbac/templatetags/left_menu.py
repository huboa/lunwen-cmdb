import re
from django.template import Library
from django.conf import settings
register = Library()
from django.shortcuts import render,HttpResponse,redirect

"""
{% menu request %}
"""
###数据转换例子
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



@register.inclusion_tag('menu.html')
def menu(request):
    current_url = request.path_info
    permission_menu_list = request.session.get(settings.PERMISSION_MENU_SESSION_KEY)
    # 获取session中菜单信息，自动生成二级菜单【默认选中，默认展开】
    # print("获取菜单列表",permission_menu_list)
    if not permission_menu_list:
        return {}
    per_dict = {}
    for item in permission_menu_list:
        if item['id'] == item['gmid']:
            per_dict[item['id']] = item

    for item in permission_menu_list:
        reg = settings.REX_FORMAT % (item['url'])
        if not re.match(reg, current_url):
            continue
        # 匹配成功
        # print(item,'=================')
        if item['id']:
            per_dict[item['gmid']]['active'] = True
        else:
            item['active'] = True


    menu_result = {}
    for item in per_dict.values():
        menu_id = item['menu_id']
        if menu_id in menu_result:
            temp = {'id': item['id'], 'title': item['app_name'], 'url': item['url'], 'active': item.get('active', False)}
            menu_result[menu_id]['children'].append(temp)
            if item.get('active', False):
                menu_result[menu_id]['active'] = item.get('active', False)
        else:
            menu_result[menu_id] = {
                'menu_id': menu_id,
                'menu__name': item['menu_name'],
                'active': item.get('active', False),
                'children': [
                    {'id': item['id'], 'title': item['app_name'], 'url': item['url'], 'active': item.get('active', False)}
                ]
            }

    # print(menu_result)
    return {'menu_result':menu_result}