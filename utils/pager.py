import  copy
from django.utils.safestring import mark_safe

"""
应用举例子
from utils.pager import Pagination ##导入模块


  page_obj=Pagination(request,self.result_list)  ###实例化对象(总数)
        self.page_list= page_obj.page_obj_list()  ####  获取每页数据
        self.page_html=mark_safe(page_obj.page_html())   ###获取页码导航

"""


class Pagination(object):
    def __init__(self,request,result_list):
        """
        obj-表名
        :param request:
        :param obj:
        """
        ###初始化页码变量
        self.result_list=result_list
        self.item_total_count = result_list.count()  ####总数

        ###请求参数
        self.params = copy.deepcopy(request.GET)
        self.params._mutable =True

        per_page_item_count = request.GET.get('items')  ###每页显示条数
        request_current_page = request.GET.get('page')  ###当前页码
        per_group_page_count = 10     ###显示10个页码

        if not per_page_item_count:  ##每页默认显示数据条数
            per_page_item_count = 20
        else:
            per_page_item_count = int(per_page_item_count)
        self.per_page_item_count = per_page_item_count
        self.request_url=request.path_info   ###请求路径

        ####每页显示项目计算
        page_total_count,item_remainder = divmod(self.item_total_count, per_page_item_count)
        print("check item 总数",self.item_total_count,"每页码显示item 个数",per_page_item_count)
        print("check page 总页数" ,page_total_count,"item 余数",item_remainder)
        if  item_remainder:
            page_total_count += 1
        self.page_total_count = page_total_count   ####总页数
        try:
            request_current_page = int(request_current_page)
        except Exception as e:
            request_current_page = 1
        if request_current_page > page_total_count:
            request_current_page = page_total_count
        if request_current_page < 1:
            request_current_page = 1

        self.request_current_page = request_current_page   ##请求页码


        ###初始化页码组
        all_page_group_count, page_remainder = divmod(page_total_count,per_group_page_count)
        # print("check group 总组数",all_page_group_count,"每组页数",per_group_page_count,"最后一组页数",page_remainder)
        if  page_remainder:
            all_page_group_count += 1

        self.all_page_group_count = all_page_group_count   #页码组数
        self.per_group_page_count = per_group_page_count   #每组页码数
        self.current_page_group_id = int((request_current_page - 1) // per_group_page_count + 1)  ##页码组id
        self.current_page_group_start = (self.current_page_group_id - 1) * per_group_page_count + 1  ##页码组开始页

        ##页码组开结束页
        if  self.current_page_group_id >= all_page_group_count:
            self.current_page_group_end = page_total_count
        else:
            self.current_page_group_end = self.current_page_group_start + per_group_page_count - 1

        print("页码总组数", self.all_page_group_count, "当前页码组id", self.current_page_group_id, "开始页", self.current_page_group_start, "组结束页",self.current_page_group_end, )

    ##当前页码项目分片1
    @property
    def current_page_start_item(self):
        return (self.request_current_page - 1) * self.per_page_item_count

    ##当前页码项目分片2
    @property
    def current_page_end_item(self):

        if self.request_current_page >= self.page_total_count:
            req = self.item_total_count
        else:
            req = (self.request_current_page) * self.per_page_item_count
        # print("check current", req)
        return req


### 生成html 返回
    def page_html(self):
        page_html = ''
        for i in range(self.current_page_group_start,  self.current_page_group_end + 1):
            if i == self.request_current_page:
                temp = '<a class="active" href="%s?page=%s&items=%s">%s</a>' % (self.request_url,i,self.per_page_item_count, i)
            else:
                temp = '<a href=%s?page=%s&items=%s>%s</a>' % (self.request_url,i,self.per_page_item_count ,i,)
            page_html += temp


            ###单页
        if self.request_current_page > 1:
            pre_page = self.request_current_page - 1
            pre_page_html = '<a href=%s?page=%s&items=%s><</a>' % (self.request_url,pre_page,self.per_page_item_count)
        else:
            pre_page = self.request_current_page
            pre_page_html = '<a href=%s?page=%s&items=%s><</a>' % (self.request_url,pre_page,self.per_page_item_count,)
            # pre_page_html = ""
        if self.request_current_page <  self.page_total_count :
            next_page = self.request_current_page + 1
            next_page_html = '<a href=%s?page=%s&items=%s>></a>' % (self.request_url,next_page,self.per_page_item_count,)
        else:
            next_page = self.request_current_page
            next_page_html = '<a href=%s?page=%s&items=%s>></a>'  % (self.request_url,next_page,self.per_page_item_count,)
            # next_page_html = ""

            ####页码组

        if self.current_page_group_id > 1:
            pre_group_page_id = self.request_current_page - self.per_group_page_count
            pre_page_group_html = '<a href=%s?page=%s&items=%s><<</a>' % (self.request_url,pre_group_page_id,self.per_page_item_count,)

        else:
            # pre_page_group_html = ""
            pre_group_page_id = self.request_current_page
            pre_page_group_html = '<a href=%s?page=%s&items=%s><<</a>' % (self.request_url,pre_group_page_id,self.per_page_item_count,)

        if self.current_page_group_id >= self.all_page_group_count:
            next_group_page_id =  self.request_current_page
            next_page_group_html = '<a href=%s?page=%s&items=%s>>></a>' %  (self.request_url,next_group_page_id,self.per_page_item_count,)
            # next_page_group_html = ""
        else:
            next_group_page_id =  self.request_current_page  + self.per_group_page_count
            next_page_group_html = '<a href=%s?page=%s&items=%s>>></a>' % (self.request_url,next_group_page_id,self.per_page_item_count,)

            ##首页尾页
        one_page_html = '<a href=%s?page=%s&items=%s>首页</a>' % (self.request_url,1,self.per_page_item_count,)
        end_page_html = '<a href=%s?page=%s&items=%s>末页</a>' % (self.request_url,self.page_total_count,self.per_page_item_count,)
        ###共 多少页
        all_page_html = '共%s行 %s行/页 变更<select name="items"> <option value="20"></option><option value="5">5</option><option value="10">10</option> <option value="20">20</option> <option value="50">50</option> <option value="100">100</option></select>  共%s页' % (self.item_total_count,self.per_page_item_count,self.page_total_count )
        # select_page_html='<form action="">page: <input type="text" name="page"><input type="submit" value="提交"></form>'
        select_page_html = '  到  <input type="text" name="page"  size="1" > 页  <input type="submit" value="确定"></form>'
        page_html = "<form >" + one_page_html + pre_page_group_html + pre_page_html + page_html + next_page_html + next_page_group_html + end_page_html + all_page_html + select_page_html
        return  page_html
###bootstrap_page_html ##bootstrap_page 导航条
    def bootstrap_page_html(self):
        page_html = ''
        for i in range(self.current_page_group_start, self.current_page_group_end + 1):
            if i == self.request_current_page:
                self.params["page"] = i
                temp = '<li class="active"> <a href="%s?%s">%s</a></li>' % (self.request_url,self.params.urlencode(), i)
            else:
                self.params["page"] = i
                temp = '<li><a href=%s?%s>%s</a></li>' % (self.request_url,self.params.urlencode(), i,)
            page_html += temp


            ###前一页
        if self.request_current_page > 1:
            self.params["page"] = self.request_current_page - 1
            pre_page_html = '<li><a href=%s?%s><</a></li>' % (self.request_url,self.params.urlencode(),)
        else:
            self.params["page"] = self.request_current_page
            pre_page_html = '<li><a href=%s?%s><</a></li>' % (self.request_url,self.params.urlencode(),)
            # pre_page_html = ""
        if self.request_current_page < self.page_total_count:
            self.params["page"] = self.request_current_page + 1
            next_page_html = '<li><a href=%s?%s>></a></li>' % (self.request_url,self.params.urlencode())
        else:
            self.params["page"] = self.request_current_page
            next_page_html = '<li><a href=%s?%s>></a></li>' % (self.request_url,self.params.urlencode())
            # next_page_html = ""

            ####翻组前一页码组或后一页码组
        if  self.current_page_group_id > 1:
            self.params["page"] = self.request_current_page - self.per_group_page_count
            pre_page_group_html = '<li><a href=%s?%s><<</a></li>' % (self.request_url, self.params.urlencode())
        else:
            self.params["page"] = self.request_current_page
            pre_page_group_html = '<li><a href=%s?%s><<</a></li>' % (self.request_url, self.params.urlencode())

        if self.current_page_group_id >= self.all_page_group_count:
            self.params["page"] = self.request_current_page
            next_page_group_html = '<li><a href=%s?%s>>></a></li>' % (self.request_url, self.params.urlencode())
        else:
            self.params["page"] = self.request_current_page + self.per_group_page_count
            next_page_group_html = '<li><a href=%s?%s>>></a></li>' % (self.request_url, self.params.urlencode())

            ##首页尾页

        self.params["page"] = 1
        one_page_html = '<li><a href=%s?%s>首页</a></li>' % (self.request_url,self.params.urlencode())
        self.params["page"] = self.page_total_count
        end_page_html = '<li><a href=%s?%s>末页</a></li>' % (self.request_url,self.params.urlencode())
        ###共 多少页
        all_page = '<li><a>总数%s 每页%s 共%s页  </a></li>' % ( self.item_total_count,self.per_page_item_count,self.page_total_count, )
        # go_page = '<li><input type = "text" size="1" name="page" border: none placeholder="" value=""></li>'

        # item_per_page = '<li><a > <select  name="items"> <option value="20"></option><option value="10">10</option><option value="50">50</option><option value="100">100</option></select><a></li>'
        page_html =  one_page_html + pre_page_group_html + pre_page_html + page_html + next_page_html + next_page_group_html + end_page_html +  all_page

        return page_html

####list要显示每页内容
    def page_obj_list(self):
        obj_list = self.result_list.order_by('-id')[self.current_page_start_item:self.current_page_end_item]
        return obj_list