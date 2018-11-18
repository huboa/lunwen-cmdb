import re
from django.conf import settings
from django.shortcuts import render,HttpResponse,redirect

###复制django 框架
class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

####自定义权限的类
class RbacMiddleware(MiddlewareMixin):

    def process_request(self,request):
        # 当前访问的URL
        current_url = request.path_info
        for valid in settings.VALID_LIST:
            if re.match(valid,current_url):
                return None

        permission_dict = request.session.get(settings.PERMISSION_DICT_SESSION_KEY)

        print(permission_dict)
        if not permission_dict:
            # return redirect('/login/')
            # return redirect('/index/')
            return HttpResponse('当前用户无权限目录信息')
            # return  HttpResponse('login.html')


        # 用户权限和当前URL进行匹配
        flag = False
        for item in permission_dict.values():
            urls = item['urls']
            codes = item['codes']
            for rex in urls:

                reg = settings.REX_FORMAT %(rex,)
                # print(reg,current_url,"#####",re.match(reg,current_url))
                if re.match(reg,current_url):
                    flag = True
                    request.permission_codes = codes
                    break
            if flag:
                break

        if not flag:
            return redirect('/index/')
            # return HttpResponse('无权限访问')
