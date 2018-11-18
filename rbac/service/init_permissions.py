from  rbac.models import UserInfo
from django.conf import settings
from django.shortcuts import render,HttpResponse
#####根据用户获取菜单和权限信息系
def init_permissions(user,request):

    #把权限列表转换成字典格式
    """
                   [
                       {'permissions__title': '用户列表', 'permissions__url': '/users/', 'permissions__code': 'list', 'permissions__group_id': 1}
                       {'permissions__title': '添加用户', 'permissions__url': '/users/add/', 'permissions__code': 'add', 'permissions__group_id': 1}
                       {'permissions__title': '删除用户', 'permissions__url': '/users/del/(\\d+)/', 'permissions__code': 'del', 'permissions__group_id': 1}
                       {'permissions__title': '修改用户', 'permissions__url': '/users/edit/(\\d+)/', 'permissions__code': 'edit', 'permissions__group_id': 1}
                       {'permissions__title': '主机列表', 'permissions__url': '/hosts/', 'permissions__code': 'list', 'permissions__group_id': 2}
                       {'permissions__title': '添加主机', 'permissions__url': '/hosts/add/', 'permissions__code': 'add', 'permissions__group_id': 2}
                       {'permissions__title': '删除主机', 'permissions__url': '/hosts/del/(\\d+)/', 'permissions__code': 'del', 'permissions__group_id': 2}
                       {'permissions__title': '修改主机', 'permissions__url': '/hosts/edit/(\\d+)/', 'permissions__code': 'edit', 'permissions__group_id': 2}
                   ]

                   {
                       1(权限组ID): {
                           urls: [/u sers/,/users/add/ ,/users/del/(\d+)/],
                           codes: [list,add,del]
                       },
                       2: {
                           urls: [/hosts/,/hosts/add/ ,/hosts/del/(\d+)/],
                           codes: [list,add,del]
                       }
                   }

   """
    print(user,'user----------')
    roles =UserInfo.objects.get(username=user).roles.all()
    # roles = user.roles.filter(permissions__id__isnull=False)
    permission_list = roles.values('permissions__id', ##权限id
                                   'permissions__title',  ##权限名称
                                   'permissions__url',  ##权限 url
                                   'permissions__code', ##权限码
                                   'permissions__group_id', ###权限组id
                                   'permissions__group__name',  ###应用名
                                   'permissions__gmid_id',  ###组内菜单
                                   'permissions__group__menu__id',##top menu id
                                   'permissions__group__menu__name', ##top menu name
                                   ).distinct()


    print(permission_list,"获取所有权限")
#####初始化登陆权限
    permission_dict = {}
    for permission in permission_list:
        gpid = permission["permissions__group_id"]
        url = permission["permissions__url"]
        code = permission["permissions__code"]
        if gpid in permission_dict:
            permission_dict[gpid]['urls'].append(url)
            permission_dict[gpid]['codes'].append(code)

        else:
            permission_dict[gpid] = {'urls': [], 'codes': []}
            permission_dict[gpid]['urls'].append(url)
            permission_dict[gpid]['codes'].append(code)
    print(permission_dict,"权限字典")
    request.session[settings.PERMISSION_DICT_SESSION_KEY] = permission_dict




###初始化菜单显示哪些菜单

    '''
    生成菜单数据
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
    '''
    permission_menu_list=[]
    for item in  permission_list:
        var={
            'id':item['permissions__id'],
            'title': item['permissions__title'],
            'url': item['permissions__url'],
            'gid': item['permissions__group_id'],
            'app_name': item['permissions__group__name'],
            'gmid': item['permissions__gmid_id'],
            'menu_id': item['permissions__group__menu__id'],
            'menu_name': item['permissions__group__menu__name']
        }

        permission_menu_list.append(var)
    print("菜单权限列表####",permission_menu_list,)
    request.session[settings.PERMISSION_MENU_SESSION_KEY] = permission_menu_list  ###将菜单信息放入session


    #用户名保存到session
    request.session["user_name"] = user.username
    # print(request.session.get("user_name"))
    # # 获取当前用户的session_key,并保存数据库用户表
    if not request.session.session_key:
        request.session.save()
    user.session_key = request.session.session_key
    user.status = 1
    user.save()


###注销用户
def reset_permission(user_obj,request,):
    """
    根据session_key，删除session中保存的信息，以此来设置修改权限后需要重新登录。
    :param session_key: 被修改权限的用户session_key
    :return:
    """
    print(user_obj.username,"注销用户")
    request.session.delete(user_obj.session_key)
    user_obj.session_key = None
    user_obj.status=2
    user_obj.save()

####用户在线状态
def user_state(request):
    session_dict = request.session.get(settings.PERMISSION_DICT_SESSION_KEY)
    if session_dict:
        return True
    else:
        return False
